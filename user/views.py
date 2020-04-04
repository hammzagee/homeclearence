from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, ItemForm, ProfileForm
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
    if request.user.is_authenticated:   #item searched based on keywords
        result = Item.objects.exclude(User_id = request.user.id).filter(bidding = True).filter(title__contains=search)
    else:
        result = Item.objects.filter(bidding = True).filter(title__contains=search)
    return render(request,'home.html',{"items":result})

def home(request):
    chk = Item.objects.filter(bidding=True)
    for it in chk:
        c = it.bidding_end_data-it.created_at
        if c.days == 0:
            expTime(it.id)
    if request.user.is_authenticated:
        items = Item.objects.exclude(User_id = request.user.id).filter(bidding = True).order_by('-views')
    else:
        items = Item.objects.filter(bidding = True).order_by('-views')
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
            item = Item.objects.get(id = item_id)
            u = User.objects.get(id = itemstatus.user_id)
            bidreplace = render_to_string('bidReplaced.html',{
                'bid': bid,
                'user': u,
                'item':item,
            })
            mail_subject = 'You Bid on '+ item.title + 'was replaced'
            print("im here")
            email = u.email
            _email = EmailMessage(mail_subject, bidreplace, to=[email])
            _email.send()
            itemstatus.user_id = request.POST.get("user_id")
            itemstatus.bid = bid                #updating bid for item
            itemstatus.save()
        return HttpResponse("Your Bid is Successfully Placed!")
    else:
        return HttpResponse(status=500)


# This Function is used to remove the items which have expired the bidding timeself.
# exp can be selling the item to highest bidder if any or just removing from platform if there are no bids
def expTime(item_id):
    item = Item.objects.get(id=item_id)
    try:
        itemstatus = ItemStatus.objects.get(item_id = item_id)
    except ItemStatus.DoesNotExist:
        item.bidding = False
        item.save()
        return True
    else:
        if itemstatus.sold == True:
            return True
        else:
            user = User.objects.get(id=itemstatus.user_id)
            contact = User.objects.get(id = item.User_id)
            itemstatus.sold = True                              #updating stataus
            itemstatus.save()
            item.bidding = False
            item.save()
            price = itemstatus.bid
            buyermessage = render_to_string('buyer.html', {     #sending the highest bidder an email that item is sold to you
                'user':user,
                'contact': contact,
                'price': price,
                'item': item,
            })
            buyer_mail_subject = 'You had highest bid, Item was sold to you'
            buyer_to_email = user.email
            buyer_email = EmailMessage(buyer_mail_subject, buyermessage, to=[buyer_to_email])
            buyer_email.send()
            return True


# This function is same as the above one but it is used when a user opt
#to stop bidding ona product from dashboard
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
            buyermessage = render_to_string('buyer.html', {     #sending the highest bidder an email that item is sold to you
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


#THis function is used when a user click buyNow and it sends email
# both to buyer and seller for the futher insstructions
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
            price = item.buyNow
            item.save()
            newItem.save()
        else:
            itemstatus.user_id = request.POST.get("user_id")
            itemstatus.sold = True
            item.bidding = False
            price = item.buyNow        #updating item status
            item.save()
            itemstatus.save()
        buyermessage = render_to_string('buyer.html', {         #sending the email to buyer for further details
            'user':user,
            'contact': contact,
            'price': price,
            'item': item,
        })
        sellermessage = render_to_string('seller.html', {       #sending seller email for the news of item sold
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


#Used when user wants to list an item on platform
def addItem(request):
    user=request.user
    if request.method == 'POST':
        item = Item(User=user, title=request.POST.get('title'),description=request.POST.get('description'),starting_bid=request.POST.get('starting_bid'),
        location=request.POST.get('location'),lat=request.POST.get('lat'), lng=request.POST.get('lng'), bidding=True, image=request.FILES['image'],
        buyNow=request.POST.get('buyNow'), bidding_end_data=request.POST.get('bidding_end_data'))
        item.save()     #creating the item from the form atttributes
        messages.success(request, 'Item Successfully Listed')
        return redirect('dashboard')
    return render(request, 'addItem.html',{})


#dashboard Information for a authenticated user
@login_required(login_url='login')
def dashboard(request):
    itemsListed = Item.objects.filter(User_id = request.user.id)
    itemsSold = Item.objects.filter(itemstatus__sold = True).filter(User_id = request.user.id).count() #items that were listed and sold
    items = Item.objects.filter(itemstatus__user_id = request.user.id).filter(itemstatus__sold = True)  #items for the user
    return render(request, 'dashboard.html', {"itemsListed":itemsListed, "items":items, "itemsSold": itemsSold})

#if user wants to remove item from listing it is not same as stop bidding
def remove_item(request,pk):
    item = Item.objects.get(id=pk)
    item.delete()
    return HttpResponse("Item Successfully Removed from Listing")


#item details page information with related Items also
# as of now all the items on the platform are of houseHold
# So the related items are selected upon the number of views,
# Views for a item increases whenever there is a click on it.
def item_detail(request, pk):
    if request.user.is_authenticated:
        items = Item.objects.exclude(id=pk).exclude(User_id = request.user.id).filter(bidding = True).order_by('id')[:3]    #excluding user listed items from related items
    else:
        items = Item.objects.filter(bidding = True).exclude(id=pk).order_by('-views')[:3]    #related Items in the suggestions
    item = Item.objects.get(id=pk)
    v = item.views + 1
    item.views = v
    item.save()
    try:
        item.itemstatus.bid
    except ItemStatus.DoesNotExist:
        bid = item.starting_bid  #adding 1 to starting bid if no one has bid yet
    else:
        bid = item.itemstatus.bid #adding one to previous bid

    days = item.bidding_end_data-item.created_at
    return render(request, 'item_detail.html',{"item" : item, "bid":bid, "items":items, "days":days})



def signup(request): #registering the user
    if request.method == 'POST':
        form = SignupForm(request.POST)
        profileForm = ProfileForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            profile = Profile(user = user, phone=request.POST.get('phone'))
            user.save()
            profile.save()
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
        profileForm = ProfileForm()

    return render(request, 'signup.html', {'form': form, 'profile':profileForm})

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
