from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PatientProfile, ClinicianProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ('username','email','first_name','last_name','role','is_active')
    list_filter   = ('role','is_active')
    fieldsets     = UserAdmin.fieldsets + (('Role', {'fields': ('role',)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('Role', {'fields': ('role',)}),)

admin.site.register(PatientProfile)


@admin.register(ClinicianProfile)
class ClinicianProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'can_view_all_patients')
    list_filter = ('can_view_all_patients',)
