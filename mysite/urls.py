"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

import home
from home import views
from order import views as OrderViews
from user import views as UserViews
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    path('selectlanguage', views.selectlanguage, name='selectlanguage'),
    path('selectcurrency', views.selectcurrency, name='selectcurrency'),
    path('change_currency/<str:c_type>/', views.change_currency, name='change_currency'),
    path('savelangcur', views.savelangcur, name='savelangcur'),
    path('i18n/', include('django.conf.urls.i18n')),
]


urlpatterns += i18n_patterns(
    path('currencies/', include('currencies.urls')),
    path(_('admin/'), admin.site.urls),
    path('', views.index, name='home'),
    path('home/', include('home.urls')),
    path('product/', include('product.urls')),
    path('order/', include('order.urls')),
    path('user/', include('user.urls'), name='user'),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    path('create_product_stripe/<str:total>/<str:currency>/', views.create_product_stripe, name='create_product_stripe'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout_index/', views.checkout_index, name='checkout_index'),
    path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('thanks/', views.thanks, name='thanks'),


    path(_('about/'), views.aboutus, name='aboutus'),
    path(_('contact/'), views.contactus, name='contactus'),
    path('search/', views.search, name='search'),
    path('search_auto/', views.search_auto, name='search_auto'),
    path('men', views.men_products, name='men_products'),
    path('women', views.women_products, name='women_products'),
    path('kids', views.kids_products, name='kids_products'),
    path('unisex', views.unisex_products, name='unisex_products'),
    path('category/<int:id>/<slug:slug>', views.category_products, name='category_products'),
    path('brand/<int:id>/<slug:slug>', views.brand_products, name='brand_products'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('shopcart/', OrderViews.shopcart, name='shopcart'),
    path('login/', UserViews.login_form, name='login'),
    path('logout/', UserViews.logout_func, name='logout'),
    path('signup/', UserViews.signup_form, name='signup'),
    path('faq/', views.faq, name='faq'),
    path('ajaxcolor/', views.ajaxcolor, name='ajaxcolor'),
    prefix_default_language=False,
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)