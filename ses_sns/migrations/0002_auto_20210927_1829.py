# Generated by Django 3.2.7 on 2021-09-27 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ses_sns', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blacklistedemail',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='snsnotification',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
