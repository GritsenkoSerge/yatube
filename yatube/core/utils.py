from django.conf import settings
from django.core.paginator import Page, Paginator


def get_page_obj(request, obj_list) -> Page:
    paginator = Paginator(obj_list, settings.ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
