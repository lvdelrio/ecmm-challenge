# Prueba técnica Junior Fullstack

Aplicación para administrar un catálogo de productos: API REST en Django + Django
REST Framework, interfaz web en React (Vite) que la consume, base de datos SQLite.

![CI](https://github.com/lvdelrio/ecmm-challenge/actions/workflows/ci.yml/badge.svg)

## Alcance cubierto

**API**

- Listar productos y consultar uno por su ID.
- Crear, editar y eliminar productos.
- Filtrar productos por categoría (`?category=<id>`).
- Buscar productos por nombre (`?search=<texto>`, parcial e insensible a mayúsculas).

**Categoría:** `nombre` (único).
**Producto:** `nombre`, `descripción`, `precio`, `stock`, `categoría`, `fecha de creación`.

**Interfaz web**

- Listado de productos.
- Alta mediante formulario (los errores 400 de la API se muestran bajo cada campo).
- Búsqueda por nombre + filtro por categoría (combinables, con debounce).

## Reglas implementadas

| Regla | Implementación |
|---|---|
| Backend Django + DRF | `backend/config/` + `backend/catalog/` |
| BD SQLite | `settings.DATABASES` → `sqlite3` |
| Nombre de categoría único | `Category.name` con `unique=True` |
| Nombre, precio, stock y categoría obligatorios | Campos sin `null/blank/default` ⇒ DRF exige ⇒ 400 |
| Precio ≥ 0 | `MinValueValidator(0)` en el modelo (DRF lo hereda al serializer) |
| Stock entero ≥ 0 | `PositiveIntegerField` + `MinValueValidator(0)` |
| La categoría asociada debe existir | FK + `PrimaryKeyRelatedField` ⇒ 400 si el id no existe |
| Errores de validación con HTTP apropiado | 400 + JSON `{campo: [mensajes]}`; borrar categoría con productos ⇒ 409 |

---

# Anotaciones del postulante

## Instrucciones de ejecución

Requisitos: **Python 3.10+** y **Node.js 18+**. SQLite viene con Python (no se
instala nada). Probado en Windows 10 (Python 3.11, Node 24) y en CI con Ubuntu +
Python 3.12.

### Backend — API en `http://localhost:8000`

Desde `backend/`:

```bash
python -m venv .venv
# Windows PowerShell:  .\.venv\Scripts\Activate.ps1
# Windows Git Bash:    source .venv/Scripts/activate
# macOS / Linux:       source .venv/bin/activate

python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_catalog        # opcional: 4 categorías + 6 productos
python manage.py runserver
```

### Frontend — `http://localhost:5173`

En otra terminal, desde `frontend/`, con el backend corriendo:

```bash
npm install
npm run dev
```

### Pruebas

Desde `backend/`, con el entorno virtual activo:

```bash
python manage.py test
```

Esperado: `Ran 14 tests ... OK`. Cubre los dos casos pedidos
(`test_create_product_ok`, `test_create_product_rejects_invalid_data`) más casos
de borde: precio/stock en 0, categoría inexistente, búsqueda insensible a
mayúsculas, filtro + búsqueda combinados, `PATCH` parcial y borrado protegido de
categoría.

### Admin de Django (opcional)

```bash
python manage.py createsuperuser
```

`http://localhost:8000/admin/` para gestionar el catálogo por UI.

### Endpoints

Base: `http://localhost:8000/api`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/products/` | Listar (lo más nuevo primero) |
| `GET` | `/products/?search=<texto>` | Buscar por nombre |
| `GET` | `/products/?category=<id>` | Filtrar por categoría |
| `GET` | `/products/?ordering=price` | Ordenar (`name`, `price`, `stock`, `created_at`) |
| `GET` | `/products/{id}/` | Obtener uno |
| `POST` | `/products/` | Crear |
| `PUT` / `PATCH` | `/products/{id}/` | Editar total / parcial |
| `DELETE` | `/products/{id}/` | Eliminar |
| `GET` `POST` | `/categories/` | Listar / crear categoría |
| `GET/PUT/PATCH/DELETE` | `/categories/{id}/` | Detalle / editar / borrar |

`DELETE /categories/{id}/` sobre una categoría con productos devuelve **409
Conflict** con `{"detail": "No se puede eliminar una categoria con productos asociados."}`.

## Decisiones y observaciones

**Stack.** Django + DRF + SQLite (obligatorio). Frontend **Vite + React**, no
Next.js: es una sola pantalla que consume una API externa; no hay SSR, SEO,
routing ni runtime de servidor que justifiquen Next. El criterio "herramientas
acorde al alcance" penaliza sobre-ingeniería. Sin Redux / React Query / axios:
`fetch` + hooks alcanzan.

**ORM.** El de Django, no SQLAlchemy: DRF (`ModelSerializer`, `ModelViewSet`,
`DjangoFilterBackend`) y las migraciones dependen de él. SQLAlchemy sería doble
fuente de verdad y perder `makemigrations`.

**Modelo.** `price` es `DecimalField` (dinero, nunca `float`). `stock` es
`PositiveIntegerField`. `created_at` con `auto_now_add` y `read_only` en el
serializer. La FK `Product.category` usa `on_delete=PROTECT`: borrar una
categoría no debe llevarse productos en silencio.

**Validación en un solo lugar.** Los `MinValueValidator(0)` viven en el modelo;
`ModelSerializer` los hereda, así que `price=-1` / `stock=-3` dan 400 sin código
extra. Los mensajes salen en español porque `LANGUAGE_CODE = "es"` activa las
traducciones de Django/DRF. No hay `validate_price` / `validate_stock`: con el
validador de campo ya presente serían código muerto y duplicarían la regla.

**Manejo de errores.** `catalog/exceptions.py` es un `EXCEPTION_HANDLER` de DRF
que traduce `ProtectedError` (borrar categoría con productos) a **409** en vez
del **500** que daría por defecto. Las vistas quedan declarativas y la
traducción vive en un único sitio.

**Vistas y filtros.** `ModelViewSet` + `DefaultRouter` para las 6 rutas REST por
recurso. `select_related("category")` evita N+1 al serializar `category_name`.
Filtro por categoría con `django-filter`; búsqueda por nombre con `SearchFilter`.

**Serializer.** `ProductSerializer` expone `category` (id, para escribir) y
`category_name` (solo lectura) para que el front no pida `/categories` por fila.

**CORS.** `django-cors-headers` con lista blanca de orígenes
(`http://localhost:5173`), no `CORS_ALLOW_ALL_ORIGINS`. Alternativa: `server.proxy`
de Vite hacia `/api`.

**Sin paginación.** El alcance es chico; la respuesta es una lista simple. En un
catálogo real: `PageNumberPagination`.

**Frontend limpio.** Utilidades fuera de los componentes: formato de moneda/fecha
en `src/lib/format.js`, debounce en `src/hooks/useDebouncedValue.js`. El código
no lleva comentarios: nombres de dominio y archivos con una responsabilidad.

**CI.** `.github/workflows/ci.yml` corre en cada push/PR: backend
(`makemigrations --check` + `migrate` + `test`) y frontend (`npm ci` + `build`).

**Supuestos.** El nombre de producto no es único (sí el de categoría, por regla).
`description` es opcional (las reglas solo exigen nombre, precio, stock y
categoría).

**Mejoras pendientes.** Edición inline en la tabla (el `PATCH` ya existe en API y
`api.js`); alta de categorías desde la UI (hoy vía `seed_catalog` o admin);
paginación y orden desde la UI; tests de front con Vitest.

Rationale extendido y comparación de alternativas: [`ANALISIS.md`](ANALISIS.md).

## Herramientas de IA utilizadas

Se usó **Claude (Claude Code)** como apoyo para: estructurar el proyecto, generar
el boilerplate de Django/DRF y Vite, redactar los tests y esta documentación, y
revisar el código contra principios de código limpio (responsabilidad única,
sin duplicación, sin comentarios).

Todo el código es estándar de DRF/React y es explicable línea por línea.
Verificación propia: `python manage.py test` → 14 OK, `npm run build` → OK, y la
API probada de punta a punta con `curl` (alta válida e inválida, filtro,
búsqueda, borrado protegido).
