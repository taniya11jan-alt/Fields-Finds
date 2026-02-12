from django.contrib import admin
from .models import Profile, Tool, Booking

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'district', 'pincode', 'is_verified') # [cite: 189, 191]
    list_filter = ('is_verified', 'district') # [cite: 28]

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'price_per_day', 'is_approved') # [cite: 52-53]
    list_filter = ('is_approved', 'category') # [cite: 29]
    actions = ['approve_tools']

    def approve_tools(self, request, queryset):
        queryset.update(is_approved=True)
    approve_tools.short_description = "Approve selected tools for listing"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('tool', 'borrower', 'status', 'start_date', 'end_date') # [cite: 67, 100]
    list_filter = ('status',) # [cite: 31]