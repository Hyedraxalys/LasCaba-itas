from django.db import models
from supplies.models import supply

class InventoryHistory(models.Model):
    supply = models.ForeignKey(supply, on_delete=models.CASCADE, related_name="history")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Registro de {self.supply.cabin.name} ({self.created_at.date()})"

    class Meta:
        verbose_name = "Registro de inventario"
        verbose_name_plural = "Históricos de inventarios"


class InventoryHistoryItem(models.Model):
    history = models.ForeignKey(InventoryHistory, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=10)

    def __str__(self):
        return ""

    class Meta:
        verbose_name = "Insumo registro"
        verbose_name_plural = "Insumos registro"