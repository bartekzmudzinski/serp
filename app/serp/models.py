from django.contrib.postgres.fields import ArrayField
from django.db import models

from .managers import SearchRequestsManager


class SearchRequest(models.Model):
    query = models.CharField(max_length=200)
    results = models.IntegerField()
    most_common_words = ArrayField(
        models.CharField(max_length=25),
        default=list,
    )
    ip = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    objects = SearchRequestsManager()

    class Meta:
        ordering = ('-created_at',)


class Resusult(models.Model):
    request = models.ForeignKey(
        SearchRequest,
        related_name='search_results',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=1000)
    link = models.URLField()
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('order',)
