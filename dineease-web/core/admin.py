from django.contrib import admin
from .models import Restaurant, Promo, Menu, RestaurantImage, AddonCategory, AddonOption, Category, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.gis.db import models as geo_models
from mapwidgets.widgets import MapboxPointFieldWidget

class MapAdmin(admin.ModelAdmin):
    formfield_overrides = {
        geo_models.PointField: {"widget": MapboxPointFieldWidget(attrs={
            "map_height": "500px",  # Set map height
            "map_width": "100%",  # Set map width
        })},
    }

# Inline for restaurant images
class RestaurantImageInline(admin.TabularInline):
    model = RestaurantImage
    extra = 1
    fields = ('image', 'caption')

    # Ensure only images related to the restaurant are shown
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(restaurant__isnull=False)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'description')
    list_filter = ('category_type',)
    search_fields = ('name',)

@admin.register(Restaurant)
class RestaurantAdmin(MapAdmin, admin.ModelAdmin):
    list_display = ('name', 'location', 'owner', 'status')
    inlines = [RestaurantImageInline]
    search_fields = ['name']

# Inline for menu images
class MenuImageInline(admin.TabularInline):
    model = RestaurantImage
    extra = 1
    fields = ('image', 'caption')

    # Ensure only images related to the menu are shown
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(menu__isnull=False)

class AddonOptionInline(admin.TabularInline):
    model = AddonOption
    extra = 1  # One extra form for options
    fields = ('name', 'price', 'menu_item')

# Inline for addon categories (used in MenuAdmin)
class AddonCategoryInline(admin.TabularInline):
    model = AddonCategory
    extra = 2  # Display one extra blank form for categories
    inlines = [AddonOptionInline]  # Allow adding options inside categories

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        if obj:
            # Only show options for an existing category
            inline_instances += [AddonOptionInline(self.model, self.admin_site)]
        return inline_instances

class PromoInline(admin.TabularInline):
    model = Promo
    extra = 1
    fields = ('name', 'description', 'discount', 'discount_type', 'status', 'restaurant', 'start_date', 'end_date')

# Admin for Menu
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    inlines = [MenuImageInline, AddonCategoryInline, PromoInline]  # Add categories and options in MenuAdmin
    list_display = ('name', 'restaurant', 'cost', 'status')
    search_fields = ['name']

# Admin for Promo
class PromoAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'discount', 'status')
    search_fields = ['name']

# Admin for RestaurantImage
@admin.register(RestaurantImage)
class RestaurantImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'image')
    search_fields = ('caption',)

# Admin for AddonCategory (if you want to manage categories independently)
@admin.register(AddonCategory)
class AddonCategoryAdmin(admin.ModelAdmin):
    inlines = [AddonOptionInline]  # Allow adding options directly in AddonCategoryAdmin
    list_display = ('name', 'menu', 'required', 'max_selections')
    search_fields = ['name']

# Register Promo admin separately
admin.site.register(Promo, PromoAdmin)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fields = ['email', 'type_of_user', 'phone', 'address', 'city', 'image']

# Define a new User admin
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

    # Display email and type of user in user list
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_type_of_user')
    
    def get_type_of_user(self, obj):
        return obj.profile.type_of_user
    get_type_of_user.short_description = 'User Type'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
