from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField("nombre", max_length=120, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "categoria"
        verbose_name_plural = "categorias"

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField("nombre", max_length=200)
    description = models.TextField("descripcion", blank=True, default="")
    price = models.DecimalField(
        "precio",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    stock = models.PositiveIntegerField("stock", validators=[MinValueValidator(0)])
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="categoria",
    )
    created_at = models.DateTimeField("fecha de creacion", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "producto"
        verbose_name_plural = "productos"

    def __str__(self) -> str:
        return self.name
