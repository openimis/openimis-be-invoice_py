# Generated by Django 3.2.19 on 2023-09-21 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0011_auto_20230914_0805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'draft'), (1, 'validated'), (2, 'paid'), (3, 'cancelled'), (4, 'deleted'), (5, 'suspended'), (6, 'unpaid'), (7, 'reconciliated')], db_column='Status', default=0),
        ),
        migrations.AlterField(
            model_name='historicalbill',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'draft'), (1, 'validated'), (2, 'paid'), (3, 'cancelled'), (4, 'deleted'), (5, 'suspended'), (6, 'unpaid'), (7, 'reconciliated')], db_column='Status', default=0),
        ),
        migrations.AlterField(
            model_name='historicalinvoice',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'draft'), (1, 'validated'), (2, 'paid'), (3, 'cancelled'), (4, 'deleted'), (5, 'suspended'), (6, 'unpaid'), (7, 'reconciliated')], db_column='Status', default=0),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'draft'), (1, 'validated'), (2, 'paid'), (3, 'cancelled'), (4, 'deleted'), (5, 'suspended'), (6, 'unpaid'), (7, 'reconciliated')], db_column='Status', default=0),
        ),
    ]
