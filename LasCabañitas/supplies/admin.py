from django.contrib import admin
from .models import cabin, items, supply, categoryItem

class supplyInLine(admin.TabularInline):
    model = supply
    extra = 0
    autocomplete_fields = ['item']

@admin.register(cabin)
class cabinAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = [supplyInLine]

@admin.register(items)
class itemsAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(categoryItem)
class categoryItemAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']