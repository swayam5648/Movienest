from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from navbar.models import User

class UserModelAdmin(BaseUserAdmin):
    model = User

    # Fields visible in List view
    list_display = ("id", "email", "name", "city", "is_active", "is_superuser", "is_staff")
    list_filter = ("is_superuser", "is_staff", "is_active")

    # Edit page for sections
    fieldsets = (
        ("User Credentials", {"fields": ("email", "password")}),
        ("Personal Information", {"fields": ("name", "city")}),
        ("Permissions", {"fields": ("is_active", "is_superuser", "is_staff")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    # Add sections for user form
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "city", "password1", "password2", "is_active", "is_staff", "is_superuser"),
        }),
    )
    search_fields = ("email", "name")
    ordering = ("email", "id")
    filter_horizontal = ()

# Register
admin.site.register(User, UserModelAdmin)
