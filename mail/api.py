from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from mail.models import Subscriber, Letter


@require_POST
def create_letters_view(request):
    emails = request.POST.getlist('email', None)
    subject = request.POST.get('subject', '')
    text = request.POST.get('text', '')
    new_letters = []
    if emails and subject and text:
        new_letters = Letter.create_letters(emails, subject, text)
    subscribers = Subscriber.get_objects_list()

    # Демо-режим
    if not settings.DEBUG:
        for letter in new_letters:
            letter.delete()

    return JsonResponse({'subscribers': subscribers})


@require_POST
def send_letters(request):
    emails = request.POST.getlist('email', None)

    for email in emails:
        subscriber = Subscriber.get_by_email(email)
        if subscriber:
            subscriber.send_post(bulk=True)

    return JsonResponse({'ok': 'ok'})


def get_subscribers(request):
    all_emails_sent = not Letter.objects.filter(is_sent=False).exists()
    return JsonResponse({'subscribers': Subscriber.get_objects_list(),
                         'all_emails_sent': all_emails_sent})
