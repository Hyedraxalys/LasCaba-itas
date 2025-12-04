from django.db import models
from supplies.models import cabin, items

class InventoryHistory(models.Model):
    cabin = models.ForeignKey("supplies.Cabin", on_delete=models.PROTECT, related_name="inventory_histories", null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Registro de {self.cabin.name} ({self.created_at.strftime('%d-%m-%Y %H:%M')})"

    class Meta:
        verbose_name = "Registro de inventario"
        verbose_name_plural = "Históricos de inventarios"


class InventoryHistoryItem(models.Model):
    history = models.ForeignKey(InventoryHistory, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey("supplies.items", on_delete=models.PROTECT, null=True, blank=True)
    item_name = models.CharField(max_length=50) 
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20)     

    def __str__(self):
        return f"{self.item_name} ({self.quantity}) - {self.status}"

    class Meta:
        verbose_name = "Insumo registro"
        verbose_name_plural = "Insumos registro"