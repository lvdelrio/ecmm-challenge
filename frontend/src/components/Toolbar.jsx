export default function Toolbar({ categories, search, category, onChange }) {
  return (
    <div className="toolbar">
      <input
        type="search"
        placeholder="Buscar por nombre..."
        value={search}
        onChange={(e) => onChange({ search: e.target.value, category })}
      />
      <select
        value={category}
        onChange={(e) => onChange({ search, category: e.target.value })}
      >
        <option value="">Todas las categorias</option>
        {categories.map((c) => (
          <option key={c.id} value={c.id}>
            {c.name}
          </option>
        ))}
      </select>
    </div>
  );
}
