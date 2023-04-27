from django.core.paginator import Paginator

from .models import POSTS_ON_THE_PAGE


def get_paginator(posts, request):
    paginator = Paginator(posts, POSTS_ON_THE_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
