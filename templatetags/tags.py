import re

from django import template
from django.urls import reverse, NoReverseMatch
from table.models import User, Client, Portfolio

register = template.Library()

@register.simple_tag(takes_context=True)
def active_url(context, url):
    try:
        pattern = '^%s$' % reverse(url)
    except NoReverseMatch:
        pattern = url

    path = context['request'].path
    to_return = "active" if re.search(pattern, path) else ''
    return to_return

@register.simple_tag
def get_portfolios(user):
    if user.is_client:
        print('(Fetching client portfolios.)')
        return Portfolio.objects.filter(owner= user) # Client.objects.get(client_id= user.client.client_id).user)
    elif user.is_broker:
        print('(Fetching broker portfolios.)')
        return Portfolio.objects.filter(owner= user)
    elif user.is_company:
        print('(Fetching company portfolio.)')
        return Portfolio.objects.filter(owner= user)

