from django.db import models
from django.utils import timezone

class categoryItem(models.Model):
    name = models.CharField(max_length = 50, verbose_name = "Nombre de la categoría")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Categoria de insumo"
        verbose_name_plural = "Categoria de insumos"

class cabin(models.Model):
    ESTADOS = [
        ('lista', 'Lista'),
        ('abasteciendo', 'En Abastecimiento'),
        ('preparacion', 'En Preparacion'),
        ('disponible', 'Disponible')
    ]
    name = models.CharField(max_length = 50, verbose_name = "Nombre de la cabaña")
    status = models.CharField(max_length = 50, choices = ESTADOS, default = 'disponible', verbose_name = 'Estado')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Cabaña"
        verbose_name_plural = "Cabañas"

class items(models.Model):
    name = models.CharField(max_length = 50, verbose_name="Nombre del insumo")
    category = models.ForeignKey(categoryItem, on_delete = models.CASCADE, null = True, blank = True, verbose_name = "Categoría")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"

class supply(models.Model):
    cabin = models.ForeignKey("cabin", on_delete=models.PROTECT, verbose_name="Cabaña")
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=150, editable=False, verbose_name="Nombre del inventario")

    def save(self, *args, **kwargs):
        fecha = timezone.localtime(self.created_at or timezone.now()).strftime("%Y-%m-%d")
        self.name = f"{self.cabin.name} - Inventario - {fecha}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Inventario de cabaña"
        verbose_name_plural = "Inventarios de cabañas"
        
class SupplyItem(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('bajo', 'Bajo stock'),
        ('pendiente', 'Pendiente'),
        ('agotado', 'Agotado'),
    ]

    supply = models.ForeignKey(supply, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(items, on_delete=models.CASCADE, verbose_name="Insumo")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Cantidad")
    status = models.CharField(max_length=10, choices=ESTADOS, default='disponible', verbose_name="Estado")

    def __str__(self):
        return f"{self.item.name} ({self.quantity}, {self.get_status_display()})"
    
    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Inventario"
        verbose_name_plural = "Inventario"
    
class BaseSupply(models.Model):
    cabin = models.ForeignKey("cabin", on_delete=models.PROTECT, verbose_name="Cabaña")
    name = models.CharField(max_length=100, verbose_name="Nombre del inventario base", editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.name:  # solo si no se definió manualmente
            fecha = timezone.localtime(self.created_at or timezone.now()).strftime("%Y-%m-%d")
            self.name = f"{self.cabin.name} - Inventario base - {fecha}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Inventario base"
        verbose_name_plural = "Inventarios base"

class BaseSupplyItem(models.Model):
    base_supply = models.ForeignKey(BaseSupply, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey("items", on_delete=models.CASCADE, verbose_name="Insumo")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Cantidad")

    def __str__(self):
        return f"{self.item.name} ({self.quantity})"
