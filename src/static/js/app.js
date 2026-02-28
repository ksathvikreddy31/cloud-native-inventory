function send(action) {
  fetch(`/api/${document.getElementById("module").value}/${action}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      db: document.getElementById("db").value,
      name: document.getElementById("name").value,
      user_id: 1,
      product_id: 1,
      stock: 10,
      products: [{ product_id: 1, qty: 1 }],
    }),
  })
    .then((r) => r.json())
    .then((d) => {
      document.getElementById("output").innerHTML = JSON.stringify(d);
    });
}
