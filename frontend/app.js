const API_URL = "http://localhost:5000/api";

document.addEventListener("DOMContentLoaded", () => {
  loadStudents();
  loadInternships();
  loadDocuments();
});

function showAlert(message, type) {
  const alertContainer = document.getElementById("alert-container");
  alertContainer.innerHTML = `<div class="alert alert-${type} alert-dismissible fade show">${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>`;
}

async function loadStudents() {
  try {
    const response = await fetch(`${API_URL}/students`);
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
    const response = await fetch(`${API_URL}/internships`);
    const data = await response.json();
    const tbody = document.getElementById("internships-table-body");
    tbody.innerHTML = data
      .map(
        (p) => `
            <tr>
                <td>${p.id}</td>
                <td><strong>${p.nazwa_firmy}</strong><br><small>Student ID: ${p.student_id}</small></td>
                <td>${p.data_rozpoczecia} do ${p.data_zakonczenia}</td>
                <td><span class="badge bg-secondary">${p.status}</span></td>
                <td><button class="btn btn-sm btn-danger" onclick="deleteResource('internships', ${p.id}, loadInternships)">Usuń</button></td>
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
      return showAlert("Data zakończenia nie może być wcześniejsza!", "danger");
    }
    await createResource(
      "internships",
      payload,
      "internship-form",
      loadInternships,
    );
  });

async function loadDocuments() {
  try {
    const response = await fetch(`${API_URL}/documents`);
    const data = await response.json();
    const tbody = document.getElementById("documents-table-body");
    tbody.innerHTML = data
      .map(
        (d) => `
            <tr>
                <td>${d.id}</td>
                <td>Praktyka: ${d.identyfikator_praktyki}</td>
                <td>${d.nazwa_dokumentu}</td>
                <td>${d.typ_dokumentu}</td>
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

async function createResource(endpoint, payload, formId, reloadFunction) {
  try {
    const res = await fetch(`${API_URL}/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      showAlert("Zapisano pomyślnie!", "success");
      document.getElementById(formId).reset();
      reloadFunction();
    } else {
      const data = await res.json();
      showAlert(`Błąd API: ${data.error || "Nieprawidłowe dane"}`, "danger");
    }
  } catch (error) {
    showAlert("Błąd połączenia z serwerem!", "danger");
  }
}

async function deleteResource(endpoint, id, reloadFunction) {
  if (!confirm("Czy na pewno usunąć ten rekord?")) return;
  try {
    const res = await fetch(`${API_URL}/${endpoint}/${id}`, {
      method: "DELETE",
    });
    if (res.ok) {
      showAlert("Usunięto rekord.", "success");
      reloadFunction();
    } else {
      showAlert("Błąd podczas usuwania.", "danger");
    }
  } catch (error) {
    showAlert("Błąd połączenia!", "danger");
  }
}
