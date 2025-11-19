from django.contrib import admin
from .models import cabin, items, supply, categoryItem, SupplyItem, InventoryHistory, InventoryHistoryItem
from .services import iniciar_abastecimiento_supplies, finalizar_abastecimiento_supplies

# PDF
from django.contrib import admin
from django.http import HttpResponse
from .pdf_utils import generar_inventario_pdf

def generate_pdf(modeladmin, request, queryset):
    supply_obj = queryset.first()
    if not supply_obj:
        return
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="inventario_{supply_obj.cabin.name}.pdf"'
    generar_inventario_pdf(supply_obj, response)
    return response
generate_pdf.short_description = "Generar PDF de inventario de cabañas"

def iniciar_abastecimiento(modeladmin, request, queryset):
    iniciar_abastecimiento_supplies(queryset)
iniciar_abastecimiento.short_description = "Marcar abastecimiento en curso"

class SupplyItemInline(admin.TabularInline):
    model = SupplyItem
    extra = 0
    fields = ['item', 'quantity', 'status']
    autocomplete_fields = ['item']
    readonly_fields = ('status',)

@admin.register(cabin)
class cabinAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(items)
class itemsAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    search_fields = ['name']

@admin.register(categoryItem)
class categoryItemAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(supply)
class supplyAdmin(admin.ModelAdmin):
    list_display = ['cabin', 'created_at']
    search_fields = ['cabin__name']
    inlines = [SupplyItemInline]
    actions = [generate_pdf, iniciar_abastecimiento]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        pending_items = obj.items.filter(status='pendiente')
        if pending_items.exists():
            finalizar_abastecimiento_supplies([obj])
            self.message_user(request, f"Reabastecimiento finalizado para {obj.cabin.name}")

class InventoryHistoryItemInline(admin.TabularInline):
    model = InventoryHistoryItem
    extra = 0
    readonly_fields = ['item_name', 'quantity', 'status']

@admin.register(InventoryHistory)
class InventoryHistoryAdmin(admin.ModelAdmin):
    list_display = ['supply', 'created_at']
    search_fields = ['supply__cabin__name']
    inlines = [InventoryHistoryItemInline]

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return True