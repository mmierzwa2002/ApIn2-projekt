const API_URL = "/api";
const AUTH_URL = "/auth";

let currentUser = null;

document.addEventListener("DOMContentLoaded", () => {
  checkSessionStatus();
});

function showAlert(message, type) {
  const alertContainer = document.getElementById("alert-container");
  alertContainer.innerHTML = `<div class="alert alert-${type} alert-dismissible fade show border-0 shadow-sm">${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>`;
}

async function checkSessionStatus() {
  try {
    const res = await fetch(`${AUTH_URL}/me`, { credentials: "include" });
    if (res.ok) {
      currentUser = await res.json();

      document.getElementById("auth-container").style.display = "none";
      document.getElementById("dashboard-container").style.display = "block";

      const badge = document.getElementById("user-profile-badge");
      badge.style.display = "block";
      document.getElementById("user-display-name").innerText =
        `Użytkownik: ${currentUser.full_name} [${currentUser.role.toUpperCase()}]`;

      enforcePermissions();
      loadAuthorizedData();
    } else {
      document
        .getElementById("auth-container")
        .style.setProperty("display", "flex", "important");
      document.getElementById("dashboard-container").style.display = "none";
      document.getElementById("user-profile-badge").style.display = "none";
    }
  } catch (error) {
    document.getElementById("auth-container").style.display = "flex";
    document.getElementById("dashboard-container").style.display = "none";
  }
}

function enforcePermissions() {
  if (currentUser.role === "student") {
    document.getElementById("tab-students-li").style.display = "none";

    const wrapper = document.getElementById("p_student_id_wrapper");
    const field = document.getElementById("p_student_id");
    if (wrapper && field) {
      wrapper.style.display = "none";
      field.value = currentUser.id;
      field.removeAttribute("required");
    }

    const pTab = document.getElementById("tab-internships-btn");
    if (pTab) {
      bootstrap.Tab.getOrCreateInstance(pTab).show();
    }
  } else {
    document.getElementById("tab-students-li").style.display = "block";
  }
}

function loadAuthorizedData() {
  if (currentUser.role !== "student") {
    loadStudents();
  }
  loadInternships();
  loadDocuments();
  loadJournal();
  loadOutcomes();
}

document
  .getElementById("local-login-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      email: document.getElementById("login_email").value,
      password: document.getElementById("login_pass").value,
    };
    try {
      const res = await fetch(`${AUTH_URL}/login/local`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        showAlert("Zalogowano pomyślnie!", "success");
        checkSessionStatus();
      } else {
        const data = await res.json();
        showAlert(data.error || "Błąd logowania", "danger");
      }
    } catch (e) {
      showAlert("Błąd połączenia z serwerem logowania.", "danger");
    }
  });

document
  .getElementById("register-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      full_name: document.getElementById("reg_name").value,
      numer_indeksu: document.getElementById("reg_indeks").value,
      email: document.getElementById("reg_email").value,
      password: document.getElementById("reg_pass").value,
    };
    try {
      const res = await fetch(`${AUTH_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (res.ok) {
        showAlert(data.message, "success");
        document.getElementById("register-form").reset();
      } else {
        showAlert(data.error, "danger");
      }
    } catch (e) {
      showAlert("Błąd połączenia podczas rejestracji.", "danger");
    }
  });

async function loadStudents() {
  try {
    const response = await fetch(`${API_URL}/students`, {
      credentials: "include",
    });
    const data = await response.json();
    const tbody = document.getElementById("students-table-body");
    tbody.innerHTML = data
      .map(
        (s) => `
        <tr>
            <td>${s.id}</td>
            <td><strong>${s.imie} ${s.nazwisko}</strong></td>
            <td>${s.numer_indeksu}</td>
            <td>${s.email}</td>
            <td><button class="btn btn-sm btn-danger" onclick="deleteResource('students', ${s.id}, loadStudents)">Usuń</button></td>
        </tr>`,
      )
      .join("");
  } catch (e) {
    console.error("Błąd ładowania studentów");
  }
}

document
  .getElementById("student-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      imie: document.getElementById("s_imie").value,
      nazwisko: document.getElementById("s_nazwisko").value,
      numer_indeksu: document.getElementById("s_indeks").value,
      email: document.getElementById("s_email").value,
    };
    await createResource("students", payload, "student-form", loadStudents);
  });

async function loadInternships() {
  try {
    const response = await fetch(`${API_URL}/internships`, {
      credentials: "include",
    });
    const data = await response.json();
    const tbody = document.getElementById("internships-table-body");
    tbody.innerHTML = data
      .map(
        (p) => `
        <tr>
            <td>${p.id}</td>
            <td><strong>${p.nazwa_firmy}</strong><br><small>ID Studenta: ${p.student_id}</small></td>
            <td>${p.data_rozpoczecia} do ${p.data_zakonczenia}</td>
            <td><span class="badge bg-secondary">${p.status}</span></td>
            <td>
                <div class="btn-group">
                    <button class="btn btn-sm btn-warning" onclick="openEditInternship(${p.id}, '${p.nazwa_firmy}', '${p.status}')">Status</button>
                    <button class="btn btn-sm btn-outline-primary" onclick="window.open('${API_URL}/generate-pdf/dziennik/${p.id}', '_blank')">📄 Dziennik</button>
                    <button class="btn btn-sm btn-outline-info" onclick="window.open('${API_URL}/generate-pdf/efekty/${p.id}', '_blank')">🎯 Efekty</button>
                    <button class="btn btn-sm btn-outline-success" onclick="window.open('${API_URL}/generate-pdf/raport/${p.id}', '_blank')">📋 Raport</button>
                    <button class="btn btn-sm btn-dark" onclick="window.open('${API_URL}/generate-pdf/zbiorcze/${p.id}', '_blank')">📦 ZIP</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteResource('internships', ${p.id}, loadInternships)">Usuń</button>
                </div>
            </td>
        </tr>`,
      )
      .join("");
  } catch (e) {
    console.error("Błąd ładowania praktyk");
  }
}

document
  .getElementById("internship-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      student_id: parseInt(document.getElementById("p_student_id").value),
      nazwa_firmy: document.getElementById("p_firma").value,
      data_rozpoczecia: document.getElementById("p_od").value,
      data_zakonczenia: document.getElementById("p_do").value,
      status: "Oczekująca",
    };
    if (payload.data_rozpoczecia > payload.data_zakonczenia) {
      return showAlert(
        "Data zakończenia nie może być wcześniejsza niż rozpoczęcia!",
        "danger",
      );
    }
    await createResource(
      "internships",
      payload,
      "internship-form",
      loadInternships,
    );
  });

function openEditInternship(id, firma, status) {
  document.getElementById("edit_p_id").value = id;
  document.getElementById("edit_p_firma").value = firma;
  document.getElementById("edit_p_status").value = status;
  new bootstrap.Modal(document.getElementById("editInternshipModal")).show();
}

document
  .getElementById("edit-internship-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("edit_p_id").value;
    const payload = { status: document.getElementById("edit_p_status").value };
    try {
      const res = await fetch(`${API_URL}/internships/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        showAlert("Status zaktualizowany pomyślnie!", "success");
        bootstrap.Modal.getInstance(
          document.getElementById("editInternshipModal"),
        ).hide();
        loadInternships();
      } else {
        showAlert("Błąd zmiany statusu.", "danger");
      }
    } catch (error) {
      showAlert("Błąd serwera API.", "danger");
    }
  });

async function loadDocuments() {
  try {
    const response = await fetch(`${API_URL}/documents`, {
      credentials: "include",
    });
    const data = await response.json();
    const tbody = document.getElementById("documents-table-body");
    tbody.innerHTML = data
      .map(
        (d) => `
        <tr>
            <td>${d.id}</td>
            <td>Praktyka: ${d.identyfikator_praktyki}</td>
            <td>${d.nazwa_dokumentu}</td>
            <td><span class="badge bg-info">${d.typ_dokumentu}</span></td>
            <td><button class="btn btn-sm btn-danger" onclick="deleteResource('documents', ${d.id}, loadDocuments)">Usuń</button></td>
        </tr>`,
      )
      .join("");
  } catch (e) {
    console.error("Błąd ładowania dokumentów");
  }
}

document
  .getElementById("document-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      identyfikator_praktyki: parseInt(
        document.getElementById("d_praktyka_id").value,
      ),
      nazwa_dokumentu: document.getElementById("d_nazwa").value,
      typ_dokumentu: document.getElementById("d_typ").value,
      komentarz_opiekuna: "Brak uwag",
    };
    await createResource("documents", payload, "document-form", loadDocuments);
  });

async function loadJournal() {
  try {
    const response = await fetch(`${API_URL}/journal`, {
      credentials: "include",
    });
    const data = await response.json();
    const tbody = document.getElementById("journal-table-body");
    tbody.innerHTML = data
      .map(
        (j) => `
            <tr>
                <td>${j.id}</td><td>Praktyka: ${j.praktyka_id}</td><td>${j.data}</td><td>${j.godziny} h</td><td>${j.opis}</td>
            </tr>`,
      )
      .join("");
  } catch (e) {
    console.error("Błąd ładowania dziennika");
  }
}

document
  .getElementById("journal-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      praktyka_id: parseInt(document.getElementById("j_praktyka_id").value),
      data: document.getElementById("j_data").value,
      godziny: parseInt(document.getElementById("j_godziny").value),
      opis: document.getElementById("j_opis").value,
    };
    await createResource("journal", payload, "journal-form", loadJournal);
  });

async function loadOutcomes() {
  try {
    const response = await fetch(`${API_URL}/outcomes`, {
      credentials: "include",
    });
    const data = await response.json();
    const tbody = document.getElementById("outcomes-table-body");
    tbody.innerHTML = data
      .map(
        (o) => `
            <tr>
                <td>${o.id}</td>
                <td>Praktyka: ${o.praktyka_id}</td>
                <td><span class="badge bg-dark">Efekt ${o.kod_efektu}</span></td>
                <td><span class="badge ${o.status === "Uzyskał" ? "bg-success" : "bg-danger"}">${o.status}</span></td>
                <td><button class="btn btn-sm btn-danger" onclick="deleteResource('outcomes', ${o.id}, loadOutcomes)">Usuń</button></td>
            </tr>`,
      )
      .join("");
  } catch (e) {
    console.error("Błąd ładowania efektów");
  }
}

document
  .getElementById("outcome-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      praktyka_id: parseInt(document.getElementById("o_praktyka_id").value),
      kod_efektu: document.getElementById("o_efekt_id").value,
      status: document.getElementById("o_status").value,
    };
    await createResource("outcomes", payload, "outcome-form", loadOutcomes);
  });

async function createResource(endpoint, payload, formId, reloadFunction) {
  try {
    const res = await fetch(`${API_URL}/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      showAlert("Rekord zapisany pomyślnie!", "success");
      document.getElementById(formId).reset();
      reloadFunction();
    } else {
      const data = await res.json();
      showAlert(
        `Błąd API: ${data.error || "Operacja odrzucona przez serwer"}`,
        "danger",
      );
    }
  } catch (error) {
    showAlert("Błąd komunikacji z API backendu.", "danger");
  }
}

async function deleteResource(endpoint, id, reloadFunction) {
  if (!confirm("Czy na pewno chcesz bezpowrotnie usunąć ten rekord?")) return;
  try {
    const res = await fetch(`${API_URL}/${endpoint}/${id}`, {
      method: "DELETE",
      credentials: "include",
    });
    if (res.ok) {
      showAlert("Rekord został pomyślnie usunięty.", "success");
      reloadFunction();
    } else {
      showAlert(
        "Błąd usuwania. Brak autoryzacji roli administracyjnej.",
        "danger",
      );
    }
  } catch (error) {
    showAlert("Błąd połączenia z serwerem.", "danger");
  }
}
