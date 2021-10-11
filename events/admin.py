from django.contrib import admin
from . import models

# Register your models here.

class PlaceLeftFilter(admin.SimpleListFilter):
    title = 'Заполненность события'
    parameter_name = 'places_left_filter'

    def lookups(self, request, model_admin):
        filter_list = [
            ('0', '<=50%'),
            ('1', '>50%'),
            ('2', 'sold-out')
        ]
        return filter_list


    def queryset(self, request, queryset):
        filter_value = self.value()
        for obj in queryset:
            new_obj = obj
            new_obj.res=models.Event.result(obj)
            new_obj.save()

        if filter_value == '0':
            return queryset.filter(res__gte=0, res__lte=0.5)
        elif filter_value == '1':
            return queryset.filter(res__gt=0.5,res__lt=1)
        elif filter_value == '2':
            return queryset.filter(res=1)
        return queryset

class ReviewInline(admin.TabularInline):
    model = models.Review
    readonly_fields = ('id','user','rate','text','created','updated',)
    can_delete = False

    def has_add_permission(self, request, obj):
        if obj:
            return False


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'date_start','participants_number','category','is_private','display_enroll_count', ]
    list_display.append('display_places_left')
    list_select_related = ['category',]
    list_filter = [PlaceLeftFilter, 'category', 'features', ]
    search_fields = ['title',]
    readonly_fields = ['display_enroll_count','display_places_left']
    exclude = ['res']
    filter_horizontal = ['features',]
    inlines = [ReviewInline]




@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id','display_event_count', 'title', ]
    list_display_links = ['id', 'title', ]


@admin.register(models.Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', ]
    list_display_links = ['id', 'title', ]

@admin.register(models.Enroll)
class EnrollAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event', ]
    list_display_links = ['id', 'user', 'event', ]

@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['created', 'user', 'event', 'updated', 'id', ]
    list_display_links = ['id', 'user', 'event', ]
    list_filter = ['created','event',]


