import { deleteProduct } from "../api.js";
import { formatCurrency, formatDate } from "../lib/format.js";

export default function ProductList({ products, loading, onDeleted }) {
  if (loading) return <p>Cargando...</p>;
  if (products.length === 0) return <p>No hay productos que coincidan.</p>;

  async function handleDelete(id) {
    if (!confirm("¿Eliminar este producto?")) return;
    await deleteProduct(id);
    onDeleted(id);
  }

  return (
    <table className="table">
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Categoria</th>
          <th className="num">Precio</th>
          <th className="num">Stock</th>
          <th>Creado</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {products.map((p) => (
          <tr key={p.id}>
            <td>
              <strong>{p.name}</strong>
              {p.description && <div className="muted">{p.description}</div>}
            </td>
            <td>{p.category_name}</td>
            <td className="num">{formatCurrency(p.price)}</td>
            <td className="num">{p.stock}</td>
            <td>{formatDate(p.created_at)}</td>
            <td>
              <button className="link" onClick={() => handleDelete(p.id)}>
                Eliminar
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
