# Generated by Django 5.1.3 on 2024-12-02 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='level',
            field=models.IntegerField(default=0),
        ),
    ]
