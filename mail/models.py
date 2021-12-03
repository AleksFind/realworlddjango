from threading import Thread
from time import sleep

from django.conf import settings
from django.core.mail import send_mail
from django.db import models

from mail.managers import SubscriberQuerySet


class Subscriber(models.Model):
    email = models.EmailField(null=True)
    objects = SubscriberQuerySet.as_manager()

    def __str__(self):
        return f'{self.email}'

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

    @staticmethod
    def get_by_email(email):
        return Subscriber.objects.filter(email__iexact=email).first()

    @staticmethod
    def get_objects_list():
        qs = Subscriber.objects.with_counts()
        subscribers = []
        for item in qs:
            subscribers.append({
                'email': item.email,
                'letter_count': item.letter_count,
                'sent_letter_count': item.sent_letter_count,
            })
        return subscribers

    def unset_letters(self):
        return self.letters.filter(is_sent=False)

    def send_post(self, bulk=False):
        # Демо-режим
        if not settings.DEBUG:
            letters = list(self.letters.filter(is_sent=True))
            for letter in letters:
                letter.is_sent = False
            Letter.objects.bulk_update(letters, ['is_sent'])

        th_list = []
        for letter in self.unset_letters():
            if bulk:
                th = Thread(target=letter.send)
                th.start()
                th_list.append(th)
            else:
                letter.send()

        # Демо-режим
        if not settings.DEBUG:
            for item in th_list:
                item.join()
            th_reset = Thread(target=self.reset_post)
            th_reset.start()

    def reset_post(self):
        # Демо-режим
        sleep(5)
        letters = list(self.letters.filter(is_sent=True))
        for letter in letters:
            letter.is_sent = False
        Letter.objects.bulk_update(letters, ['is_sent'])


class Letter(models.Model):
    to = models.ForeignKey(Subscriber, null=True, on_delete=models.CASCADE, verbose_name='Получатель',
                           related_name='letters')
    subject = models.CharField(max_length=200, default='', verbose_name='Тема письма')
    text = models.TextField(default='', verbose_name='Текст письма')
    is_sent = models.BooleanField(default=False, verbose_name='Отправлено')

    def __str__(self):
        return f'{self.to} - {self.subject}'

    class Meta:
        verbose_name = 'Письмо'
        verbose_name_plural = 'Письма'

    @staticmethod
    def create_letters(emails, subject, text):
        new_letters = []
        for email in emails:
            to = Subscriber.get_by_email(email)
            if to:
                new_letters.append(Letter.objects.create(to=to, subject=subject, text=text))
        return new_letters

    def send(self):
        send_mail(
            self.subject,
            self.text,
            settings.EMAIL_HOST_USER,
            [self.to],
            fail_silently=True,
         )
        self.is_sent = True
        self.save()