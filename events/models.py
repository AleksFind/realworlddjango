from django.db import models
from django.contrib.auth.models import User

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
    title = models.CharField(max_length=200, blank=True, default='', verbose_name='Название')
    description = models.TextField(blank=True, default='', verbose_name='Описание')
    date_start = models.DateTimeField(verbose_name='Дата начала')
    participants_number = models.PositiveSmallIntegerField(verbose_name='Количество участников')
    is_private = models.BooleanField(default=False, verbose_name='Частное')
    category = models.ForeignKey(Category,null=True,on_delete=models.CASCADE,related_name='events')
    features = models.ManyToManyField(Feature)


    def display_enroll_count(self):
        return len(self.enrolls.all())

    display_enroll_count.short_description = 'Количество записей'

    res = models.FloatField(blank=True)

    def result(self):
        self.res = len(self.enrolls.all())/self.participants_number
        return self.res

    def display_places_left(self):
        col = self.participants_number-len(self.enrolls.all())
        if col>= self.participants_number/2:
            return f'{col}(<=50%)'
        elif col< self.participants_number/2 and col !=0:
            return f'{col}(>50%)'
        elif col == 0:
            return f'{col}(sold-out)'

    display_places_left.short_description = 'Осталось мест'


    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
        ordering = ['date_start']

    def __str__(self):
        return self.title


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








