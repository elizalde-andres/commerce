# Generated by Django 3.2.5 on 2021-07-15 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_alter_auctionlisting_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='image_url',
            field=models.URLField(blank=True, default='static/no-image-available.jpg', null=True),
        ),
    ]
