from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from django.core.exceptions import PermissionDenied

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'currency', 'balance')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'currency', 'balance', 'is_active', 'is_staff', 'is_superuser')

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ('username', 'email', 'first_name', 'last_name', 'currency', 'balance')
    list_filter = ('currency', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)

    # Fields for adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'currency', 'balance', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    # Fields for changing an existing user
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'currency', 'balance')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if obj:
            readonly_fields = ['username', 'email']
            if not request.user.is_superuser:  # Only superusers can edit balance
                readonly_fields.append('balance')
        return readonly_fields

    # Restrict changes to superusers
    def has_change_permission(self, request, obj=None):
        if obj and 'balance' in request.POST and not request.user.is_superuser:
            raise PermissionDenied("Only superusers can change the balance.")
        return super().has_change_permission(request, obj)

    #Log balance changes
    def save_model(self, request, obj, form, change):
        if change and 'balance' in form.changed_data and not request.user.is_superuser:
            raise PermissionDenied("Only superusers can change the balance.")
        super().save_model(request, obj, form, change)