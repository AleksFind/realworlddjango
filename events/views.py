import datetime
import json
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, UpdateView, DeleteView, CreateView

from events.forms import (EventUpdateForm, EventCreationForm, EnrollCreationForm,
                          EventAddToFavoriteForm, EventFilterForm)
from events.models import Event, Review, Enroll, Favorite


class PermissionRequiredMixin:
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden('Недостаточно прав')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden('Недостаточно прав')
        return super().post(request, *args, **kwargs)


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'  # необязательно, указать, если имя шаблона отличается от стандартного
    context_object_name = 'event_objects'
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = EventFilterForm(self.request.GET)
        return context

    def get_queryset(self):

        queryset = super().get_queryset()
        queryset = queryset.EvQuSet()

        # обработка кнопки "Сбросить"
        if self.request.GET.get('Delete', ''):
            filter_dist = self.request.GET.copy()
            # удалить 'filter' в сесии:
            if 'filter' in self.request.session:
                del self.request.session['filter']

            # удаоить фильтры в запросах GET:
            if 'date_start' in filter_dist:
                del filter_dist['date_start']
            if 'date_end' in filter_dist:
                del filter_dist['date_end']
            if 'category' in filter_dist:
                del filter_dist['category']
            if 'features' in filter_dist:
                del filter_dist['features']
            if 'is_private' in filter_dist:
                del filter_dist['is_private']
            if 'is_available' in filter_dist:
                del filter_dist['is_available']
            if 'page' in filter_dist:
                del filter_dist['page']
            if 'Delete' in filter_dist:
                del filter_dist['Delete']

            self.request.GET = filter_dist

            return queryset.order_by('-pk')

        # начало обработки запроса GET для запоминариня фильтров
        filter_dist = {}
        # если был переход по стриницам
        page = self.request.GET.get('page', None)

        if 'filter' in self.request.session:
            filter_dist = self.request.session['filter']

            if page:
                # добавить 'page' к session['filter']
                filter_dist.update({'page': page})
            else:
                if self.request.GET:
                    # поностью обновить session['filter']
                    del self.request.session['filter']
                    filter_dist = self.request.GET.copy()

            if len(filter_dist) > 0:
                self.request.session['filter'] = filter_dist
                self.request.GET = filter_dist
        else:
            filter_dist = self.request.GET.copy()
        # конец обработки запроса GET для запоминариня фильтров

        # обработка фильтров
        if filter_dist.__contains__('category'):
            filter_category = self.request.GET.get('category', '')
            filter_dist['category'] = filter_category
        else:
            filter_category = None

        if filter_dist.__contains__('features'):
            q = json.loads(json.dumps(dict(filter_dist)))
            filter_features = q['features']
            filter_dist['features'] = filter_features
        else:
            filter_features = None

        if filter_dist.__contains__('date_start'):
            filter_date_start = self.request.GET.get('date_start', '')
            filter_dist['date_start'] = filter_date_start
        else:
            filter_date_start = None

        if filter_dist.__contains__('date_end'):
            filter_date_end = self.request.GET.get('date_end', '')
            filter_dist['date_end'] = filter_date_end
        else:
            filter_date_end = None

        if filter_dist.__contains__('is_private'):
            filter_is_private = self.request.GET.get('is_private', '')
            filter_dist['is_private'] = filter_is_private
        else:
            filter_is_private = None

        if filter_dist.__contains__('is_available'):
            filter_is_available = self.request.GET.get('is_available', '')
            filter_dist['is_available'] = filter_is_available
        else:
            filter_is_available = None

        if page:
            filter_dist['page'] = page

        if len(filter_dist) > 0:
            self.request.session['filter'] = filter_dist

        if filter_category:
            queryset = queryset.filter(category=filter_category)
        if filter_features:
            for feature in filter_features:
                queryset = queryset.filter(features__in=feature)
        if filter_date_start:
            queryset = queryset.filter(date_start__gt=filter_date_start)
        if filter_date_end:
            queryset = queryset.filter(date_start__lt=filter_date_end)
        if filter_is_private:
            queryset = queryset.filter(is_private=True)
        if filter_is_available:
            queryset = queryset.filter(available__gt=0)

        return queryset.order_by('-pk')


class EventUpdateView(PermissionRequiredMixin, UpdateView):
    model = Event
    template_name = 'events/event_update.html'
    form_class = EventUpdateForm

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.event_qs()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heading'] = 'Редактирование события'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Cобытие {form.cleaned_data["title"]} успешно изменено')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        return super().form_invalid(form)


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = {
            'user': self.request.user,
            'event': self.object,
        }
        context['enroll_form'] = EnrollCreationForm(initial=initial)
        context['favorite_form'] = EventAddToFavoriteForm(initial=initial)
        context['heading'] = 'Cобытие'
        return context

    def get_queryset(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = super().get_queryset()
        queryset = queryset.event_qs().filter(pk=pk)
        return queryset


class EventDeleteView(PermissionRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/event_update.html'
    success_url = reverse_lazy('events:event_list')

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.success(request, f'Событие {self.object} удалено')
        return result


class EventCreateView(PermissionRequiredMixin, CreateView):
    model = Event
    template_name = 'events/event_update.html'
    form_class = EventCreationForm
    success_url = reverse_lazy('events:event_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heading'] = 'Добавление события'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Новое событие {form.cleaned_data["title"]} создано успешно')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        return super().form_invalid(form)


class EnrollCreateView(PermissionRequiredMixin, CreateView):
    model = Enroll
    form_class = EnrollCreationForm

    def get_success_url(self):
        return self.object.event.get_absolute_url()

    def form_valid(self, form):
        messages.success(self.request, f'Вы успешно записались на {form.cleaned_data["event"]}')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        event = form.cleaned_data.get('event', None)
        if not event:
            event = get_object_or_404(Event, pk=form.data.get('event'))

        redirect_url = event.get_absolute_url() if event else reverse_lazy('events:event_list')
        return HttpResponseRedirect(redirect_url)


class EventAddToFavoriteView(PermissionRequiredMixin, CreateView):
    model = Favorite
    form_class = EventAddToFavoriteForm

    def get_success_url(self):
        return self.object.event.get_absolute_url()

    def form_valid(self, form):
        messages.success(self.request, f'Событие {form.cleaned_data["event"]} добавлено в избранное')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        event = form.cleaned_data.get('event', None)

        if not event:
            event = get_object_or_404(Event, pk=form.data.get('event'))
        redirect_url = event.get_absolute_url() if event else reverse_lazy('events:event_list')
        return HttpResponseRedirect(redirect_url)


@require_POST
def create_review(request):
    data = {
        'ok': True,
        'msg': '',
        'rate': request.POST.get('rate'),
        'text': request.POST.get('text'),
        'created': datetime.date.today().strftime('%d.%m.%Y'),
        'user_name': ''
    }

    pk = request.POST.get('event_id', '')
    if not pk:
        data['msg'] = 'Событие не найдено'
        data['ok'] = False
        return JsonResponse(data)

    else:
        event = Event.objects.get(pk=pk)

        if not request.user.is_authenticated:
            data['msg'] = 'Отзывы могут отправлять только зарегистрированные пользователи'
            data['ok'] = False
            return JsonResponse(data)

        data['user_name'] = request.user.__str__()

        if Review.objects.filter(user=request.user, event=event).exists():
            data['msg'] = 'Вы уже отправляли отзыв к этому событию'
            data['ok'] = False

        elif data['text'] == '' or data['rate'] == '':
            data['msg'] = 'Оценка и текст отзыва - обязательные поля'
            data['ok'] = False

        else:
            new_review = Review(
                user=request.user,
                event=event,
                rate=data['rate'],
                text=data['text'],
                created=data['created'],
                updated=data['created']
            )

            new_review.save()

        return JsonResponse(data)