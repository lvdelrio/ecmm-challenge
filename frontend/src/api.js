const BASE_URL = "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(status, data) {
    super(`HTTP ${status}`);
    this.status = status;
    this.data = data;
  }
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (res.status === 204) return null;

  const data = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(res.status, data);
  return data;
}

export function listProducts({ search = "", category = "" } = {}) {
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (category) params.set("category", category);
  const qs = params.toString();
  return request(`/products/${qs ? `?${qs}` : ""}`);
}

export function getProduct(id) {
  return request(`/products/${id}/`);
}

export function createProduct(payload) {
  return request("/products/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateProduct(id, payload) {
  return request(`/products/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteProduct(id) {
  return request(`/products/${id}/`, { method: "DELETE" });
}

export function listCategories() {
  return request("/categories/");
}

export function createCategory(name) {
  return request("/categories/", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}
