from django.urls import path

from .views import (
    admin_dashboard_view,
    base_supply_detail_view,
    manager_dashboard_view,
    manager_inventory_detail_view,
    default_dashboard_view,
    supply_restock_detail_view,
    inventory_history_list_view,
    inventory_history_pdf_view,
)


urlpatterns = [
    # Dashboard administrador
    path("admin/", admin_dashboard_view, name="admin_dashboard"),

    # Vista detalle de inventario base (para ver/editar ítems)
    path("admin/base/<int:pk>/", base_supply_detail_view, name="base_supply_detail"),

    # Vista detalle de reabastecimiento de inventario de cabaña
    path("admin/restock/<int:pk>/", supply_restock_detail_view, name="supply_restock_detail"),

    # Histórico de inventarios
    path("admin/history/", inventory_history_list_view, name="inventory_history_list"),
    path("admin/history/<int:pk>/pdf/", inventory_history_pdf_view, name="inventory_history_pdf"),

    # Dashboard encargado
    path("manager/", manager_dashboard_view, name="manager_dashboard"),
    path("manager/inventory/<int:pk>/", manager_inventory_detail_view, name="manager_inventory_detail"),

    # Dashboard por defecto (otros roles)
    path("", default_dashboard_view, name="default_dashboard"),
]

