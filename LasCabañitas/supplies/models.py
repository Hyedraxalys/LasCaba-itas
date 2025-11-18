from django.db import models

class categoryItem(models.Model):
    name = models.CharField(max_length = 50, verbose_name = "Nombre de la categoría")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Categoria de insumo"
        verbose_name_plural = "Categoria de insumos"

class cabin(models.Model):
    name = models.CharField(max_length = 50, verbose_name = "Nombre de la cabaña")

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
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('pendiente', 'Pendiente'),
        {'agotado', 'Agotado'}
    ]

    cabin = models.ForeignKey(cabin, on_delete = models.CASCADE, verbose_name = "Cabaña")
    item = models.ForeignKey(items, on_delete = models.CASCADE, verbose_name = "Insumo")
    quantity = models.PositiveIntegerField(default = 0, verbose_name = "Cantidad")
    status = models.CharField(max_length = 10, choices = ESTADOS, default = 'disponible', verbose_name = "Estado")

    def __str__(self):
        return f"{self.item.name} en {self.cabin.name} ({self.quantity}, {self.get_status_display()})"
    
    class Meta:
        verbose_name = "Insumo de cabaña"
        verbose_name_plural = "Insumos de cabañas"
        unique_together = ('cabin', 'item')