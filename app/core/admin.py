from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
# recommended convention for
# coverting strings to human readable text to get it passed through translation
# engine and later will be easier to extend in multiple language

from core import models


class UserAdmin(BaseUserAdmin):  # extend baseuseradmin
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # first field is titlte of
        # the section
        (_('Personal Info'), {'fields': ('name',)}),  # create personal info
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    # edit the field sets for the add user page
    add_fieldsets = (
        (None, {  # {} means opening a dictionary here
            'classes': ('wide',),  # classes assigned to the form, default is
            # wide class
            'fields': ('email', 'password1', 'password2')
        }),  # the ',' should be here,otherwise python would consider as object
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Category)  # do not need the UserAdmin as we are
admin.site.register(models.Supply)
admin.site.register(models.Painting)
# using a basic model of read, update and delete here
