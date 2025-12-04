from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from supplies.models import cabin, BaseSupply, BaseSupplyItem, items, supply, SupplyItem
from supplies.services import crear_inventario, iniciar_preparacion_supplies, finalizar_abastecimiento_supplies
from datalogs.models import InventoryHistory
from datalogs.pdf_utils import generar_inventario_pdf
from django.http import HttpResponse

@login_required
@role_required("Encargado")
def manager_dashboard_view(request):
    # Mostrar cabañas en estado de preparación
    prep_cabins = cabin.objects.filter(status="preparacion")
    supplies = supply.objects.filter(cabin__in=prep_cabins)
    return render(request, "dashboard/manager_dashboard.html", {
        "username": request.user.username,
        "prep_cabins": prep_cabins,
        "supplies": supplies,
    })

# Vista para realizar inventario de cabaña en preparación
@login_required
@role_required("Encargado")
def manager_inventory_detail_view(request, pk):
    sup = get_object_or_404(supply, pk=pk)
    supply_items = list(sup.items.all())
    for item in supply_items:
        base_item = BaseSupplyItem.objects.filter(
            base_supply__cabin=sup.cabin, item=item.item
        ).first()
        item.base_quantity = base_item.quantity if base_item else 0

    errors = []
    if request.method == "POST" and "finalize_inventory" in request.POST:
        new_values = {}
        for item in supply_items:
            field_name = f"quantity_{item.id}"
            raw_value = request.POST.get(field_name)
            base_quantity = getattr(item, "base_quantity", 0)
            try:
                new_qty = int(raw_value)
                if new_qty < 0:
                    errors.append(f"Cantidad negativa en {item.item.name}")
                else:
                    new_values[item.id] = new_qty
            except (TypeError, ValueError):
                errors.append(f"Valor inválido en {item.item.name}")
        if not errors:
            # Guardar cantidades
            for item in supply_items:
                item.quantity = new_values[item.id]
                item.save()
            # Actualizar estados y pasar a abastecimiento
            from supplies.services import actualizar_estados_inventario, iniciar_abastecimiento_supplies
            actualizar_estados_inventario(sup)
            iniciar_abastecimiento_supplies([sup])
            return redirect("manager_dashboard")
    return render(request, "dashboard/manager_inventory_detail.html", {
        "username": request.user.username,
        "supply": sup,
        "supply_items": supply_items,
        "errors": errors,
    })


# Vista para listar históricos de inventarios
@login_required
@role_required("Administrador")
def inventory_history_list_view(request):
    histories = InventoryHistory.objects.select_related('cabin').order_by('-created_at')
    return render(request, 'dashboard/inventory_history_list.html', {
        'histories': histories,
    })

# Vista para generar PDF de un histórico
@login_required
@role_required("Administrador")
def inventory_history_pdf_view(request, pk):
    history = get_object_or_404(InventoryHistory, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="inventario_{history.cabin.name}_{history.created_at.strftime('%Y%m%d_%H%M')}.pdf"'
    generar_inventario_pdf(history, response)
    return response

@login_required
@role_required("Administrador")
def supply_restock_detail_view(request, pk):
    sup = get_object_or_404(supply, pk=pk)
    # Asignar base_quantity a cada item
    supply_items = list(sup.items.all())
    for item in supply_items:
        base_item = BaseSupplyItem.objects.filter(
            base_supply__cabin=sup.cabin, item=item.item
        ).first()
        item.base_quantity = base_item.quantity if base_item else 0

    if request.method == "POST" and "save_restock" in request.POST:
        errors = []
        new_values = {}
        for item in supply_items:
            field_name = f"quantity_{item.id}"
            raw_value = request.POST.get(field_name)
            base_quantity = getattr(item, "base_quantity", 0)
            try:
                new_qty = int(raw_value)
                if new_qty < 0:
                    errors.append(f"Cantidad negativa en {item.item.name}")
                elif new_qty > base_quantity:
                    errors.append(
                        f"{item.item.name}: no puede superar la cantidad base ({base_quantity})"
                    )
                else:
                    new_values[item.id] = new_qty
            except (TypeError, ValueError):
                errors.append(f"Valor inválido en {item.item.name}")
        if errors:
            return render(request, "dashboard/supply_restock_detail.html", {
                "username": request.user.username,
                "supply": sup,
                "errors": errors,
            })
        # Guardar y finalizar reabastecimiento
        for item in supply_items:
            item.quantity = new_values[item.id]
            item.save()
        finalizar_abastecimiento_supplies([sup])
        return redirect("admin_dashboard")

    return render(request, "dashboard/supply_restock_detail.html", {
        "username": request.user.username,
        "supply": sup,
        "supply_items": supply_items,
    })


@login_required
@role_required("Administrador")
def admin_dashboard_view(request):
    cabins = cabin.objects.all()
    abasteciendo_cabins = cabin.objects.filter(status="abasteciendo")
    base_supplies = BaseSupply.objects.all()
    abasteciendo_supplies = supply.objects.filter(
        cabin__status="abasteciendo"
    ).prefetch_related("items__item")

    # 🔧 Anotar cada SupplyItem con su cantidad base
    for sup in abasteciendo_supplies:
        for item in sup.items.all():
            base_item = BaseSupplyItem.objects.filter(
                base_supply__cabin=sup.cabin, item=item.item
            ).first()
            item.base_quantity = base_item.quantity if base_item else 0

    # Acción: preparar cabaña
    if request.method == "POST" and "prepare_cabin" in request.POST:
        cab_id = request.POST.get("prepare_cabin")
        cab = get_object_or_404(cabin, pk=cab_id)
        inv = crear_inventario(cab)
        iniciar_preparacion_supplies([inv])
        return redirect("admin_dashboard")

    # Acción: guardar en lote los ítems editados de un supply en abastecimiento
    if request.method == "POST" and "save_supply" in request.POST:
        sup_id = request.POST.get("save_supply")
        sup = get_object_or_404(supply, pk=sup_id)


        # Recalcular base_quantity para este supply (asegura que todos los items tengan base_quantity)
        supply_items = list(sup.items.all())
        for item in supply_items:
            base_item = BaseSupplyItem.objects.filter(
                base_supply__cabin=sup.cabin, item=item.item
            ).first()
            item.base_quantity = base_item.quantity if base_item else 0


        errors = []
        new_values = {}

        for item in supply_items:
            field_name = f"quantity_{item.id}"
            raw_value = request.POST.get(field_name)
            base_quantity = getattr(item, "base_quantity", 0)

            try:
                new_qty = int(raw_value)
                if new_qty < 0:
                    errors.append(f"Cantidad negativa en {item.item.name}")
                elif new_qty > base_quantity:
                    errors.append(
                        f"{item.item.name}: no puede superar la cantidad base ({base_quantity})"
                    )
                else:
                    new_values[item.id] = new_qty
            except (TypeError, ValueError):
                errors.append(f"Valor inválido en {item.item.name}")

        if errors:
            # Recalcular base_quantity para todos los abasteciendo_supplies
            for sup in abasteciendo_supplies:
                for item in sup.items.all():
                    base_item = BaseSupplyItem.objects.filter(
                        base_supply__cabin=sup.cabin, item=item.item
                    ).first()
                    item.base_quantity = base_item.quantity if base_item else 0

            return render(request, "dashboard/admin_dashboard.html", {
                "username": request.user.username,
                "cabins": cabins,
                "base_supplies": base_supplies,
                "abasteciendo_supplies": abasteciendo_supplies,
                "errors": errors,
            })

        # Guardar y finalizar abastecimiento
        for item in sup.items.all():
            item.quantity = new_values[item.id]
            item.save()

        finalizar_abastecimiento_supplies([sup])
        return redirect("admin_dashboard")

    return render(request, "dashboard/admin_dashboard.html", {
        "username": request.user.username,
        "cabins": cabins,
        "base_supplies": base_supplies,
        "abasteciendo_supplies": abasteciendo_supplies,
        "abasteciendo_cabins": abasteciendo_cabins,
    })

@login_required
@role_required("Administrador")
def base_supply_detail_view(request, pk):
    base_supply = get_object_or_404(BaseSupply, pk=pk)

    # Acción: editar item existente
    if request.method == "POST" and "edit_base_item" in request.POST:
        item_id = request.POST.get("edit_base_item")
        new_quantity = request.POST.get("quantity")
        base_item = get_object_or_404(BaseSupplyItem, pk=item_id)
        base_item.quantity = new_quantity
        base_item.save()
        return redirect("base_supply_detail", pk=base_supply.pk)

    # Acción: agregar nuevo item
    if request.method == "POST" and "add_base_item" in request.POST:
        item_id = request.POST.get("item_id")
        quantity = request.POST.get("quantity")
        item = get_object_or_404(items, pk=item_id)
        BaseSupplyItem.objects.create(
            base_supply=base_supply,
            item=item,
            quantity=quantity
        )
        return redirect("base_supply_detail", pk=base_supply.pk)
    
    # Acción: eliminar item
    if request.method == "POST" and "delete_base_item" in request.POST:
        item_id = request.POST.get("delete_base_item")
        base_item = get_object_or_404(BaseSupplyItem, pk=item_id)
        base_item.delete()
        return redirect("base_supply_detail", pk=base_supply.pk)

    return render(request, "dashboard/base_supply_detail.html", {
        "username": request.user.username,
        "base_supply": base_supply,
        "items": base_supply.items.all(),
        "all_items": items.objects.all(), 
    })

@login_required
def default_dashboard_view(request):
    return render(request, "dashboard/default_dashboard.html", {"username": request.user.username})
