# Generated by Django 5.0.1 on 2024-02-10 06:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_alter_bookinstance_book'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='author',
            options={'ordering': ['last_name'], 'permissions': (('can_modify', 'Create, Update and Delete authors'),)},
        ),
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ['title'], 'permissions': (('can_modify', 'Create, Update and Delete authors'),)},
        ),
    ]