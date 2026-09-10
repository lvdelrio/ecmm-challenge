import { useState } from "react";
import { createProduct, ApiError } from "../api.js";

const EMPTY = {
  name: "",
  description: "",
  price: "",
  stock: "",
  category: "",
};

export default function ProductForm({ categories, onCreated }) {
  const [form, setForm] = useState(EMPTY);
  const [errors, setErrors] = useState(null);
  const [saving, setSaving] = useState(false);

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setErrors(null);
    setSaving(true);
    try {
      const created = await createProduct({
        name: form.name,
        description: form.description,
        price: form.price,
        stock: form.stock === "" ? null : Number(form.stock),
        category: form.category === "" ? null : Number(form.category),
      });
      setForm(EMPTY);
      onCreated(created);
    } catch (err) {
      if (err instanceof ApiError && err.data) {
        setErrors(err.data);
      } else {
        setErrors({ detail: ["No se pudo conectar con la API."] });
      }
    } finally {
      setSaving(false);
    }
  }

  const fieldError = (name) => errors?.[name]?.join(" ");

  return (
    <form className="card" onSubmit={handleSubmit} noValidate>
      <h2>Nuevo producto</h2>

      <label>
        Nombre *
        <input
          value={form.name}
          onChange={(e) => update("name", e.target.value)}
        />
        {fieldError("name") && <span className="err">{fieldError("name")}</span>}
      </label>

      <label>
        Descripcion
        <textarea
          rows={2}
          value={form.description}
          onChange={(e) => update("description", e.target.value)}
        />
      </label>

      <div className="row">
        <label>
          Precio *
          <input
            type="number"
            min="0"
            step="0.01"
            value={form.price}
            onChange={(e) => update("price", e.target.value)}
          />
          {fieldError("price") && <span className="err">{fieldError("price")}</span>}
        </label>

        <label>
          Stock *
          <input
            type="number"
            min="0"
            step="1"
            value={form.stock}
            onChange={(e) => update("stock", e.target.value)}
          />
          {fieldError("stock") && <span className="err">{fieldError("stock")}</span>}
        </label>
      </div>

      <label>
        Categoria *
        <select
          value={form.category}
          onChange={(e) => update("category", e.target.value)}
        >
          <option value="">Selecciona...</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        {fieldError("category") && (
          <span className="err">{fieldError("category")}</span>
        )}
      </label>

      {fieldError("detail") && <p className="err">{fieldError("detail")}</p>}

      <button type="submit" disabled={saving}>
        {saving ? "Guardando..." : "Crear producto"}
      </button>
    </form>
  );
}
