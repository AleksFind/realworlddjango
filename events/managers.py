from django.db import models
from django.db.models.functions import Coalesce


class EventQuerySet(models.QuerySet):
    def with_counts(self):
        return self.annotate(
            count=Coalesce(models.Count('enrolls', distinct=True), 0),
        )

    def event_qs(self):
        return self.select_related(
            'category',
        ).prefetch_related(
            'enrolls__user',
            'features',
            'reviews__user',
        ).with_counts()

    def event_qs1(self):
        return self.select_related(
            'category',
        ).prefetch_related(
            'features',
        ).with_counts()
