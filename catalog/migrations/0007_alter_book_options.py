# Generated by Django 5.0.1 on 2024-02-10 06:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_alter_author_options_alter_book_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ['title'], 'permissions': (('can_modify', 'Create, Update and Delete books'),)},
        ),
    ]