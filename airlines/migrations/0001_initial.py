# Generated by Django 2.0.2 on 2018-05-05 11:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('src', models.CharField(max_length=200, verbose_name='Source airport')),
                ('dest', models.CharField(max_length=200, verbose_name='Destination airport')),
                ('start', models.DateTimeField(verbose_name='Start date')),
                ('end', models.DateTimeField(verbose_name='Landing date')),
            ],
        ),
        migrations.CreateModel(
            name='Plane',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reg_id', models.CharField(max_length=200, verbose_name='Registration identificator')),
                ('seats_count', models.IntegerField(verbose_name='Seats')),
                ('service_start', models.DateTimeField(verbose_name='In service since')),
            ],
        ),
        migrations.AddField(
            model_name='flight',
            name='plane',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airlines.Plane'),
        ),
    ]
