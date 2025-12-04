from django.contrib import admin
from .models import InventoryHistory, InventoryHistoryItem

#PDF generation
from django.http import HttpResponse
from .pdf_utils import generar_inventario_pdf

def generate_pdf(modeladmin, request, queryset):
    history = queryset.first()   # ahora trabajamos con InventoryHistory
    if not history:
        return
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="inventario_{history.cabin.name}.pdf"'
    generar_inventario_pdf(history, response)   # pasamos el histórico
    return response
generate_pdf.short_description = "Generar PDF de inventario de cabañas"

class InventoryHistoryItemInline(admin.TabularInline):
    model = InventoryHistoryItem
    extra = 0
    readonly_fields = ['item_name', 'quantity', 'status']

@admin.register(InventoryHistory)
class InventoryHistoryAdmin(admin.ModelAdmin):
    list_display = ['cabin', 'created_at']   # supply ya no existe
    search_fields = ['cabin__name']
    inlines = [InventoryHistoryItemInline]
    actions = [generate_pdf]

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return True