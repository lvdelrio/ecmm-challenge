from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product


class ProductCreateTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Bebidas")
        self.list_url = reverse("product-list")

    def test_create_product_ok(self):
        payload = {
            "name": "Cafe molido 250g",
            "description": "Tueste medio",
            "price": "5990.00",
            "stock": 12,
            "category": self.category.id,
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.get()
        self.assertEqual(product.name, "Cafe molido 250g")
        self.assertEqual(product.price, Decimal("5990.00"))
        self.assertEqual(product.category, self.category)
        self.assertIsNotNone(product.created_at)

    def test_create_product_rejects_invalid_data(self):
        payload = {
            "name": "",
            "price": "-1",
            "stock": -3,
            "category": 9999,
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn("price", response.data)
        self.assertIn("stock", response.data)
        self.assertIn("category", response.data)
        self.assertEqual(Product.objects.count(), 0)

    def test_price_and_stock_zero_are_allowed(self):
        payload = {
            "name": "Muestra gratis",
            "price": "0.00",
            "stock": 0,
            "category": self.category.id,
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.get().price, Decimal("0.00"))

    def test_create_product_requires_existing_category(self):
        payload = {"name": "Sin categoria", "price": "1000", "stock": 1}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("category", response.data)


class ProductQueryTests(APITestCase):
    def setUp(self):
        self.bebidas = Category.objects.create(name="Bebidas")
        self.snacks = Category.objects.create(name="Snacks")
        self.list_url = reverse("product-list")
        Product.objects.create(
            name="Jugo de naranja", price=1500, stock=5, category=self.bebidas
        )
        Product.objects.create(
            name="Agua mineral", price=990, stock=20, category=self.bebidas
        )
        Product.objects.create(
            name="Papas fritas", price=1200, stock=8, category=self.snacks
        )

    def test_filter_by_category(self):
        response = self.client.get(self.list_url, {"category": self.snacks.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Papas fritas")

    def test_search_by_name(self):
        response = self.client.get(self.list_url, {"search": "agua"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Agua mineral")

    def test_search_is_case_insensitive_and_partial(self):
        response = self.client.get(self.list_url, {"search": "MINERAL"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Agua mineral")

    def test_filter_and_search_combined(self):
        response = self.client.get(
            self.list_url, {"category": self.bebidas.id, "search": "jugo"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Jugo de naranja")

    def test_retrieve_by_id(self):
        product = Product.objects.first()

        response = self.client.get(reverse("product-detail", args=[product.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], product.id)
        self.assertEqual(response.data["category_name"], product.category.name)


class ProductUpdateTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Bebidas")
        self.product = Product.objects.create(
            name="Agua mineral", price=990, stock=20, category=self.category
        )

    def test_partial_update_changes_price(self):
        url = reverse("product-detail", args=[self.product.id])

        response = self.client.patch(url, {"price": "1290.00"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, Decimal("1290.00"))

    def test_partial_update_rejects_negative_stock(self):
        url = reverse("product-detail", args=[self.product.id])

        response = self.client.patch(url, {"stock": -5}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CategoryTests(APITestCase):
    def setUp(self):
        self.list_url = reverse("category-list")

    def test_category_name_must_be_unique(self):
        Category.objects.create(name="Bebidas")

        response = self.client.post(self.list_url, {"name": "Bebidas"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_cannot_delete_category_with_products(self):
        category = Category.objects.create(name="Bebidas")
        Product.objects.create(
            name="Agua mineral", price=990, stock=20, category=category
        )

        response = self.client.delete(reverse("category-detail", args=[category.id]))

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(Category.objects.filter(id=category.id).exists())

    def test_can_delete_category_without_products(self):
        category = Category.objects.create(name="Vacia")

        response = self.client.delete(reverse("category-detail", args=[category.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())
