const currency = new Intl.NumberFormat("es-CL", {
  style: "currency",
  currency: "CLP",
});

export function formatCurrency(value) {
  return currency.format(Number(value));
}

export function formatDate(value) {
  return new Date(value).toLocaleDateString("es-CL");
}
