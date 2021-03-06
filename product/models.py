from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import Avg, Count
from django.forms import ModelForm
from django.urls import reverse
from django.utils.safestring import mark_safe
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from taggit.managers import TaggableManager

from home.models import Language

from django.db.utils import OperationalError


class Brand(MPTTModel):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
    )
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    keywords = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(blank=True, upload_to='images/')
    status = models.CharField(max_length=10, choices=STATUS)
    slug = models.SlugField(null=False, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['title']

    def get_absolute_url(self):
        return reverse('brand_products', kwargs={'id': self.pk, 'slug': self.slug})

    def __str__(self):
        return self.title


class Category(MPTTModel):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
    )
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    keywords = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(blank=True, upload_to='images/')
    status = models.CharField(max_length=10, choices=STATUS)
    slug = models.SlugField(null=False, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['title']

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'id': self.pk, 'slug': self.slug})

    def __str__(self):  # __str__ method elaborated later in
        full_path = [self.title]  # post.  use __unicode__ in place of
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' / '.join(full_path[::-1])

    class Meta:
        verbose_name_plural = "Categories"
        verbose_name = "Category"


class Product(models.Model):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
    )

    SEX = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Unisex', 'Unisex'),
    )

    VARIANTS = (
        ('None', 'None'),
        ('Size', 'Size'),
        ('Color', 'Color'),
        ('Size-Color', 'Size-Color'),

    )

    title = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # many to one relation with Category
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, blank=True, null=True)  # many to one relation with Brand
    wishlisted = models.BooleanField(default=False, blank=True, null=True)
    for_kids = models.BooleanField(default=False, blank=True, null=True)
    tags = TaggableManager(blank=True)
    keywords = models.CharField(max_length=255)
    # description = models.TextField(max_length=255)
    image = models.ImageField(upload_to='images/', null=False)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.IntegerField(default=0, blank=True, null=True)  # Only needed when ordering
    minamount = models.IntegerField(default=3, blank=True, null=True)  # Only needed when ordering

    sex = models.CharField(max_length=6, choices=SEX, default='Unisex', blank=False, null=False)
    variant = models.CharField(max_length=10, choices=VARIANTS, default='None')
    detail = RichTextUploadingField()
    slug = models.SlugField(null=False, unique=True)
    status = models.CharField(max_length=10, choices=STATUS, default='True')
    color = models.CharField(max_length=20, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    discount_percentage = models.IntegerField(default=0)
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)

    def __str__(self):
        return self.title

    ## method to create a fake table field in read only mode
    def image_tag(self):
        if self.image.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        else:
            return ""

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'id': self.pk, 'slug': self.slug})

    def get_discount_percentage(self):
        return f'-{self.discount_percentage}%'

    def avaregereview(self):
        reviews = Comment.objects.filter(product=self, status='True').aggregate(avarage=Avg('rate'))
        avg = 0
        if reviews["avarage"] is not None:
            avg = float(reviews["avarage"])
        return avg

    def countreview(self):
        reviews = Comment.objects.filter(product=self, status='True').aggregate(count=Count('id'))
        cnt = 0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt

    def save(self, *args, **kwargs):
        if self.discount_percentage > 1:
            self.discount_price = float((self.discount_percentage / 100)) * float(self.price)
            super(Product, self).save(*args, **kwargs)

        super(Product, self).save(*args, **kwargs)


class Images(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, blank=True)
    image = models.ImageField(blank=True, upload_to='images/')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Images"
        verbose_name = "Images"


class Comment(models.Model):
    STATUS = (
        ('New', 'New'),
        ('True', 'True'),
        ('False', 'False'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, blank=True)
    comment = models.CharField(max_length=250, blank=True)
    rate = models.IntegerField(default=1)
    ip = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['subject', 'comment', 'rate']


class Color(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name

    def color_tag(self):
        if self.code is not None:
            return mark_safe('<p style="background-color:{}">Color </p>'.format(self.code))
        else:
            return ""


class Size(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name


class Variants(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, blank=True, null=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, blank=True, null=True)
    image_id = models.IntegerField(blank=True, null=True, default=0)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.title

    def image(self):
        img = Images.objects.get(id=self.image_id)
        if img.id is not None:
            varimage = img.image.url
        else:
            varimage = ""
        return varimage

    def image_tag(self):
        img = Images.objects.get(id=self.image_id)
        if img.id is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(img.image.url))
        else:
            return ""


try:
    llist = Language.objects.filter(status=True)
    list1 = []
    for rs in llist:
        list1.append((rs.code, rs.name))
    langlist = (list1)
except OperationalError:
    #  no such table: home_language
    langlist = None


class ProductLang(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # many to one relation with Category
    lang = models.CharField(max_length=6, choices=langlist)
    title = models.CharField(max_length=150)
    keywords = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    slug = models.SlugField(null=False, unique=True)
    detail = RichTextUploadingField()

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})


class CategoryLang(models.Model):
    category = models.ForeignKey(Category, related_name='categorylangs',
                                 on_delete=models.CASCADE)  # many to one relation with Category
    lang = models.CharField(max_length=6, choices=langlist)
    title = models.CharField(max_length=150)
    keywords = models.CharField(max_length=255)
    slug = models.SlugField(null=False, unique=True)
    description = models.CharField(max_length=255)

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name_plural = "Wishlists"
        verbose_name = "Wishlist"

    def save(self, *args, **kwargs):
        Product.objects.filter(pk=self.product.pk).update(wishlisted=True)
        super(Wishlist, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        Product.objects.filter(pk=self.product.pk).update(wishlisted=False)
        super(Wishlist, self).delete(*args, **kwargs)
