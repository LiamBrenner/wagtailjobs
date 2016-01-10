from wagtail.wagtailadmin.edit_handlers import (ObjectList,
                                                extract_panel_definitions_from_model_class)


def panel_perms(Job, request):
    panels = extract_panel_definitions_from_model_class(
        Job, exclude=['jobindex'])
    EditHandler = ObjectList(panels).bind_to_model(Job)
    return EditHandler
