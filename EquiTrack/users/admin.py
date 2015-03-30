__author__ = 'jcranwellward'

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from import_export import resources
from import_export.admin import ImportExportMixin

from .models import UserProfile


class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserResource(resources.ModelResource):

    class Meta:
        model = User


class UserAdminPlus(ImportExportMixin, UserAdmin):
    resource_class = UserResource
    inlines = (ProfileInline,)


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'office',
        'section',
        'job_title',
        'phone_number',
    )
    list_editable = (
        'office',
        'section',
        'job_title',
        'phone_number',
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdminPlus)
admin.site.register(UserProfile, ProfileAdmin)