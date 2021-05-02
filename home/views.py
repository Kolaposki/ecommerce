import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q, F
from django.db.models.functions import Concat
# from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, request
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import translation

from home.forms import SearchForm
from home.models import Setting, ContactForm, ContactMessage, FAQ, SettingLang, Language
from mysite import settings
from product.models import *
from order.models import ShopCart

from user.models import UserProfile
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def thanks(request):
    return render(request, 'thanks.html')


@csrf_exempt
def checkout(request):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1H06q8IdX0gthvYPWudV1aw1',
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('thanks')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('index')),
    )

    return JsonResponse({
        'session_id': session.id,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })


@csrf_exempt
def stripe_webhook(request):
    print('WEBHOOK!')
    # You can find your endpoint's secret in your webhook settings
    endpoint_secret = 'whsec_Xj8wBk2qiUcjDEmYu5kfKkOrJCJ5UUjW'

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        print(line_items)

    return HttpResponse(status=200)


def index(request):
    if not request.session.has_key('currency'):
        request.session['currency'] = settings.DEFAULT_CURRENCY

    setting = Setting.objects.get(pk=1)
    products_latest = Product.objects.all().order_by('-id')[:4]  # last 4 products
    # >>>>>>>>>>>>>>>> M U L T I   L A N G U G A E >>>>>> START
    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]

    if defaultlang != currentlang:
        setting = SettingLang.objects.get(lang=currentlang)
        products_latest = Product.objects.raw(
            'SELECT p.id,p.price, l.title, l.description,l.slug  '
            'FROM product_product as p '
            'LEFT JOIN product_productlang as l '
            'ON p.id = l.product_id '
            'WHERE  l.lang=%s ORDER BY p.id DESC LIMIT 4', [currentlang])

    products_slider = Product.objects.all().order_by('id')[:4]  # first 4 products

    products_picked = Product.objects.all().order_by('?')[:4]  # Random selected 4 products

    page = "home"
    context = {'setting': setting,
               'page': page,
               'products_slider': products_slider,
               'products_latest': products_latest,
               'products_picked': products_picked,
               # 'category':category
               }

    return render(request, 'index.html', context)


def wishlist(request):
    products = Wishlist.objects.filter(user_id=request.user.id)
    print("wishlist_pro: ", products)

    context = {'wishlists': products, }
    return render(request, 'wishlist.html', context)


@login_required(login_url='/login')  # Check login
# Handles wishlisting of products in an asynchronous manner [AJAX]
def wishlist_actions_ajax(request):
    if request.method == 'GET' and request.is_ajax():

        current_user = request.user  # Access User Session information
        product_id = request.GET['product_id']
        product = Product.objects.get(pk=product_id)
        data_dict = {}

        try:
            wishlist_obj = Wishlist.objects.get(product=product)
            print("wishlist_obj presnt: ", wishlist_obj)
        except Wishlist.DoesNotExist:
            print("wishlist_obj Absent: ")
            wishlist_obj = Wishlist(user_id=int(current_user.id), product=product)
            wishlist_obj.save()

            print("Wishlisted objected", wishlist_obj)
            print("Wishlisted: ", product.wishlisted)
            count = Wishlist.objects.filter(user_id=int(current_user.id)).count()

            data_dict = {'count': count, 'wishlisted': True}
            return JsonResponse(data=data_dict, safe=False)

        wishlist_obj.delete()

        count = Wishlist.objects.filter(user_id=int(current_user.id)).count()
        data_dict = {'count': count, 'wishlisted': False}
        return JsonResponse(data=data_dict, safe=False)

    else:
        return HttpResponseBadRequest('Unrecognized request')


def new_home(request):
    if not request.session.has_key('currency'):
        request.session['currency'] = settings.DEFAULT_CURRENCY
        print("No currency", request.session['currency'])

    setting = Setting.objects.get(pk=1)
    products_latest = Product.objects.all().order_by('-id')[:3]  # last 3 products
    # >>>>>>>>>>>>>>>> M U L T I   L A N G U G A E >>>>>> START
    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]

    if defaultlang != currentlang:
        setting = SettingLang.objects.get(lang=currentlang)
        products_latest = Product.objects.raw(
            'SELECT p.id,p.price, l.title, l.description,l.slug  '
            'FROM product_product as p '
            'LEFT JOIN product_productlang as l '
            'ON p.id = l.product_id '
            'WHERE  l.lang=%s ORDER BY p.id DESC LIMIT 4', [currentlang])

    products_slider = Product.objects.all().order_by('id')[:3]  # first 3 products

    products_picked = Product.objects.all().order_by('?')[:3]  # Random selected 3 products

    category = Category.objects.all()
    current_user = request.user  # Access User Session information
    shop_cart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    for rs in shop_cart:
        if rs.product.discount_price:
            total += rs.product.discount_price * rs.quantity
        else:
            total += rs.product.price * rs.quantity

    page = "home"
    context = {'setting': setting,
               'page': page,
               'products_slider': products_slider,
               'products_latest': products_latest,
               'products_picked': products_picked,
               'shopcart': shop_cart,
               'category': category,
               'total': total,
               }

    return render(request, 'home.html', context)


def selectlanguage(request):
    if request.method == 'POST':  # check post
        cur_language = translation.get_language()
        lasturl = request.META.get('HTTP_REFERER')
        lang = request.POST['language']
        translation.activate(lang)
        request.session[translation.LANGUAGE_SESSION_KEY] = lang
        # return HttpResponse(lang)
        return HttpResponseRedirect("/" + lang)


def aboutus(request):
    # category = categoryTree(0,'',currentlang)
    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]
    setting = Setting.objects.get(pk=1)
    if defaultlang != currentlang:
        setting = SettingLang.objects.get(lang=currentlang)

    context = {'setting': setting}
    return render(request, 'about.html', context)


def contactus(request):
    currentlang = request.LANGUAGE_CODE[0:2]
    # category = categoryTree(0,'',currentlang)
    if request.method == 'POST':  # check post
        form = ContactForm(request.POST)
        if form.is_valid():
            data = ContactMessage()  # create relation with model
            data.name = form.cleaned_data['name']  # get form input data
            data.email = form.cleaned_data['email']
            data.subject = form.cleaned_data['subject']
            data.message = form.cleaned_data['message']
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()  # save data to table
            messages.success(request, "Your message has ben sent. Thank you for your message.")
            return HttpResponseRedirect('/contact')

    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]
    setting = Setting.objects.get(pk=1)
    if defaultlang != currentlang:
        setting = SettingLang.objects.get(lang=currentlang)

    form = ContactForm
    context = {'setting': setting, 'form': form}
    return render(request, 'contactus.html', context)


def category_products(request, id, slug):
    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]
    catdata = Category.objects.get(pk=id)
    products = Product.objects.filter(category_id=id)  # default language
    if defaultlang != currentlang:
        try:
            products = Product.objects.raw(
                'SELECT p.id,p.price,p.amount,p.image,p.variant,l.title, l.keywords, l.description,l.slug,l.detail '
                'FROM product_product as p '
                'LEFT JOIN product_productlang as l '
                'ON p.id = l.product_id '
                'WHERE p.category_id=%s and l.lang=%s', [id, currentlang])
        except:
            pass
        catdata = CategoryLang.objects.get(category_id=id, lang=currentlang)

    context = {'products': products,
               'catdata': catdata}
    return render(request, 'shop-category.html', context)


def men_products(request):
    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]
    products = Product.objects.filter(sex='Male')
    all_brands = []

    for product in products:
        # reverse lookup
        if product.brand:
            all_brands.append(product.brand)

    top_brands = set(all_brands)
    total = len(products)
    next_page = False

    top_tags = Product.tags.most_common()[:7]

    if total > 21:
        next_page = True

    products = products[0:21]

    if defaultlang != currentlang:
        try:
            products = Product.objects.raw(
                'SELECT p.id,p.price,p.amount,p.image,p.variant,l.title, l.keywords, l.description,l.slug,l.detail '
                'FROM product_product as p '
                'LEFT JOIN product_productlang as l '
                'ON p.id = l.product_id '
                'WHERE p.category_id=%s and l.lang=%s', [id, currentlang])
        except:
            pass

    context = {'products': products, "is_brand": False, 'category': 'Men', 'next_page': next_page, 'total': total,
               'top_tags': top_tags, 'top_brands': top_brands}
    return render(request, 'shop-category.html', context)


def women_products(request):
    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]
    products = Product.objects.filter(sex='Female')
    if defaultlang != currentlang:
        try:
            products = Product.objects.raw(
                'SELECT p.id,p.price,p.amount,p.image,p.variant,l.title, l.keywords, l.description,l.slug,l.detail '
                'FROM product_product as p '
                'LEFT JOIN product_productlang as l '
                'ON p.id = l.product_id '
                'WHERE p.category_id=%s and l.lang=%s', [id, currentlang])
        except:
            pass

    context = {'products': products, "is_brand": False, 'category': 'Women'}
    return render(request, 'shop-category.html', context)


def kids_products(request):
    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]
    products = Product.objects.filter(sex='for_kids')
    if defaultlang != currentlang:
        try:
            products = Product.objects.raw(
                'SELECT p.id,p.price,p.amount,p.image,p.variant,l.title, l.keywords, l.description,l.slug,l.detail '
                'FROM product_product as p '
                'LEFT JOIN product_productlang as l '
                'ON p.id = l.product_id '
                'WHERE p.category_id=%s and l.lang=%s', [id, currentlang])
        except:
            pass

    context = {'products': products, "is_brand": False, 'category': 'Kids'}
    return render(request, 'shop-category.html', context)


def brand_products(request, id, slug):
    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]
    brand_data = Brand.objects.get(pk=id)
    products = Product.objects.filter(brand_id=id)  # default language
    if defaultlang != currentlang:
        try:
            products = Product.objects.raw(
                'SELECT p.id,p.price,p.amount,p.image,p.variant,l.title, l.keywords, l.description,l.slug,l.detail '
                'FROM product_product as p '
                'LEFT JOIN product_productlang as l '
                'ON p.id = l.product_id '
                'WHERE p.category_id=%s and l.lang=%s', [id, currentlang])
        except:
            pass
        brand_data = CategoryLang.objects.get(category_id=id, lang=currentlang)

    context = {'products': products,
               'catdata': brand_data, "is_brand": True}
    return render(request, 'shop-category.html', context)


def search(request):
    if request.method == 'POST':  # check post
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']  # get form input data
            catid = form.cleaned_data['catid']
            if catid == 0:
                products = Product.objects.filter(
                    title__icontains=query)  # SELECT * FROM product WHERE title LIKE '%query%'
            else:
                products = Product.objects.filter(title__icontains=query, category_id=catid)

            category = Category.objects.all()
            context = {'products': products, 'query': query,
                       'category': category}
            return render(request, 'search_products.html', context)

    return HttpResponseRedirect('/')


def search_auto(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        products = Product.objects.filter(title__icontains=q)

        results = []
        for rs in products:
            product_json = {}
            product_json = rs.title + " > " + rs.category.title
            results.append(product_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def product_detail(request, id, slug):
    query = request.GET.get('q')
    # >>>>>>>>>>>>>>>> M U L T I   L A N G U G A E >>>>>> START
    defaultlang = settings.LANGUAGE_CODE[0:2]  # en-EN
    currentlang = request.LANGUAGE_CODE[0:2]
    # category = categoryTree(0, '', currentlang)
    category = Category.objects.all()

    product = Product.objects.get(pk=id)

    if defaultlang != currentlang:
        try:
            prolang = Product.objects.raw(
                'SELECT p.id,p.price,p.amount,p.image,p.variant,l.title, l.keywords, l.description,l.slug,l.detail '
                'FROM product_product as p '
                'INNER JOIN product_productlang as l '
                'ON p.id = l.product_id '
                'WHERE p.id=%s and l.lang=%s', [id, currentlang])
            product = prolang[0]
        except:
            pass
    # <<<<<<<<<< M U L T I   L A N G U G A E <<<<<<<<<<<<<<< end

    images = Images.objects.filter(product_id=id)
    comments = Comment.objects.filter(product_id=id, status='True')
    context = {'product': product, 'category': category,
               'images': images, 'comments': comments,
               }
    if product.variant != "None":  # Product have variants
        if request.method == 'POST':  # if we select color
            variant_id = request.POST.get('variantid')
            variant = Variants.objects.get(id=variant_id)  # selected product by click color radio
            colors = Variants.objects.filter(product_id=id, size_id=variant.size_id)
            sizes = Variants.objects.raw('SELECT * FROM  product_variants  WHERE product_id=%s GROUP BY size_id', [id])
            query += variant.title + ' Size:' + str(variant.size) + ' Color:' + str(variant.color)
        else:
            variants = Variants.objects.filter(product_id=id)
            colors = Variants.objects.filter(product_id=id, size_id=variants[0].size_id)
            sizes = Variants.objects.raw('SELECT * FROM  product_variants  WHERE product_id=%s GROUP BY size_id', [id])
            variant = Variants.objects.get(id=variants[0].id)
        context.update({'sizes': sizes, 'colors': colors,
                        'variant': variant, 'query': query
                        })
    return render(request, 'single-product.html', context)


def ajaxcolor(request):
    data = {}
    if request.POST.get('action') == 'post':
        size_id = request.POST.get('size')
        productid = request.POST.get('productid')
        colors = Variants.objects.filter(product_id=productid, size_id=size_id)
        context = {
            'size_id': size_id,
            'productid': productid,
            'colors': colors,
        }
        data = {'rendered_table': render_to_string('color_list.html', context=context)}
        return JsonResponse(data)
    return JsonResponse(data)


def faq(request):
    defaultlang = settings.LANGUAGE_CODE[0:2]
    currentlang = request.LANGUAGE_CODE[0:2]

    if defaultlang == currentlang:
        faq = FAQ.objects.filter(status="True", lang=defaultlang).order_by("ordernumber")
    else:
        faq = FAQ.objects.filter(status="True", lang=currentlang).order_by("ordernumber")

    context = {
        'faq': faq,
    }
    return render(request, 'faq.html', context)


def selectcurrency(request):
    lasturl = request.META.get('HTTP_REFERER')
    if request.method == 'POST':  # check post
        request.session['currency'] = request.POST['currency']
    return HttpResponseRedirect(lasturl)


@login_required(login_url='/login')  # Check login
def savelangcur(request):
    lasturl = request.META.get('HTTP_REFERER')
    curren_user = request.user
    language = Language.objects.get(code=request.LANGUAGE_CODE[0:2])
    # Save to User profile database
    data = UserProfile.objects.get(user_id=curren_user.id)
    data.language_id = language.id
    data.currency_id = request.session['currency']
    data.save()  # save data
    return HttpResponseRedirect(lasturl)
