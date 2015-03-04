from citizengrid.models import Branch, Category,SubCategory

from django import template

register = template.Library()

@register.inclusion_tag("cg_select_template.html")

def branch_model_select():
    branch_list =  Branch.objects.all()
    return {'branch_list':branch_list}