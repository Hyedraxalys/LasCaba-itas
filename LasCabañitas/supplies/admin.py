from django.contrib import admin
from .models import cabin, items, supply, categoryItem, SupplyItem
from .services import iniciar_abastecimiento_supplies, finalizar_abastecimiento_supplies, iniciar_preparacion_supplies

def iniciar_abastecimiento(modeladmin, request, queryset):
    iniciar_abastecimiento_supplies(queryset)
iniciar_abastecimiento.short_description = "Marcar abastecimiento en curso"

def iniciar_preparacion(modeladmin, request, queryset):
    iniciar_preparacion_supplies(queryset)
iniciar_preparacion.short_description = "Iniciar preparacion"

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
    actions = [iniciar_abastecimiento, iniciar_preparacion]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        pending_items = obj.items.filter(status='pendiente')
        if pending_items.exists():
            finalizar_abastecimiento_supplies([obj])
            self.message_user(request, f"Reabastecimiento finalizado para {obj.cabin.name}")
    
    def get_actions(self, request):
        return super().get_actions(request)

        #if not 

