const API_URL = "/produkty";
const AUTH_URL = "/";
let token = localStorage.getItem('access_token') || null;

document.getElementById("authForm").addEventListener("submit", async e => {
    e.preventDefault();
    const login = document.getElementById("login").value;
    const password = document.getElementById("password").value;

    if (e.submitter.id === "loginBtn") {
        const res = await fetch(`${AUTH_URL}login`, {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({login, password})
        });
        const data = await res.json();
        if (res.status === 200) {
            token = data.access_token;
            localStorage.setItem('access_token', token);
            Swal.fire('Sukces!', 'Zalogowano!', 'success');
            loadProdukty();
        } else {
            Swal.fire('Błąd', data.msg, 'error');
        }
    }
});

document.getElementById("registerBtn").addEventListener("click", async () => {
    const login = document.getElementById("login").value;
    const password = document.getElementById("password").value;

    const res = await fetch(`${AUTH_URL}register`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({login, password})
    });
    const data = await res.json();
    Swal.fire(data.msg);
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

    produkty.forEach(p => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${p.id}</td>
            <td>${p.nazwa}</td>
            <td>${p.cena}</td>
            <td>${p.kategoria}</td>
            <td>${p.ilosc}</td>
            <td>${p.producent || '-'}</td>
            <td>${p.data_dodania || '-'}</td>
            <td>
                <button class="btn btn-sm btn-warning" onclick="editProdukt(${p.id}, '${p.nazwa}', ${p.cena}, '${p.kategoria}', ${p.ilosc}, '${p.producent || ''}', '${p.data_dodania || ''}')">Edytuj</button>
                <button class="btn btn-sm btn-danger" onclick="deleteProdukt(${p.id})">Usuń</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

document.getElementById("productForm").addEventListener("submit", async e => {
    e.preventDefault();
    if (!token) return Swal.fire('Błąd','Musisz być zalogowany!','error');

    const id = document.getElementById("productId").value;
    const data = {
        nazwa: document.getElementById("nazwa").value,
        cena: parseFloat(document.getElementById("cena").value),
        kategoria: document.getElementById("kategoria").value,
        ilosc: parseInt(document.getElementById("ilosc").value),
        producent: document.getElementById("producent").value,
        data_dodania: document.getElementById("data_dodania").value
    };
    const method = id ? "PUT" : "POST";
    const url = id ? `${API_URL}/${id}` : API_URL;

    await fetch(url, {
        method,
        headers: {
            "Content-Type":"application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(data)
    });

    e.target.reset();
    document.getElementById("productId").value = "";
    loadProdukty();
});

function deleteProdukt(id) {
    if (!token) return Swal.fire('Błąd','Musisz być zalogowany!','error');
    Swal.fire({
        title: 'Na pewno chcesz usunąć ten produkt?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Tak',
        cancelButtonText: 'Nie'
    }).then(async result => {
        if (result.isConfirmed) {
            await fetch(`${API_URL}/${id}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });
            loadProdukty();
            Swal.fire('Usunięto!','Produkt został usunięty.','success');
        }
    });
}

function editProdukt(id, nazwa, cena, kategoria, ilosc, producent, data_dodania) {
    document.getElementById("productId").value = id;
    document.getElementById("nazwa").value = nazwa;
    document.getElementById("cena").value = cena;
    document.getElementById("kategoria").value = kategoria;
    document.getElementById("ilosc").value = ilosc;
    document.getElementById("producent").value = producent;
    document.getElementById("data_dodania").value = data_dodania;
}

loadProdukty();
