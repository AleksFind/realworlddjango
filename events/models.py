from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.
class Feature(models.Model):
    title = models.CharField(max_length=90, blank=True, default='', verbose_name='Свойство события')

    class Meta:
        verbose_name = 'Свойство'
        verbose_name_plural = 'Свойства'

    def __str__(self):
        return self.title

class Category(models.Model):
    title = models.CharField(max_length=90, blank=True, default='', verbose_name='Категория')

    def display_event_count(self):
        return len(self.events.all())
    display_event_count.short_description = 'Количество событий'


    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title

class Event(models.Model):

    FULLNESS_FREE = '1'
    FULLNESS_MIDDLE = '2'
    FULLNESS_FULL = '3'
    FULLNESS_LEGEND_FREE = '<= 50%'
    FULLNESS_LEGEND_MIDDLE = '> 50%'
    FULLNESS_LEGEND_FULL = 'sold-out'
    FULLNESS_VARIANTS = (
        (FULLNESS_FREE, FULLNESS_LEGEND_FREE),
        (FULLNESS_MIDDLE, FULLNESS_LEGEND_MIDDLE),
        (FULLNESS_FULL, FULLNESS_LEGEND_FULL),
    )

    title = models.CharField(max_length=200, blank=True, default='', verbose_name='Название')
    description = models.TextField(blank=True, default='', verbose_name='Описание')
    date_start = models.DateTimeField(verbose_name='Дата начала')
    participants_number = models.PositiveSmallIntegerField(verbose_name='Количество участников')
    is_private = models.BooleanField(default=False, verbose_name='Частное')
    category = models.ForeignKey(Category,null=True,on_delete=models.CASCADE,related_name='events')
    features = models.ManyToManyField(Feature)
    logo = models.ImageField( blank=True, null=True)


    def display_enroll_count(self):
        return len(self.enrolls.all())

    display_enroll_count.short_description = 'Количество записей'


    def get_enroll_count(self):
        return self.enrolls.count()

    def get_places_left(self):
        return int(self.participants_number or 0) - self.get_enroll_count()

    def get_fullness_legend(self, **kwargs):
        legend = ''
        if int(self.participants_number or 0) > 0:
            legend = Event.FULLNESS_LEGEND_FREE
            places_left = kwargs.get('places_left', None)
            if places_left is None:
                places_left = self.get_places_left()
            if places_left == 0:
                legend = Event.FULLNESS_LEGEND_FULL
            elif places_left < self.participants_number / 2:
                legend = Event.FULLNESS_LEGEND_MIDDLE
        return legend

    def display_places_left(self):
        places_left = self.get_places_left()
        return f'{places_left} ({self.get_fullness_legend(places_left=places_left)})'

    display_places_left.short_description = 'Осталось мест'

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
        ordering = ['date_start']

    def __str__(self):
        return self.title

    @property
    def rate(self):
        reviews = self.reviews.all()
        sum,count = 0,0
        for rev in reviews:
            sum += rev.rate
            count += 1
        try:
            return round(sum/count,1)
        except:
            return 0


    @property
    def logo_url(self):
        return self.logo.url if self.logo else f'{settings.STATIC_URL}images/svg-icon/event.svg'

    def get_absolute_url(self):
        return reverse('events:event_detail', args=[str(self.pk)])




class Enroll(models.Model):
    user = models.ForeignKey(User, blank=True, on_delete = models.CASCADE,related_name='enrolls')
    event = models.ForeignKey(Event, blank=True, on_delete = models.CASCADE,related_name='enrolls')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def __str__(self):
        return self.event

class Review(models.Model):
    user = models.ForeignKey(User, blank=True, on_delete = models.CASCADE,related_name='reviews')
    event = models.ForeignKey(Event, blank=True, on_delete = models.CASCADE,related_name='reviews')
    created = models.DateTimeField(auto_now_add=True)
    rate = models.PositiveSmallIntegerField()
    updated = models.DateTimeField(auto_now=True)
    text = models.TextField(blank=True, default='', verbose_name='текст отзыва')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'








