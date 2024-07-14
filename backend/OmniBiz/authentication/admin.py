from django.contrib import admin

from authentication.models import StaffAccess, HigherStaffUser, HigherStaffAccess

admin.site.register([StaffAccess, HigherStaffUser, HigherStaffAccess])
