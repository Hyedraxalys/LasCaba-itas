from django.db import models

class categoryItem(models.Model):
    name = models.CharField(max_length = 50, verbose_name = "Nombre de la categoría")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "3. Categoria de insumo"
        verbose_name_plural = "3. Categoria de insumos"

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
        verbose_name = "1. Cabaña"
        verbose_name_plural = "1. Cabañas"

class items(models.Model):
    name = models.CharField(max_length = 50, verbose_name="Nombre del insumo")
    category = models.ForeignKey(categoryItem, on_delete = models.CASCADE, null = True, blank = True, verbose_name = "Categoría")
    base_quantity = models.PositiveIntegerField(default = 1, verbose_name = "Cantidad Base")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "2. Insumo"
        verbose_name_plural = "2. Insumos"

class supply(models.Model):
    cabin = models.ForeignKey(cabin, on_delete=models.PROTECT, verbose_name="Cabaña")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inventario de {self.cabin.name} ({self.created_at.date()})"
    
    class Meta:
        verbose_name = "4. Inventario de cabaña"
        verbose_name_plural = "4. Inventarios de cabañas"

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

    def save(self, *args, **kwargs):
        if self.status != 'pendiente':
            if self.quantity == 0:
                self.status = 'agotado'
            elif self.quantity < self.item.base_quantity:
                self.status = 'bajo'
            else:
                self.status = 'disponible'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} ({self.quantity}, {self.get_status_display()})"
    
    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Inventario"
    
