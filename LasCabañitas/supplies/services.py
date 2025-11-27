from datalogs.models import InventoryHistory, InventoryHistoryItem

def iniciar_abastecimiento_supplies(queryset):
    for sup in queryset:  
        for item in sup.items.all():  
            if item.status in ['agotado', 'bajo']:
                item.status = 'pendiente'
                item.save()


def finalizar_abastecimiento_supplies(queryset):
    for sup in queryset:
        for item in sup.items.all():
            if item.quantity == 0:
                item.status = 'agotado'
            elif item.quantity < item.item.base_quantity:
                item.status = 'bajo'
            else:
                item.status = 'disponible'
            item.save()

        history = InventoryHistory.objects.create(supply=sup)
        for item in sup.items.all():
            InventoryHistoryItem.objects.create(
                history=history,
                item_name=item.item.name,
                quantity=item.quantity,
                status=item.status
            )

def iniciar_preparacion_supplies(queryset):
    for sup in queryset:
        sup.cabin.status = 'preparacion'
        sup.cabin.save()