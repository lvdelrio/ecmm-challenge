import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True, verbose_name='nombre')),
            ],
            options={
                'verbose_name': 'categoria',
                'verbose_name_plural': 'categorias',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='nombre')),
                ('description', models.TextField(blank=True, default='', verbose_name='descripcion')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='precio')),
                ('stock', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='stock')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creacion')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='catalog.category', verbose_name='categoria')),
            ],
            options={
                'verbose_name': 'producto',
                'verbose_name_plural': 'productos',
                'ordering': ['-created_at'],
            },
        ),
    ]
