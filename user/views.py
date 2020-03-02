from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, ItemForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib import messages
from .models import *


def search(request):
    search =request.GET.get('search')
    if request.user.is_authenticated:
        result = Item.objects.exclude(User_id = request.user.id).filter(bidding = True).filter(title__contains=search)
    else:
        result = Item.objects.filter(bidding = True).filter(title__contains=search)
    return render(request,'home.html',{"items":result})

def home(request):
    if request.user.is_authenticated:
        items = Item.objects.exclude(User_id = request.user.id).filter(bidding = True)
    else:
        items = Item.objects.filter(bidding = True)
    return render(request, 'home.html', {"items":items})    #all the items that has bidding enabled

def logout2(request):
    logout(request)
    items = Item.objects.filter(bidding = True)
    return render(request, 'home.html', {"items":items})


def makeBid(request):
    if request.POST.get("user_id") != "0":      #checking if user is authenticated
        bid = request.POST.get("bid")
        item_id = request.POST.get("item_id")
        try:
            itemstatus = ItemStatus.objects.get(item_id = item_id)  #checking if there is any previous bids
        except ItemStatus.DoesNotExist:
            newItem = ItemStatus(bid=bid, item_id=item_id, user_id=request.POST.get("user_id"),sold=False)
            newItem.save()
        else:
            itemstatus.bid = bid                #updating bid for item
            itemstatus.save()
        return HttpResponse("Your Bid is Successfully Placed!")
    else:
        return HttpResponse(status=500)

def stopBid(request):
    item_id = request.POST.get("item_id")
    item = Item.objects.get(id = item_id)
    try:
        itemstatus = ItemStatus.objects.get(item_id = item_id)          #checking if someone has made a bid on item
    except ItemStatus.DoesNotExist:
        return HttpResponse(status=500)
    else:
        if itemstatus.sold == True:
            return HttpResponse("Your Item has already been sold")
        else:
            user = User.objects.get(id=itemstatus.user_id)
            contact = User.objects.get(id = item.User_id)
            itemstatus.sold = True                              #updating stataus
            itemstatus.save()
            item.bidding = False
            item.save()
            price = itemstatus.bid
            buyermessage = render_to_string('buyer.html', {
                'user':user,
                'contact': contact,
                'price': price,
                'item': item,
            })
            buyer_mail_subject = 'You had highest bid, Item was sold to you'
            buyer_to_email = user.email
            buyer_email = EmailMessage(buyer_mail_subject, buyermessage, to=[buyer_to_email])
            buyer_email.send()
            return HttpResponse("Item Successfully Sold to Highest Bidder")

def buyNow(request):
    if request.POST.get("user_id") != "0":
        user = User.objects.get(id=request.POST.get("user_id"))     #user who wants to buy item
        item_id = request.POST.get("item_id")
        item = Item.objects.get(id = item_id)
        contact = User.objects.get(id = item.User_id)       #the user who has listed item
        try:
            itemstatus = ItemStatus.objects.get(item_id = item_id)      #checking for the bids
        except ItemStatus.DoesNotExist:
            newItem = ItemStatus(bid=item.starting_bid, item_id=item_id, user_id=request.POST.get("user_id"),sold=True)
            item.bidding = False
            price = item.starting_bid
            item.save()
            newItem.save()
        else:
            itemstatus.user_id = request.POST.get("user_id")
            itemstatus.sold = True
            item.bidding = False
            price = itemstatus.bid          #updating item status
            item.save()
            itemstatus.save()
        buyermessage = render_to_string('buyer.html', {
            'user':user,
            'contact': contact,
            'price': price,
            'item': item,
        })
        sellermessage = render_to_string('seller.html', {
            'user':user,
            'contact': contact,
            'price': price,
            'item': item,
        })
        buyer_mail_subject = 'Instructions For Item You Bought'
        seller_mail_subject = 'Your Item was Sold'
        buyer_to_email = user.email
        seller_to_email = contact.email
        buyer_email = EmailMessage(buyer_mail_subject, buyermessage, to=[buyer_to_email])       #sending buyer email for instructions
        seller_email = EmailMessage(seller_mail_subject, sellermessage, to=[seller_to_email])   #sending the seller the email for sold item
        buyer_email.send()
        seller_email.send()
        return HttpResponse("Successfully Item Bought")
    else:
        return HttpResponse(status=500)

def addItem(request):
    user=request.user
    if request.method == 'POST':
        item = Item(User=user, title=request.POST.get('title'),description=request.POST.get('description'),starting_bid=request.POST.get('starting_bid'),
        location=request.POST.get('location'),lat=request.POST.get('lat'), lng=request.POST.get('lng'), bidding=True, image=request.FILES['image'])
        item.save()     #creating the item from the form atttributes
        messages.success(request, 'Item Successfully Listed')
        return redirect('dashboard')
    return render(request, 'addItem.html',{})


@login_required(login_url='login')
def dashboard(request):
    itemsListed = Item.objects.filter(User_id = request.user.id)
    itemsSold = Item.objects.filter(itemstatus__sold = True).filter(User_id = request.user.id).count() #items that were listed and sold
    items = Item.objects.filter(itemstatus__user_id = request.user.id).filter(itemstatus__sold = True)  #items for the user
    return render(request, 'dashboard.html', {"itemsListed":itemsListed, "items":items, "itemsSold": itemsSold})

def item_detail(request, pk):
    if request.user.is_authenticated:
        items = Item.objects.exclude(id=pk).exclude(User_id = request.user.id).filter(bidding = True).order_by('id')[:3]    #excluding user listed items from related items
    else:
        items = Item.objects.filter(bidding = True).exclude(id=pk).order_by('?')[:3]    #related Items
    item = Item.objects.get(id=pk)
    try:
        item.itemstatus.bid
    except ItemStatus.DoesNotExist:
        bid = item.starting_bid + 1 #adding 1 to starting bid if no one has bid yet
    else:
        bid = item.itemstatus.bid + 1 #adding one to previous bid
    return render(request, 'item_detail.html',{"item" : item, "bid":bid, "items":items})



def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            message = render_to_string('acc_active_email.html', {
                'user':user,
                'domain':current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = 'Activate Your Account.'
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])  #sending email to verify the account
            email.send()
            return render(request,'email_verified.html', {})
        else:
            print(form.errors)
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):      #verifying the token against the user
        user.is_active = True   #activating account
        user.save()
        login(request, user)
        # return redirect('home')
        return render(request,'email_sent.html', {})
    else:
        return render(request,'invalid_link.html', {})
