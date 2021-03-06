from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest

# Create your views here.
from django.utils.crypto import get_random_string

from order.models import ShopCart, ShopCartForm, OrderForm, Order, OrderProduct
from product.models import Category, Product, Variants
from user.models import UserProfile


def index(request):
    return HttpResponse("Order Page")


@login_required(login_url='/login')  # Check login
def addtoshopcart(request, id):
    url = request.META.get('HTTP_REFERER')  # get last url
    current_user = request.user  # Access User Session information
    product = Product.objects.get(pk=id)

    if product.variant != 'None':
        variantid = request.POST.get('variantid')  # from variant add to cart
        checkinvariant = ShopCart.objects.filter(variant_id=variantid,
                                                 user_id=current_user.id)  # Check product in shopcart
        if checkinvariant:
            control = 1  # The product is in the cart
        else:
            control = 0  # The product is not in the cart"""
    else:
        checkinproduct = ShopCart.objects.filter(product_id=id, user_id=current_user.id)  # Check product in shopcart
        if checkinproduct:
            control = 1  # The product is in the cart
        else:
            control = 0  # The product is not in the cart"""

    if request.method == 'POST':  # if there is a post
        form = ShopCartForm(request.POST)
        if form.is_valid():
            if control == 1:  # Update  shopcart
                if product.variant == 'None':
                    data = ShopCart.objects.get(product_id=id, user_id=current_user.id)
                else:
                    data = ShopCart.objects.get(product_id=id, variant_id=variantid, user_id=current_user.id)
                data.quantity += form.cleaned_data['quantity']
                data.save()  # save data
            else:  # Inser to Shopcart
                data = ShopCart()
                data.user_id = current_user.id
                data.product_id = id
                data.variant_id = variantid
                data.quantity = form.cleaned_data['quantity']
                data.save()
        messages.success(request, "Product added to Shopcart ")
        return HttpResponseRedirect(url)

    else:  # if there is no post
        if control == 1:  # Update  shopcart
            data = ShopCart.objects.get(product_id=id, user_id=current_user.id)
            data.quantity += 1
            data.save()  #
        else:  # Inser to Shopcart
            data = ShopCart()  # model ile ba??lant?? kur
            data.user_id = current_user.id
            data.product_id = id
            data.quantity = 1
            data.variant_id = None
            data.save()  #
        messages.success(request, "Product added to Shopcart")
        return HttpResponseRedirect(url)


@login_required(login_url='/login')  # Check login
def add_to_cart_ajax(request):
    if request.method == 'GET' and request.is_ajax():

        current_user = request.user  # Access User Session information
        print("current_user: ", current_user)
        product_id = request.GET['product_id']
        new_quantity = request.GET['new_quantity']
        print("new_quantity: ", new_quantity)

        product = Product.objects.get(pk=product_id)

        checkinproduct = ShopCart.objects.filter(product_id=product_id,
                                                 user_id=int(current_user.id))  # Check product in shopcart
        if checkinproduct:
            control = 1  # The product is in the cart
        else:
            control = 0  # The product is not in the cart"""

        if control == 1:  # Update  shopcart
            data = ShopCart.objects.get(product_id=product_id, user=current_user)
            if new_quantity:
                data.quantity += int(new_quantity)
            else:
                data.quantity += 1
            data.save()  #
        else:  # Insert to Shopcart
            data = ShopCart()  #
            data.user_id = current_user.id
            data.product_id = product_id
            if new_quantity:
                data.quantity = int(new_quantity)
            else:
                data.quantity = 1
            data.variant_id = None
            data.save()

        all_shop_cart = ShopCart.objects.filter(user_id=int(current_user.id))
        total = 0
        for rs in all_shop_cart:
            if rs.product.discount_price:
                total += rs.product.discount_price * rs.quantity
            else:
                total += rs.product.price * rs.quantity

        html = render_to_string(
            template_name="partials/header_minicart.html",
            context={'shopcart': all_shop_cart, 'total': total, "request": request, "user_pk": int(current_user.id),
                     'curr': request.session['currency']}
        )

        count = all_shop_cart.count()
        data_dict = {"html_from_view": html, 'count': count}
        return JsonResponse(data=data_dict, safe=False)

        # return HttpResponse('success')
    else:
        return HttpResponseBadRequest('Unrecognized request')


def shopcart(request):
    category = Category.objects.all()
    current_user = request.user  # Access User Session information
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    for rs in shopcart:
        if rs.product.discount_price:
            total += rs.product.discount_price * rs.quantity
        else:
            total += rs.product.price * rs.quantity

    context = {'shopcart': shopcart,
               'category': category,
               'total': total, 'curr': request.session['currency']
               }
    return render(request, 'shopcart.html', context)


@login_required(login_url='/login')  # Check login
def deletefromcart(request, id):
    ShopCart.objects.filter(id=id).delete()
    messages.success(request, "Your item deleted form Shopcart.")
    return HttpResponseRedirect("/shopcart")


@login_required(login_url='/login')  # Check login
def delete_from_cart_ajax(request):
    if request.method == 'GET' and request.is_ajax():

        current_user = request.user  # Access User Session information
        product_id = request.GET['product_id']
        ShopCart.objects.filter(id=product_id).delete()

        all_shop_cart = ShopCart.objects.filter(user_id=int(current_user.id))
        total = 0
        for rs in all_shop_cart:
            if rs.product.discount_price:
                total += rs.product.discount_price * rs.quantity
            else:
                total += rs.product.price * rs.quantity

        html = render_to_string(
            template_name="partials/header_minicart.html",
            context={'shopcart': all_shop_cart, 'total': total, "request": request, "user_pk": int(current_user.id),
                     'curr': request.session['currency']}
        )

        count = all_shop_cart.count()
        data_dict = {"html_from_view": html, 'count': count}
        return JsonResponse(data=data_dict, safe=False)
    else:
        return HttpResponseBadRequest('Unrecognized request')


def orderproduct(request):
    category = Category.objects.all()
    current_user = request.user
    shop_cart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    for rs in shop_cart:
        if rs.product.variant == 'None':
            total += rs.product.price * rs.quantity
        else:
            total += rs.variant.price * rs.quantity

    if request.method == 'POST':  # if there is a post
        form = OrderForm(request.POST)
        # return HttpResponse(request.POST.items())
        if form.is_valid():
            # Send Credit card to bank,  If the bank responds ok, continue, if not, show the error

            data = Order()
            data.first_name = form.cleaned_data['first_name']  # get product quantity from form
            data.last_name = form.cleaned_data['last_name']
            data.address = form.cleaned_data['address']
            data.city = form.cleaned_data['city']
            data.phone = form.cleaned_data['phone']
            data.user_id = current_user.id
            data.total = total
            data.ip = request.META.get('REMOTE_ADDR')
            ordercode = get_random_string(5).upper()  # random cod
            data.code = ordercode
            data.save()  #

            for rs in shop_cart:
                detail = OrderProduct()
                detail.order_id = data.id  # Order Id
                detail.product_id = rs.product_id
                detail.user_id = current_user.id
                detail.quantity = rs.quantity
                if rs.product.variant == 'None':
                    detail.price = rs.product.price
                else:
                    detail.price = rs.variant.price
                detail.variant_id = rs.variant_id
                detail.amount = rs.amount
                detail.save()
                # ***Reduce quantity of sold product from Amount of Product
                if rs.product.variant == 'None':
                    product = Product.objects.get(id=rs.product_id)
                    product.amount -= rs.quantity
                    product.save()
                else:
                    variant = Variants.objects.get(id=rs.product_id)
                    variant.quantity -= rs.quantity
                    variant.save()
                # ************ <> *****************

            ShopCart.objects.filter(user_id=current_user.id).delete()  # Clear & Delete shopcart
            request.session['cart_items'] = 0
            messages.success(request, "Your Order has been completed. Thank you ")
            return render(request, 'complete.html',
                          {'ordercode': ordercode, 'category': category, 'curr': request.session['currency']})
        else:
            messages.warning(request, form.errors)
            return HttpResponseRedirect("/order/orderproduct")

    form = OrderForm()
    profile = UserProfile.objects.get(user_id=current_user.id)
    context = {'shopcart': shop_cart,
               'category': category,
               'total': total,
               'form': form,
               'profile': profile, 'curr': request.session['currency']
               }
    return render(request, 'checkout.html', context)
