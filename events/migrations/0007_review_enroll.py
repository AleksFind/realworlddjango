# Generated by Django 3.2.6 on 2021-11-12 15:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_alter_review_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='enroll',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='events.enroll'),
        ),
    ]