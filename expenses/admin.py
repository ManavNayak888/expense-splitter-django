from django.contrib import admin
from .models import Group, Expense

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display= ['name', 'created_by', 'created_at']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display= ['description', 'amount', 'paid_by', 'group', 'date']