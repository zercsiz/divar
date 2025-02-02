# Generated by Django 4.2.18 on 2025-02-01 15:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_entry'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='entry',
            name='category',
            field=models.ForeignKey(null=False, on_delete=django.db.models.deletion.CASCADE, to='core.category'),
        ),
    ]
