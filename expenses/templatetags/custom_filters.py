from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Template filter to get dictionary value by key"""
    return dictionary.get(key)

@register.filter
def can_manage_members(group, user):
    """Template filter to check if user can manage group members"""
    return group.can_manage_members(user)