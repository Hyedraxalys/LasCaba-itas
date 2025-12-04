from django.contrib import admin
from django.contrib import messages
from .models import (cabin, 
                     items, 
                     supply, 
                     categoryItem, 
                     SupplyItem,
                     BaseSupply,
                     BaseSupplyItem
                     )
from .services import ( iniciar_abastecimiento_supplies, 
                        finalizar_abastecimiento_supplies, 
                        iniciar_preparacion_supplies,
                        crear_inventario,
                        actualizar_estados_inventario
                    )

def iniciar_abastecimiento(modeladmin, request, queryset):
    iniciar_abastecimiento_supplies(queryset)
    for sup in queryset:
        modeladmin.message_user(request, f"Cabaña {sup.cabin.name} ahora en abastecimiento.")
iniciar_abastecimiento.short_description = "Iniciar abastecimiento"

def iniciar_preparacion(modeladmin, request, queryset):
    iniciar_preparacion_supplies(queryset)
iniciar_preparacion.short_description = "Iniciar preparacion"

def finalizar_abastecimiento(modeladmin, request, queryset):
    # Verificar diferencias con inventario base
    problemas = []
    for sup in queryset:
        base_items = {
            bsi.item_id: bsi.quantity
            for bsi in BaseSupplyItem.objects.filter(base_supply__cabin=sup.cabin)
        }
        for item in sup.items.all():
            base_quantity = base_items.get(item.item_id, 0)
            if item.quantity < base_quantity:
                problemas.append(f"{sup.cabin.name} - {item.item.name}: {item.quantity} (base {base_quantity})")

    # Mostrar warning si hay problemas, pero continuar
    if problemas:
        modeladmin.message_user(
            request,
            "Advertencia: algunos ítems tienen menos cantidad que la base:\n" + "\n".join(problemas),
            level=messages.WARNING
        )

    # Ejecutar igualmente la finalización
    finalizar_abastecimiento_supplies(queryset)
    for sup in queryset:
        modeladmin.message_user(request, f"Reabastecimiento finalizado para {sup.cabin.name}, cabaña lista.")
finalizar_abastecimiento.short_description = "Finalizar abastecimiento"

class SupplyItemInline(admin.TabularInline):
    model = SupplyItem
    extra = 0
    fields = ['item', 'quantity', 'base_quantity_ref', 'status']
    autocomplete_fields = ['item']
    readonly_fields = ('status', 'base_quantity_ref')

    def has_add_permission(self, request, obj=None):
        # No permitir agregar ítems manualmente
        return False

    def has_delete_permission(self, request, obj=None):
        # No permitir borrar ítems
        return False
    
    def base_quantity_ref(self, obj):
        # Buscar cantidad base desde el inventario base de la cabaña
        try:
            base_item = BaseSupplyItem.objects.get(
                base_supply__cabin=obj.supply.cabin,
                item=obj.item
            )
            return base_item.quantity
        except BaseSupplyItem.DoesNotExist:
            return "-"
    base_quantity_ref.short_description = "Cantidad base"

class BaseSupplyItemInline(admin.TabularInline):
    model = BaseSupplyItem
    extra = 0

@admin.register(cabin)
class CabinAdmin(admin.ModelAdmin):
    list_display = ["name", "status"]


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
    actions = [iniciar_abastecimiento, iniciar_preparacion, finalizar_abastecimiento]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        # Recalcular estados si la cabaña está en preparación
        if form.instance.cabin.status == 'preparacion':
            actualizar_estados_inventario(form.instance)
            self.message_user(
                request,
                f"Inventario actualizado para {form.instance.cabin.name} (fase de preparación)."
            )

    def has_add_permission(self, request):
        # Bloquear creación manual desde el admin
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Bloquear borrado manual desde el admin
        return True

@admin.register(BaseSupply)
class BaseSupplyAdmin(admin.ModelAdmin):
    list_display = [ "name", "cabin", "created_at"]
    inlines = [BaseSupplyItemInline]
    actions = ["crear_inventario_action"]

    def crear_inventario_action(self, request, queryset):
        for base in queryset:
            inv = crear_inventario(base.cabin)
            messages.success(request, f"Inventario creado para {base.cabin.name}: {inv.name}")
    crear_inventario_action.short_description = "Crear inventario desde inventario base"

