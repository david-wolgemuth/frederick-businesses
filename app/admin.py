from django.contrib import admin
from django.urls import reverse

from app import models


admin.site.site_header = "Frederick Business Admin"


def link_to_admin_instance(model):
    def instance_link(obj):
        url = reverse('admin:%s_%s_changelist' % (model._meta.app_label,  model._meta.model_name),  args=[obj.id] )
        return f'<a href="{url}">{obj}</a>'
    return instance_link


def get_all_fields(model):
    fields = []
    for field in model._meta.get_fields():
        if field.many_to_many:
            continue
        elif field.one_to_many:
            continue
        # elif field.many_to_one:
        #     fields.append(link_to_admin_instance(field.related_model))
        else:
            fields.append(field.name)
    return fields


@admin.register(models.Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = get_all_fields(models.Address)


@admin.register(models.BusinessCategory)
class BusinessCategoryAdmin(admin.ModelAdmin):
    list_display = get_all_fields(models.BusinessCategory)


@admin.register(models.Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = get_all_fields(models.Business)
    search_fields = [
        "name",
        "slug",
    ]


@admin.register(models.SocialMediaLink)
class SocialMediaLinkAdmin(admin.ModelAdmin):
    list_display = get_all_fields(models.SocialMediaLink)
