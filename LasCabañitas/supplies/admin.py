from django.contrib import admin
from .models import cabin, items, supply, categoryItem

# PDF
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def generate_pdf(modeladmin, request, queryset):
    # Solo exportamos la primera cabaña seleccionada
    cabin = queryset.first()

    # Crear respuesta HTTP como PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="inventario_{cabin.name}.pdf"'

    # Crear PDF con ReportLab
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, f"Inventario de {cabin.name}")

    # Encabezados de tabla
    p.setFont("Helvetica-Bold", 12)
    y = height - 100
    p.drawString(100, y, "Insumo")
    p.drawString(300, y, "Cantidad")
    p.drawString(400, y, "Estado")

    # Filas de inventario
    p.setFont("Helvetica", 12)
    y -= 20
    for supply in cabin.supply_set.all():
        p.drawString(100, y, supply.item.name)
        p.drawString(300, y, str(supply.quantity))
        p.drawString(400, y, supply.get_status_display())
        y -= 20

    p.showPage()
    p.save()
    return response
generate_pdf.short_description = "Generar PDF de inventario de cabañas"

class supplyInLine(admin.TabularInline):
    model = supply
    extra = 0
    fields = ['item', 'quantity', 'status']
    autocomplete_fields = ['item']

@admin.register(cabin)
class cabinAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = [supplyInLine]
    actions = [generate_pdf]

@admin.register(items)
class itemsAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    search_fields = ['name']

@admin.register(categoryItem)
class categoryItemAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ('cabin', 'item', 'quantity', 'status')
    list_filter = ('cabin', 'status')