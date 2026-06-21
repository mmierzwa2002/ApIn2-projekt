# API Systemu Rozliczania Praktyk

Aplikacja udostępnia REST API do zarządzania zasobami systemu praktyk. Interfejs graficzny (Swagger UI) dostępny jest pod adresem `/apidocs/`, a pełna specyfikacja w pliku `swagger.yaml`.

**Uwierzytelnianie:** wszystkie endpointy wymagają zalogowanego użytkownika (sesja Flask-Login – ciasteczko `session`). Większość operacji jest dodatkowo ograniczona rolą: `student`, `zopz`, `uopz`, `dyrektor`, `administrator`.

**Format:** endpointy CRUD (`students`, `internships`, `documents`, `outcomes`, `firms`, `journal`, `pdf`) przyjmują/zwracają JSON. Endpointy procesowe (workflow podpisów, formularze załączników) przyjmują dane formularzowe (`x-www-form-urlencoded`) i zwracają przekierowanie z komunikatem (są wywoływane z interfejsu) lub JSON.

---

## Zestawienie wszystkich endpointów

### Studenci (`/api/students`)

- `GET /api/students` – lista studentów _(role personelu)_
- `GET /api/students/<id>` – szczegóły studenta
- `POST /api/students` – tworzy studenta _(administrator, dyrektor)_
- `PUT /api/students/<id>` – aktualizuje studenta _(administrator, dyrektor)_
- `DELETE /api/students/<id>` – usuwa studenta _(administrator)_

### Praktyki (`/api/internships`)

- `GET /api/internships` – lista praktyk (student widzi własne, personel wszystkie)
- `POST /api/internships` – rejestruje praktykę _(administrator, uopz, dyrektor)_
- `DELETE /api/internships/<id>` – usuwa praktykę wraz z dokumentami potomnymi _(administrator)_

### Praktyki – workflow podpisów i formularzy

- `POST /api/internships/<id>/sign` – uniwersalny podpis dokumentu (pole `dokument`)
- `POST /api/internships/<id>/meta` – metadane Porozumienia, Zał. 1 _(administrator, uopz)_
- `POST /api/internships/<id>/zal2a` – Program i harmonogram, Zał. 2a _(zopz)_
- `POST /api/internships/<id>/zal2a/reject` – odrzuca Zał. 2a _(uopz)_
- `POST /api/internships/<id>/zal7` – składa Sprawozdanie, Zał. 7 _(student)_
- `POST /api/internships/<id>/zal32/zopz` – Karta str. 2: ocena zakładowa _(zopz)_
- `POST /api/internships/<id>/zal32/uopz` – Karta str. 2: ocena uczelniana _(uopz)_
- `POST /api/internships/<id>/zal4/zopz` – potwierdzenie 13 efektów _(zopz)_
- `POST /api/internships/<id>/zal4/uopz` – opinia UOPZ do Zał. 4 _(uopz)_
- `POST /api/internships/<id>/zal5` – kwestionariusz ankiety, Zał. 5 _(student)_
- `POST /api/internships/<id>/zal8` – Protokół Zaliczenia, Zał. 8 _(dyrektor)_
- `POST /api/internships/<id>/usos` – podpis UOPZ + wpis do USOS, zakończenie _(uopz)_
- `POST /api/internships/<id>/reset/zal4` – cofa potwierdzenie efektów _(administrator)_

### Dokumenty (`/api/documents`)

- `GET /api/documents` – lista dokumentów (parametr `?internship_id=`)
- `POST /api/documents` – dodaje dokument (wymaga istniejącej praktyki)
- `DELETE /api/documents/<id>` – usuwa dokument _(administrator, dyrektor)_

### Dziennik (`/api/journal`)

- `GET /api/journal` – lista wpisów (parametr `?internship_id=`)
- `POST /api/journal/add` – dodaje wpis _(student)_
- `POST /api/journal/fill_test` – wypełnia dziennik danymi testowymi
- `POST /api/journal/undo_last` – cofa ostatni wpis _(student)_
- `DELETE /api/journal/<id>` – usuwa wpis

### Efekty uczenia się (`/api/outcomes`)

- `GET /api/outcomes` – lista potwierdzeń (parametr `?internship_id=`)
- `POST /api/outcomes` – zapisuje potwierdzenie efektu
- `DELETE /api/outcomes/<id>` – usuwa potwierdzenie

### Firmy (`/api/firms`)

- `GET /api/firms` – lista firm
- `POST /api/firms` – dodaje firmę _(administrator, uopz)_
- `DELETE /api/firms/<id>` – usuwa firmę _(administrator, uopz)_

### Generowanie PDF (`/api/pdf`)

- `GET /api/pdf/<id>/<zal_key>` – pojedynczy załącznik jako PDF (klucze: `zal1, zal2a, zal31, zal32, zal6, zal7, zal4, zal5, zal8`)
- `POST /api/pdf/<id>/zip` – wybrane załączniki jako archiwum ZIP (pole `zalaczniki`)
- `GET /api/pdf/generate-pdf/<id>` – wszystkie dostępne załączniki jako ZIP

---

## Kody statusów HTTP

- **200 OK** – żądanie wykonane pomyślnie
- **201 Created** – zasób utworzony
- **302 Found** – przekierowanie po operacji formularzowej (z komunikatem flash)
- **400 Bad Request** – błąd walidacji danych wejściowych
- **403 Forbidden** – brak uprawnień roli lub niespełniony warunek poprzedzający w workflow
- **404 Not Found** – zasób nie istnieje
- **500 Internal Server Error** – błąd serwera

Błędy zwracane są w jednolitym formacie JSON (`app/api/errors.py`):

```json
{ "error": "Resource not found" }
```

---

## Przykładowe zapytania (cURL)

**1. Utworzenie studenta (POST):**

```bash
curl -X POST http://localhost:5000/api/students \
  -H "Content-Type: application/json" \
  -b "session=<cookie>" \
  -d '{"imie":"Adam","nazwisko":"Nowak","numer_indeksu":"987654","email":"adam@uczelnia.pl"}'
```

_(Oczekiwany status: 201 Created)_

**2. Rejestracja praktyki (POST) – wymaga istniejącego studenta i firmy, dokładnie 120 dni roboczych:**

```bash
curl -X POST http://localhost:5000/api/internships \
  -H "Content-Type: application/json" \
  -b "session=<cookie>" \
  -d '{"id_studenta":1,"id_firmy":1,"data_od":"2026-07-01","data_do":"2026-12-15"}'
```

_(Oczekiwany status: 201 Created; 400 jeśli zakres ≠ 120 dni roboczych)_

**3. Lista wpisów dziennika konkretnej praktyki (GET z parametrem):**

```bash
curl -X GET "http://localhost:5000/api/journal?internship_id=1" -b "session=<cookie>"
```

_(Oczekiwany status: 200 OK)_

**4. Pobranie pojedynczego załącznika jako PDF:**

```bash
curl -X GET "http://localhost:5000/api/pdf/1/zal8" -b "session=<cookie>" -o protokol.pdf
```

---

## Przykładowe formaty odpowiedzi JSON

### Studenci – `GET /api/students` (200 OK)

```json
[
  {
    "id": 1,
    "imie": "Jan",
    "nazwisko": "Kowalski",
    "numer_indeksu": "123456",
    "email": "jan@student.ans-elblag.pl"
  }
]
```

### Praktyki – `GET /api/internships` (200 OK)

```json
[
  {
    "id": 1,
    "id_studenta": 1,
    "nazwa_firmy": "ABC Software Sp. z o.o.",
    "data_od": "2026-07-01",
    "data_do": "2026-12-15",
    "faza": 4,
    "status": "roboczy",
    "podpisy": {
      "zal1_zopz": true,
      "zal1_dyrektor": true,
      "zal2a_zopz": true,
      "zal2a_student": true,
      "zal2a_uopz": true,
      "zal31_dyrektor": true,
      "zal32_zgloszenie_zopz": true,
      "zal32_bhp_zopz": true,
      "dziennik_zatwierdzony": true,
      "zal4_zopz": true,
      "zal4_uopz": true,
      "zal3_strona2_zopz": true,
      "zal3_strona2_uopz": true,
      "zal7_student": true,
      "zal7_zopz": true,
      "zal8_dyrektor": true
    }
  }
]
```

### Dokumenty – `GET /api/documents` (200 OK)

```json
[
  {
    "id": 1,
    "identyfikator_praktyki": 1,
    "nazwa_dokumentu": "Skierowanie_Kowalski.pdf",
    "typ_dokumentu": "Skierowanie",
    "data_przeslania": "2026-05-26",
    "status_weryfikacji": "Weryfikacja",
    "komentarz_opiekuna": "Brak uwag formalnych."
  }
]
```

### Dziennik – `GET /api/journal?internship_id=1` (200 OK)

```json
[
  {
    "id": 1,
    "id_formularza": 1,
    "nr_dnia": 1,
    "data": "2026-07-01",
    "nr_efektow": "01, 05",
    "opis": "Zapoznanie ze strukturą firmy i regulaminem."
  }
]
```

### Efekty – `GET /api/outcomes?internship_id=1` (200 OK)

```json
[{ "id": 1, "id_formularza": 1, "id_efektu": 1, "czy_uzyskany": 1 }]
```

### Firmy – `GET /api/firms` (200 OK)

```json
[
  {
    "id": 1,
    "nazwa": "ABC Software Sp. z o.o.",
    "adres": "Elbląg",
    "przedstawiciel": "Piotr Zieliński"
  }
]
```

### Obsługa błędów (404 Not Found)

```json
{ "error": "Resource not found" }
```
