def get_user_role(user):
    groups = list(user.groups.values_list("name", flat=True))

    if "Administrador" in groups:
        return "Administrador"
    elif "Encargado de preparación de cabañas" in groups:
        return "Encargado"
    else:
        return None  # sin rol asignado
