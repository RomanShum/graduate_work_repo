from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, Value
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.http import Http404

from movies_together.models import FilmWork, Roles


class MoviesMixin:
    PAGINATE = 50
    model = FilmWork
    http_method_names = ['get']

    def get_queryset(self):
        return FilmWork.objects.all().values("id", "title", "description",
                                             "creation_date", "rating",
                                             "type") \
            .annotate(genres=ArrayAgg('genres__name', distinct=True)) \
            .annotate(actors=ArrayAgg(
                'persons__full_name',
                distinct=True,
                filter=Q(personfilmwork__role=Roles.ACTOR),
                default=Value([]))) \
            .annotate(directors=ArrayAgg(
                'persons__full_name', distinct=True,
                filter=Q(personfilmwork__role=Roles.DIRECTOR),
                default=Value([]))) \
            .annotate(writers=ArrayAgg(
                'persons__full_name',
                distinct=True,
                filter=Q(personfilmwork__role=Roles.WRITER),
                default=Value([])))

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesMixin, BaseListView):

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = \
            self.paginate_queryset(queryset, self.PAGINATE)
        context = {
            'count': paginator.count,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'results': list(queryset),
            'next': page.next_page_number() if page.has_next() else None,
            'total_pages': paginator.num_pages
        }
        return context


class MoviesDetailApi(MoviesMixin, BaseListView):

    def get_context_data(self):
        detail_data = self.get_queryset().get(id=self.kwargs.get('pk'))
        if not detail_data:
            raise Http404("Фильм не найден")
        return detail_data
