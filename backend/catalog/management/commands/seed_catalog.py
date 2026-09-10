from decimal import Decimal

from django.core.management.base import BaseCommand

from catalog.models import Category, Product

CATEGORIES = ["Bebidas", "Snacks", "Aseo", "Libreria"]

PRODUCTS = [
    ("Jugo de naranja 1L", "Sin azucar anadida", Decimal("1890.00"), 25, "Bebidas"),
    ("Agua mineral 500ml", "Con gas", Decimal("990.00"), 60, "Bebidas"),
    ("Papas fritas 200g", "Corte americano", Decimal("2490.00"), 18, "Snacks"),
    ("Barra de cereal", "Avena y miel", Decimal("790.00"), 40, "Snacks"),
    ("Detergente 1kg", "Ropa de color", Decimal("4590.00"), 12, "Aseo"),
    ("Cuaderno universitario", "100 hojas cuadriculado", Decimal("2990.00"), 30, "Libreria"),
]


class Command(BaseCommand):
    help = "Crea categorias y productos de ejemplo (idempotente)."

    def handle(self, *args, **options):
        categories = {}
        for name in CATEGORIES:
            category, _ = Category.objects.get_or_create(name=name)
            categories[name] = category

        created = 0
        for name, description, price, stock, category_name in PRODUCTS:
            _, was_created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "price": price,
                    "stock": stock,
                    "category": categories[category_name],
                },
            )
            created += int(was_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Listo. Categorias: {len(categories)}. Productos nuevos: {created}."
            )
        )
