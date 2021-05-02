import admin_thumbnails
from django.contrib import admin

# Register your models here.
from mptt.admin import DraggableMPTTAdmin

from product import models
from product.models import Category, Product, Images, Comment, Color, Size, Variants, ProductLang, CategoryLang, Brand, \
    Wishlist


class CategoryLangInline(admin.TabularInline):
    model = CategoryLang
    extra = 1
    show_change_link = True
    prepopulated_fields = {'slug': ('title',)}


class CategoryAdmin2(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = ('tree_actions', 'indented_title',
                    'related_products_count', 'related_products_cumulative_count')
    list_display_links = ('indented_title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CategoryLangInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative product count
        qs = Category.objects.add_related_count(
            qs,
            Product,
            'category',
            'products_cumulative_count',
            cumulative=True)

        # Add non cumulative product count
        qs = Category.objects.add_related_count(qs,
                                                Product,
                                                'category',
                                                'products_count',
                                                cumulative=False)
        return qs

    def related_products_count(self, instance):
        return instance.products_count

    related_products_count.short_description = 'Related products (for this specific category)'

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count

    related_products_cumulative_count.short_description = 'Related products (in tree)'


class BrandAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = ('tree_actions', 'indented_title',
                    'related_products_count', 'related_products_cumulative_count')
    list_display_links = ('indented_title',)
    prepopulated_fields = {'slug': ('title',)}

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative product count
        qs = Brand.objects.add_related_count(
            qs,
            Product,
            'brand',
            'products_cumulative_count',
            cumulative=True)

        # Add non cumulative product count
        qs = Brand.objects.add_related_count(qs,
                                             Product,
                                             'category',
                                             'products_count',
                                             cumulative=False)
        return qs

    def related_products_count(self, instance):
        return instance.products_count

    related_products_count.short_description = 'Related products (for this specific brand)'

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count

    related_products_cumulative_count.short_description = 'Related products (in tree)'


@admin_thumbnails.thumbnail('image')
class ProductImageInline(admin.TabularInline):
    model = Images
    readonly_fields = ('id',)
    extra = 1


class ProductVariantsInline(admin.TabularInline):
    model = Variants
    readonly_fields = ('image_tag',)
    extra = 1
    show_change_link = True


class ProductLangInline(admin.TabularInline):
    model = ProductLang
    extra = 1
    show_change_link = True
    prepopulated_fields = {'slug': ('title',)}


@admin_thumbnails.thumbnail('image')
class ImagesAdmin(admin.ModelAdmin):
    list_display = ['image', 'title', 'image_thumbnail']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'price', 'image_tag', 'brand', 'sex']
    list_filter = ['category', 'brand', 'sex']
    inlines = [ProductImageInline, ProductVariantsInline, ProductLangInline]
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('image_tag', 'wishlisted', "amount", "minamount", "variant")
    exclude = ("wishlisted ", "amount ", "minamount ", "variant ")


class CommentAdmin(admin.ModelAdmin):
    list_display = ['subject', 'comment', 'status', 'create_at']
    list_filter = ['status']
    readonly_fields = ('subject', 'comment', 'ip', 'user', 'product', 'rate', 'id')


class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'color_tag']


class WishlistAdmin(admin.ModelAdmin):
    list_display = ['product', ]


class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


class VariantsAdmin(admin.ModelAdmin):
    list_display = ['title', 'product', 'color', 'size', 'price', 'quantity', 'image_tag']


class ProductLangugaeAdmin(admin.ModelAdmin):
    list_display = ['title', 'lang', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ['lang']


class CategoryLangugaeAdmin(admin.ModelAdmin):
    list_display = ['title', 'lang', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ['lang']


admin.site.register(Category, CategoryAdmin2)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Images, ImagesAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Variants, VariantsAdmin)
admin.site.register(ProductLang, ProductLangugaeAdmin)
admin.site.register(CategoryLang, CategoryLangugaeAdmin)
