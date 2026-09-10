import { useCallback, useEffect, useState } from "react";
import { listProducts, listCategories } from "./api.js";
import { useDebouncedValue } from "./hooks/useDebouncedValue.js";
import Toolbar from "./components/Toolbar.jsx";
import ProductForm from "./components/ProductForm.jsx";
import ProductList from "./components/ProductList.jsx";

export default function App() {
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [filters, setFilters] = useState({ search: "", category: "" });
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  const debouncedSearch = useDebouncedValue(filters.search, 250);

  useEffect(() => {
    listCategories()
      .then(setCategories)
      .catch(() => setLoadError("No se pudieron cargar las categorias."));
  }, []);

  const reload = useCallback(() => {
    setLoading(true);
    listProducts({ search: debouncedSearch, category: filters.category })
      .then((data) => {
        setProducts(data);
        setLoadError("");
      })
      .catch(() => setLoadError("No se pudo conectar con la API en :8000."))
      .finally(() => setLoading(false));
  }, [debouncedSearch, filters.category]);

  useEffect(() => {
    reload();
  }, [reload]);

  return (
    <main className="container">
      <h1>Catalogo de productos</h1>
      {loadError && <p className="err">{loadError}</p>}

      <div className="layout">
        <section>
          <Toolbar
            categories={categories}
            search={filters.search}
            category={filters.category}
            onChange={setFilters}
          />
          <ProductList
            products={products}
            loading={loading}
            onDeleted={(id) =>
              setProducts((ps) => ps.filter((p) => p.id !== id))
            }
          />
        </section>

        <aside>
          <ProductForm categories={categories} onCreated={reload} />
        </aside>
      </div>
    </main>
  );
}
