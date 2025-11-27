from django.contrib import admin
from .models import InventoryHistory, InventoryHistoryItem

#PDF generation
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

class InventoryHistoryItemInline(admin.TabularInline):
    model = InventoryHistoryItem
    extra = 0
    readonly_fields = ['item_name', 'quantity', 'status']

@admin.register(InventoryHistory)
class InventoryHistoryAdmin(admin.ModelAdmin):
    list_display = ['supply', 'created_at']
    search_fields = ['supply__cabin__name']
    inlines = [InventoryHistoryItemInline]
    actions = [generate_pdf]

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return True