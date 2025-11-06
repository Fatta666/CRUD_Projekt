const API_URL = "/produkty";
const AUTH_URL = "/";
let token = localStorage.getItem("access_token") || null;

const logoutBtn = document.getElementById("logoutBtn");
const loginBtn = document.getElementById("loginBtn");
const registerBtn = document.getElementById("registerBtn");
//
function updateAuthUI() {
  if (token) {
    logoutBtn.style.display = "inline-block";
    loginBtn.disabled = true;
    registerBtn.disabled = true;
  } else {
    logoutBtn.style.display = "none";
    loginBtn.disabled = false;
    registerBtn.disabled = false;
  }
}
updateAuthUI();

function showBackendErrors(resJson) {
  if (!resJson) return;
  let msg = resJson.message || resJson.error || resJson.msg || "Błąd";
  if (resJson.fieldErrors && Array.isArray(resJson.fieldErrors)) {
    msg += "<br/><ul style='text-align:left;'>";
    resJson.fieldErrors.forEach((fe) => {
      msg += `<li>${fe.field}: ${fe.message} (${fe.code || ""})</li>`;
    });
    msg += "</ul>";
  }
  Swal.fire({ title: "Błąd", html: msg, icon: "error" });
}

document.getElementById("authForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const login = document.getElementById("login").value;
  const password = document.getElementById("password").value;

  if (e.submitter.id === "loginBtn") {
    const res = await fetch(`${AUTH_URL}login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ login, password }),
    });
    const data = await res.json();
    if (res.status === 200) {
      token = data.access_token;
      localStorage.setItem("access_token", token);
      Swal.fire("Sukces!", "Zalogowano!", "success");
      updateAuthUI();
      loadProdukty();
    } else {
      showBackendErrors(data);
    }
  }
});

registerBtn.addEventListener("click", async () => {
  const login = document.getElementById("login").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${AUTH_URL}register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ login, password }),
  });
  const data = await res.json();
  if (res.status === 201) {
    Swal.fire("Sukces", "Zarejestrowano użytkownika", "success");
  } else {
    showBackendErrors(data);
  }
});

logoutBtn.addEventListener("click", () => {
  localStorage.removeItem("access_token");
  token = null;
  updateAuthUI();
  Swal.fire("Wylogowano", "Zostałeś wylogowany.", "info");
});

async function loadProdukty() {
  const res = await fetch(API_URL);
  const produkty = await res.json();
  const tbody = document.getElementById("produktyList");
  tbody.innerHTML = "";

  if (!produkty.length) {
    tbody.innerHTML = `<tr><td colspan="8">Brak produktów w bazie.</td></tr>`;
    return;
  }

  produkty.forEach((p) => {
    const row = document.createElement("tr");
    row.innerHTML = `
            <td>${p.id}</td>
            <td>${p.nazwa}</td>
            <td>${p.cena}</td>
            <td>${p.kategoria}</td>
            <td>${p.ilosc}</td>
            <td>${p.producent || "-"}</td>
            <td>${p.data_dodania || "-"}</td>
            <td>
                <button class="btn btn-sm btn-warning" onclick="editProdukt(${
                  p.id
                }, '${escapeHtml(p.nazwa)}', ${p.cena}, '${escapeHtml(
      p.kategoria
    )}', ${p.ilosc}, '${escapeHtml(p.producent || "")}', '${
      p.data_dodania || ""
    }')">Edytuj</button>
                <button class="btn btn-sm btn-danger" onclick="deleteProdukt(${
                  p.id
                })">Usuń</button>
            </td>
        `;
    tbody.appendChild(row);
  });
}

function escapeHtml(s) {
  if (!s && s !== 0) return "";
  return String(s).replace(/'/g, "\\'").replace(/"/g, "&quot;");
}

document.getElementById("productForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!token) return Swal.fire("Błąd", "Musisz być zalogowany!", "error");

  // HTML5 validation
  const form = e.target;
  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }
  // dodatkowa walidacja daty: nie późniejsza niż dziś
  const dataDod = document.getElementById("data_dodania").value;
  if (dataDod) {
    const chosen = new Date(dataDod);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (chosen > today) {
      return Swal.fire(
        "Błąd",
        "Data nie może być późniejsza niż dziś",
        "error"
      );
    }
  }

  const id = document.getElementById("productId").value;
  const payload = {
    nazwa: document.getElementById("nazwa").value,
    cena: parseFloat(document.getElementById("cena").value),
    kategoria: document.getElementById("kategoria").value,
    ilosc: parseInt(document.getElementById("ilosc").value),
    producent: document.getElementById("producent").value,
    data_dodania: document.getElementById("data_dodania").value || null,
  };
  const method = id ? "PUT" : "POST";
  const url = id ? `${API_URL}/${id}` : API_URL;

  const res = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  const data = await res.json();
  if (res.status >= 200 && res.status < 300) {
    e.target.reset();
    document.getElementById("productId").value = "";
    loadProdukty();
    Swal.fire("Sukces", "Zapisano produkt", "success");
  } else {
    showBackendErrors(data);
  }
});

async function deleteProdukt(id) {
  if (!token) return Swal.fire("Błąd", "Musisz być zalogowany!", "error");
  Swal.fire({
    title: "Na pewno chcesz usunąć ten produkt?",
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: "Tak",
    cancelButtonText: "Nie",
  }).then(async (result) => {
    if (result.isConfirmed) {
      const res = await fetch(`${API_URL}/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.status === 200) {
        loadProdukty();
        Swal.fire("Usunięto!", "Produkt został usunięty.", "success");
      } else {
        const data = await res.json();
        showBackendErrors(data);
      }
    }
  });
}

function editProdukt(
  id,
  nazwa,
  cena,
  kategoria,
  ilosc,
  producent,
  data_dodania
) {
  if (!token) return Swal.fire("Błąd", "Musisz być zalogowany!", "error");
  document.getElementById("productId").value = id;
  document.getElementById("nazwa").value = nazwa;
  document.getElementById("cena").value = cena;
  document.getElementById("kategoria").value = kategoria;
  document.getElementById("ilosc").value = ilosc;
  document.getElementById("producent").value = producent;
  document.getElementById("data_dodania").value = data_dodania;
}

loadProdukty();
