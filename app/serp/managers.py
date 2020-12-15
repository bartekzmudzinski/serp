from django.conf import settings
from django.db import models
from django.utils.timezone import now, timedelta

from .helpers import extract_ip_address


class SearchQuerySet(models.QuerySet):

    def active(self):
        expiration_time = now() - timedelta(minutes=settings.SEARCH_CACHE_TIMEOUT)
        return self.filter(created_at__gt=expiration_time)

    def get_from_cache(self, query, request):
        ip = extract_ip_address(request)
        return self.active().get(ip=ip, query__exact=query)


class SearchRequestsManager(models.Manager):
    def get_queryset(self):
        return SearchQuerySet(self.model, using=self._db).order_by('id')

    def active(self):
        return self.get_queryset().active()

    def get_from_cache(self, query, request):
        return self.get_queryset().get_from_cache(query, request)
