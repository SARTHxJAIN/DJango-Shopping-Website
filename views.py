from django import views
from django.db.models.query import RawQuerySet
from django.db.models.query_utils import Q
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class ProductView(View):
    def get(self,request):
        totalitem= 0
        topwears = Product.objects.filter(category='TW')
        mobiles = Product.objects.filter(category='M')
        laptops = Product.objects.filter(category='L')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request,'app/home.html',{'topwears':topwears,'mobiles':mobiles,'laptops':laptops, 'totalitem':totalitem})

class ProductDetailView(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        totalitem= 0
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/productdetail.html',{'product':product,'item_already_in_cart':item_already_in_cart, 'totalitem':totalitem})

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart')

@login_required
def show_cart(request):
    totalitem= 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 50.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                total_amount = shipping_amount + amount
            return render(request, 'app/addtocart.html',{'carts':cart,'total':total_amount,'amount':amount, 'totalitem':totalitem})
        else:
            return render(request,'app/emptycart.html')

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        amount = 0.0
        shipping_amount = 50.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
            total_amount = amount

        data = {
            'quantity': c.quantity,
            'amount':amount,
            'total':shipping_amount + total_amount
        }
        return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        amount = 0.0
        shipping_amount = 50.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
            total_amount =  amount

        data = {
            'quantity': c.quantity,
            'amount':amount,
            'total': shipping_amount + total_amount
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 50.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
            total_amount = amount

        data = {
            'amount':amount,
            'total':total_amount + shipping_amount
        }
        return JsonResponse(data)

@login_required
def buy_now(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return render(request, 'app/buynow.html')
    

def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html',{'add':add,'active':'btn-primary'})

@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html',{'order_placed':op})

def mobile(request, data=None):
    if data==None:
        mobiles = Product.objects.filter(category='M')
    elif data=='Apple' or data=='Samsung':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'Below':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=45000)
    elif data == 'Above':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__gte=45000)
    return render(request, 'app/mobile.html',{'mobiles':mobiles})

def laptop(request, data=None):
    if data==None:
        laptops = Product.objects.filter(category='L')
    elif data=='Asus' or data=='Samsung' or data=='Lenovo':
        laptops = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'Below':
        laptops = Product.objects.filter(category='L').filter(discounted_price__lt=45000)
    elif data == 'Above':
        laptops = Product.objects.filter(category='L').filter(discounted_price__gte=45000)
    return render(request, 'app/laptop.html',{'laptops':laptops})

def topwear(request, data=None):
    if data==None:
        topwears = Product.objects.filter(category='TW')
    elif data=='PeterEngland' or data=='USPolo':
        topwears = Product.objects.filter(category='TW').filter(brand=data)
    elif data == 'Below':
        topwears = Product.objects.filter(category='TW').filter(discounted_price__lt=4500)
    elif data == 'Above':
        topwears = Product.objects.filter(category='TW').filter(discounted_price__gte=4500)
    return render(request, 'app/topwear.html',{'topwears':topwears})

def bottomwear(request, data=None):
    if data==None:
        bottomwears = Product.objects.filter(category='BW')
    elif data=='Pepe' or data=='Levi':
        bottomwears = Product.objects.filter(category='BW').filter(brand=data)
    elif data == 'Below':
        bottomwears = Product.objects.filter(category='BW').filter(discounted_price__lt=4500)
    elif data == 'Above':
        bottomwears = Product.objects.filter(category='BW').filter(discounted_price__gte=4500)
    return render(request, 'app/bottomwear.html',{'bottomwears':bottomwears})

def footwear(request, data=None):
    if data==None:
        footwears = Product.objects.filter(category='FW')
    elif data=='Puma' or data=='Sparx':
        footwears = Product.objects.filter(category='FW').filter(brand=data)
    elif data == 'Below':
        footwears = Product.objects.filter(category='FW').filter(discounted_price__lt=3000)
    elif data == 'Above':
        footwears = Product.objects.filter(category='FW').filter(discounted_price__gte=3000)
    return render(request, 'app/footwear.html',{'footwears':footwears})

def watch(request, data=None):
    if data==None:
        watchs = Product.objects.filter(category='W')
    elif data=='Sonata' or data=='Titan':
        watchs = Product.objects.filter(category='W').filter(brand=data)
    elif data == 'Below':
        watchs = Product.objects.filter(category='W').filter(discounted_price__lt=2000)
    elif data == 'Above':
        watchs = Product.objects.filter(category='W').filter(discounted_price__gte=2000)
    return render(request, 'app/watch.html',{'watchs':watchs})

def headphone(request, data=None):
    if data==None:
        headphones = Product.objects.filter(category='HP')
    elif data=='Cosmic' or data=='JBL':
        headphones = Product.objects.filter(category='HP').filter(brand=data)
    elif data == 'Below':
        headphones = Product.objects.filter(category='HP').filter(discounted_price__lt=2000)
    elif data == 'Above':
        headphones = Product.objects.filter(category='HP').filter(discounted_price__gte=2000)
    return render(request, 'app/headphone.html',{'headphones':headphones})


class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html',{'form':form})

    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,"Congratulations! Registered Succesfully")
            form.save()
        return render(request, 'app/customerregistration.html',{'form':form})

@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 50.0
    total_amount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
            total_amount =  amount + shipping_amount       
    return render(request, 'app/checkout.html',{'add':add,'cart_items':cart_items,'total':total_amount})

@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect("orders")

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html',{'form':form,'active':'btn-primary'})
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            contact = form.cleaned_data['contact']
            reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode, contact=contact)
            reg.save()
            messages.success(request,"Information Saved!")
        return render(request, 'app/profile.html',{'form':form,'active':'btn-primary'})

def search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        prod = Product.objects.filter(brand__icontains=searched) | Product.objects.filter(title__icontains=searched) | Product.objects.filter(category__icontains=searched)
        return render(request,'app/search.html',{'searched':searched, 'prod':prod})
    else:
        return render(request,'app/search.html')
       
    