# Análisis previo — cómo abordar la prueba y qué necesitas

Este documento es el "para practicar": explica **qué instalar**, **qué decisiones
tomar** y **por qué**, antes de sentarte a escribir la solución real en tu fork.

---

## 1. Qué necesitas en tu entorno (y qué NO)

| Herramienta | ¿Hay que instalar algo? | Detalle |
|---|---|---|
| **Python 3.11+** | Ya lo tienes (`python --version` → 3.11.3) | Django 5.2 pide 3.10+ |
| **SQLite** | **No. Nada.** | Viene incluido en Python (`import sqlite3`). Django lo usa con `ENGINE: django.db.backends.sqlite3`. No se descarga, no hay servidor, no hay "workshop". El archivo `db.sqlite3` se crea solo al correr `migrate`. |
| **Node.js 18+** | Ya lo tienes (`node --version` → v24) | Solo para el frontend (Vite). El backend no usa Node. |
| **pip / venv** | Incluidos en Python | En Windows, si `pip` da "Permission denied", usa `python -m pip`. |
| Paquetes Python | Sí, 4 (ver abajo) | `pip install -r requirements.txt` dentro de un venv |
| Paquetes Node | Sí, `npm install` | React + Vite + plugin |

**No necesitas:** Docker, PostgreSQL, un servidor de BD, ni ningún "workshop"
o SDK aparte. Todo corre local con dos procesos (`runserver` y `vite`).

### Dependencias del backend (`requirements.txt`)

```
Django                 # framework + ORM + migraciones
djangorestframework    # la API REST (serializers, viewsets, router)
django-filter          # filtro por categoría vía querystring (?category=)
django-cors-headers    # permite que el front en :5173 llame a la API en :8000
```

Son 4 paquetes y los 4 se justifican por un requisito explícito de la prueba.

---

## 2. La duda clave: ¿SQLAlchemy? → **No. Es overkill y además rema en contra.**

Tu intuición de "quizás SQLAlchemy" es razonable si vinieras de Flask/FastAPI,
pero aquí **la prueba exige Django + Django REST Framework**, y Django trae su
**propio ORM**. Meter SQLAlchemy encima significa:

1. **Perder las migraciones automáticas.** `makemigrations` / `migrate` (un
   entregable pedido) funcionan con el ORM de Django. Con SQLAlchemy tendrías
   que sumar Alembic y mantener el esquema a mano.
2. **Perder la integración con DRF.** `ModelSerializer`, `ModelViewSet`,
   `DjangoFilterBackend` y `SearchFilter` asumen modelos de Django. Con
   SQLAlchemy escribes serializers y vistas a mano → más código, más chances de
   error, y el evaluador ve que "peleaste" con el framework.
3. **Dos fuentes de verdad.** Modelos Django (para admin, auth, sesiones) +
   modelos SQLAlchemy (para tu app) conviviendo. Complejidad pura sin beneficio.

**Regla práctica:** en un proyecto Django, el ORM es el de Django. SQLAlchemy
solo tiene sentido fuera de Django (Flask, FastAPI, scripts, ETL). Para esta
prueba, usar el ORM de Django **es** la elección "acorde con el alcance" que
pide el criterio de evaluación.

> En la solución de esta carpeta: 2 modelos, 1 archivo de migración generado por
> `makemigrations`, 0 líneas de SQL escritas a mano.

---

## 3. Frontend: ¿Next.js o React "a secas"? → **Vite + React**

La prueba permite "Next.js u otro framework basado en React… adecuado al
alcance". El alcance es: **una sola pantalla** que lista, crea y filtra
productos contra una API externa.

| | Next.js | **Vite + React (elegido)** |
|---|---|---|
| SSR / SEO | Sí (no lo necesitas: es un panel interno) | No |
| File-system routing | Sí (tienes 1 vista) | No hace falta |
| Runtime de servidor Node | Sí (otro proceso, más config) | No, es SPA estática |
| Arranque | `create-next-app` + convenciones | `npm create vite` + 5 archivos |
| Encaje con "API REST en Django aparte" | Se siente redundante | Natural: front tonto que consume la API |

**Decisión:** Vite + React. Es lo mínimo que resuelve el problema y deja claro
que el backend es la API. Next.js sería sobre-ingeniería aquí y el criterio
"elección de herramientas acorde con el alcance" penaliza eso.

Tú ya manejas React, así que la curva es cero. No uso Redux, React Query ni
axios: `fetch` + `useState`/`useEffect` alcanzan de sobra. (Con más tiempo,
React Query para cache/reintentos — ver sección 8.)

---

## 4. Modelado de datos — justificación campo por campo

### `Category`

| Campo | Tipo | Por qué |
|---|---|---|
| `name` | `CharField(max_length=120, unique=True)` | Requisito: "el nombre de cada categoría debe ser único". `unique=True` lo garantiza a nivel de BD **y** hace que DRF devuelva 400 si se repite. |

`__str__` devuelve el nombre para que el admin y los `<select>` se lean bien.
`on_delete=PROTECT` en el producto (ver abajo) evita borrar categorías con
productos colgando.

### `Product`

| Campo | Tipo | Por qué |
|---|---|---|
| `name` | `CharField(max_length=200)` | Obligatorio. `CharField` sin `null/blank` ⇒ DRF lo exige y responde 400 si falta o viene vacío. |
| `description` | `TextField(blank=True, default="")` | **Opcional** según las reglas (solo nombre, precio, stock y categoría son obligatorios). `blank=True` = puede ir vacío en formularios/serializer. |
| `price` | `DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])` | Dinero → **`Decimal`, nunca `float`** (evita errores de redondeo). `MinValueValidator(0)` ⇒ "precio ≥ 0". DRF copia ese validador al serializer, así que un `-1` da 400 automático. |
| `stock` | `PositiveIntegerField(validators=[MinValueValidator(0)])` | "Entero ≥ 0". `PositiveIntegerField` ya bloquea negativos; el `MinValueValidator` explícito lo deja documentado. `0` es válido. |
| `category` | `ForeignKey(Category, on_delete=PROTECT, related_name="products")` | Obligatorio y **debe existir**: una FK con `PrimaryKeyRelatedField` (el default de DRF) rechaza con 400 `"clave primaria inválida - objeto no existe"` si mandas un id que no está. `PROTECT` = no puedes borrar una categoría usada (más seguro que `CASCADE`, que borraría productos en silencio). `related_name="products"` permite `category.products.all()`. |
| `created_at` | `DateTimeField(auto_now_add=True)` | "Fecha de creación". `auto_now_add` la fija una sola vez al crear; queda `read_only` en el serializer para que nadie la falsee. |

`Meta.ordering = ["-created_at"]` → el listado sale con lo más nuevo primero sin
tener que pedir `?ordering=` desde el front.

---

## 5. Serializers, vistas y filtros

### Serializers (`catalog/serializers.py`)

- `ModelSerializer` para no repetir la definición de campos.
- `ProductSerializer` expone `category` (el id, para escribir) **y**
  `category_name` (solo lectura) para que el front muestre el nombre sin pedir
  `/categories` por cada fila.
- **Validación en un solo lugar:** los `MinValueValidator(0)` viven en el modelo.
  `ModelSerializer` los copia a los campos del serializer, así que `price=-1` o
  `stock=-3` dan 400 sin escribir nada más. Los mensajes salen en español porque
  `LANGUAGE_CODE = "es"` activa las traducciones de Django/DRF
  ("Asegúrese de que este valor es mayor o igual a 0."). No hay `validate_price`
  ni `validate_stock`: serían código muerto (el validador de campo corre antes y
  corta) y duplicarían la regla.
- `read_only_fields = ["id", "created_at"]`.

### Manejo de errores (`catalog/exceptions.py`)

`REST_FRAMEWORK["EXCEPTION_HANDLER"]` apunta a un handler propio. Solo hace una
cosa: si la excepción es `ProtectedError` (intentaste borrar una categoría con
productos, por el `on_delete=PROTECT`), responde **409 Conflict** con un mensaje
claro en vez del **500** que daría DRF por defecto (no cataloga `ProtectedError`
como error de API). Todo lo demás pasa al handler estándar. Ventaja: las vistas
quedan declarativas, la traducción de error vive en un único sitio.

### Vistas (`catalog/views.py`)

- `ModelViewSet` + `DefaultRouter` ⇒ las 6 rutas REST (list, retrieve, create,
  update, partial_update, destroy) con ~4 líneas por recurso. Es el patrón
  idiomático de DRF y el criterio "uso adecuado de vistas" lo premia.
- `queryset = Product.objects.select_related("category")` evita el problema
  N+1 al serializar `category_name`.
- `filter_backends`:
  - `DjangoFilterBackend` + `ProductFilter` → `?category=<id>`.
  - `SearchFilter` con `search_fields=["name"]` → `?search=<texto>`
    (búsqueda `icontains`, insensible a mayúsculas).
  - `OrderingFilter` → `?ordering=price` (extra, barato de agregar).

### Filtro (`catalog/filters.py`)

`ProductFilter` con `category` (por id) y `category_name` (por nombre exacto,
bonus). Alternativa sin dependencia: sobreescribir `get_queryset()` y leer
`request.query_params`. Usé `django-filter` porque es el estándar de facto en
DRF, son 3 líneas y queda declarativo. Con un solo filtro sería defendible
hacerlo a mano; lo menciono para que sepas el trade-off.

---

## 6. Cómo se cumple cada regla de la prueba

| Regla | Dónde se implementa |
|---|---|
| Backend en Django + DRF | `config/` + `catalog/`, `rest_framework` en `INSTALLED_APPS` |
| BD SQLite | `settings.DATABASES` → `sqlite3` |
| Nombre de categoría único | `Category.name` → `unique=True` (test: `CategoryTests`) |
| Nombre, precio, stock y categoría obligatorios | Campos sin `null/blank/default` ⇒ DRF exige ⇒ 400 (test: `test_create_product_rejects_invalid_data`) |
| Precio ≥ 0 | `MinValueValidator(0)` en el modelo (DRF lo copia al serializer) — test `test_price_and_stock_zero_are_allowed` + `test_create_product_rejects_invalid_data` |
| Stock entero ≥ 0 | `PositiveIntegerField` + `MinValueValidator(0)` |
| La categoría debe existir | FK + `PrimaryKeyRelatedField` ⇒ 400 si el id no existe (test `test_create_product_requires_existing_category`) |
| Errores de validación con HTTP apropiado | DRF devuelve `400` + JSON `{campo: [mensajes]}` automático; borrar categoría con productos ⇒ `409` (`catalog/exceptions.py`) |
| Listar / obtener por id | `GET /api/products/`, `GET /api/products/{id}/` |
| Crear / editar / eliminar | `POST` / `PUT`·`PATCH` / `DELETE` en `/api/products/{id}/` |
| Filtrar por categoría | `GET /api/products/?category=<id>` |
| Buscar por nombre | `GET /api/products/?search=<texto>` |
| Migraciones | `catalog/migrations/0001_initial.py` (generada, versionada; CI verifica que no falten con `makemigrations --check`) |
| ≥ 2 pruebas (alta OK + datos inválidos) | `catalog/tests.py` → 14 tests, incluidos los dos pedidos |
| Instrucciones para ejecutar | `README.md` |
| Interfaz: listar / crear / filtrar-buscar | `frontend/src/` (App + ProductList + ProductForm + Toolbar) |
| CI | `.github/workflows/ci.yml` (tests backend + build frontend en cada push) |

---

## 7. Decisiones y trade-offs (para poder defenderlas)

- **Sin paginación.** El alcance es chico y simplifica el front (la respuesta es
  una lista, no `{count, results}`). En un catálogo real activaría
  `PageNumberPagination` en `REST_FRAMEWORK`.
- **CORS con `django-cors-headers`** en vez del proxy de Vite. Ambos sirven; el
  header es lo que un evaluador espera ver y funciona aunque sirvas el front
  desde otro lado. La alternativa es `server.proxy` en `vite.config.js` apuntando
  a rutas relativas `/api`.
- **`on_delete=PROTECT`** en vez de `CASCADE`: borrar una categoría no debería
  llevarse productos en silencio. El `ProtectedError` se traduce a `409` en
  `catalog/exceptions.py`.
- **`category_name` en el serializer** en vez de serializer anidado completo:
  el front solo necesita el texto; anidar todo el objeto es data de más.
- **Validación solo en el modelo.** El serializer no repite la comprobación de
  `price`/`stock`: DRF hereda los validadores del modelo y los mensajes en
  español los da Django por `LANGUAGE_CODE`. Un `validate_price` que reimplemente
  `>= 0` sería código muerto (el validador de campo corre primero).
- **Código sin comentarios.** Nombres de dominio, archivos chicos con una
  responsabilidad (`models` / `serializers` / `views` / `filters` / `exceptions`)
  y utilidades del front movidas fuera de los componentes (`lib/format.js`,
  `hooks/useDebouncedValue.js`). El "por qué" va en este documento, no en el
  código.

---

## 8. Qué haría con más tiempo (mencionarlo suma)

- Edición inline en la tabla del front (hoy hay crear + eliminar; `PATCH` ya
  existe en la API y en `api.js`).
- `React Query` para cache, estados de carga/error y refetch tras mutaciones.
- Paginación + orden desde la UI (cabeceras de tabla clicables).
- `POST /api/categories/` desde la UI (hoy se siembran con `seed_catalog` o el
  admin de Django).
- Tests de front con Vitest + Testing Library.
- Endpoint de categorías con conteo de productos (`annotate(Count("products"))`).

---

## 9. Uso de IA (para tus anotaciones de la entrega)

Este scaffold se generó con asistencia de IA (Claude) para: estructurar el
proyecto, redactar el boilerplate de Django/DRF y este análisis. Todo el código
es estándar de DRF y Vite, sin comentarios (nombres descriptivos), y es
explicable línea por línea; los tests corren en verde
(`manage.py test` → 14 OK), `npm run build` OK, y la API se probó de punta a
punta con `curl`.
