from django import template

register = template.Library()

@register.filter
def has_paid(announcement, member):
    """Check if a member has paid for a bereavement announcement"""
    return announcement.has_member_paid(member)