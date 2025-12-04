from datalogs.models import InventoryHistory, InventoryHistoryItem
from .models import supply, SupplyItem, BaseSupply, BaseSupplyItem

def actualizar_estados_inventario(sup):
    # Recalcula estados al guardar inventario y cambia cabaña a 'abasteciendo'.

    base_items = {
        bsi.item_id: bsi.quantity
        for bsi in BaseSupplyItem.objects.filter(base_supply__cabin=sup.cabin)
    }

    for item in sup.items.all():
        base_quantity = base_items[item.item_id]
        if item.quantity == 0:
            item.status = 'agotado'
        elif item.quantity < base_quantity:
            item.status = 'bajo'
        else:
            item.status = 'disponible'
        item.save()


def iniciar_abastecimiento_supplies(queryset):
    for sup in queryset:  
        for item in sup.items.all():  
            if item.status in ['agotado', 'bajo']:
                item.status = 'pendiente'
                item.save()
        sup.cabin.status = 'abasteciendo'
        sup.cabin.save()


def finalizar_abastecimiento_supplies(queryset):
    for sup in queryset:
        # Recalcular estados finales
        base_items = {
            bsi.item_id: bsi.quantity
            for bsi in BaseSupplyItem.objects.filter(base_supply__cabin=sup.cabin)
        }

        for item in sup.items.all():
            base_quantity = base_items.get(item.item_id, 0)
            if item.quantity == 0:
                item.status = 'agotado'
            elif item.quantity < base_quantity:
                item.status = 'bajo'
            else:
                item.status = 'disponible'
            item.save()

        # Cambiar estado de la cabaña
        sup.cabin.status = 'lista'
        sup.cabin.save()

        # Crear histórico independiente
        history = InventoryHistory.objects.create(cabin=sup.cabin)
        for item in sup.items.all():
            InventoryHistoryItem.objects.create(
                history=history,
                item=item.item,
                item_name=item.item.name,
                quantity=item.quantity,
                status=item.get_status_display()
            )

def iniciar_preparacion_supplies(queryset):
    for sup in queryset:
        sup.cabin.status = 'preparacion'
        sup.cabin.save()

def crear_inventario(cabin):
    # Verificar si ya existe un inventario activo para la cabaña
    existente = supply.objects.filter(cabin=cabin).order_by('-created_at').first()
    if existente:
        # Si ya existe, devolvemos ese inventario en lugar de crear uno nuevo
        return existente

    # Si no existe, crear uno nuevo desde el inventario base
    inv = supply.objects.create(cabin=cabin)
    base = BaseSupply.objects.filter(cabin=cabin).first()
    if base:
        for item in base.items.all():
            SupplyItem.objects.create(
                supply=inv,
                item=item.item,
                quantity=item.quantity
            )
    return inv