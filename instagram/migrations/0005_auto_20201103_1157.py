# Generated by Django 3.1 on 2020-11-03 02:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instagram', '0004_comment_message'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-id']},
        ),
    ]