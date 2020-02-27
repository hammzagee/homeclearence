from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from .models import *


def home(request):
    if request.user.is_authenticated:
        items = Item.objects.exclude(User_id = request.user.id).filter(bidding = True)
    else:
        items = Item.objects.filter(bidding = True)
    return render(request, 'home.html', {"items":items})

def logout2(request):
    logout(request)
    items = Item.objects.filter(bidding = True)
    return render(request, 'home.html', {"items":items})


def makeBid(request):
    if request.POST.get("user_id") != "0":
        print(request.POST.get("user_id"))
        bid = request.POST.get("bid")
        item_id = request.POST.get("item_id")
        try:
            itemstatus = ItemStatus.objects.get(item_id = item_id)
        except ItemStatus.DoesNotExist:
            newItem = ItemStatus(bid=bid, item_id=item_id, user_id=request.POST.get("user_id"),sold=False)
            newItem.save()
        else:
            itemstatus.bid = bid
            itemstatus.save()
        return HttpResponse("Your Bid is Successfully Placed!")
    else:
        return HttpResponse(status=500)

def stopBid(request):
    item_id = request.POST.get("item_id")
    item = Item.objects.get(id = item_id)
    try:
        itemstatus = ItemStatus.objects.get(item_id = item_id)
    except ItemStatus.DoesNotExist:
        return HttpResponse(status=500)
    else:
        if itemstatus.sold == True:
            return HttpResponse("Your Item has already been sold")
        else:
            itemstatus.sold = True
            itemstatus.save()
            item.bidding = False
            item.save()
            return HttpResponse("Item Successfully Sold to Highest Bidder")

# def buyNow(request):



@login_required(login_url='login')
def dashboard(request):
    itemsListed = Item.objects.filter(User_id = request.user.id)
    itemsSold = Item.objects.filter(itemstatus__sold = True).filter(User_id = request.user.id).count()
    items = Item.objects.filter(itemstatus__user_id = request.user.id).filter(itemstatus__sold = True)
    return render(request, 'dashboard.html', {"itemsListed":itemsListed, "items":items, "itemsSold": itemsSold})

def item_detail(request, pk):
    item = Item.objects.get(id=pk)
    try:
        item.itemstatus.bid
    except ItemStatus.DoesNotExist:
        bid = item.starting_bid + 1
    else:
        bid = item.itemstatus.bid + 1
    return render(request, 'item_detail.html',{"item" : item, "bid":bid})



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
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return render(request,'email_verified.html', {})

    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return render(request,'email_sent.html', {})
    else:
        return render(request,'invalid_link.html', {})
