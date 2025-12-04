from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

def generar_inventario_pdf(history, response):
    # Crear documento
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    # Estilos básicos
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']

    # Título con cabaña y fecha de finalización
    elements.append(Paragraph(
        f"Inventario de {history.cabin.name} (finalizado {history.created_at.strftime('%d-%m-%Y %H:%M')})",
        title_style
    ))
    elements.append(Spacer(1, 20))

    # Encabezados de tabla
    data = [["Insumo", "Cantidad", "Estado"]]

    # Filas de inventario desde el histórico
    for item in history.items.all():
        data.append([
            item.item_name,
            str(item.quantity),
            item.status
        ])

    # Crear tabla
    table = Table(data, colWidths=[200, 100, 150])

    # Estilos de tabla
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f2f2f2")),  # encabezado gris
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),  # bordes
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),  # filas
    ]))

    elements.append(table)

    # Construir PDF
    doc.build(elements)