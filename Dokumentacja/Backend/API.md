# API Systemu Praktyk

Aplikacja udostępnia w pełni funkcjonalne REST API do zarządzania zasobami systemu. Interfejs graficzny (Swagger UI) dostępny jest pod adresem `/apidocs/`.

## Zestawienie wszystkich dostępnych endpointów

Poniżej znajduje się pełna lista zaimplementowanych ścieżek:

**Studenci:**

- `GET /api/students` - Pobiera listę wszystkich studentów
- `GET /api/students/<id>` - Pobiera szczegóły konkretnego studenta
- `POST /api/students` - Dodaje nowego studenta
- `PUT /api/students/<id>` - Aktualizuje dane studenta
- `DELETE /api/students/<id>` - Usuwa studenta

**Praktyki:**

- `GET /api/internships` - Pobiera listę praktyk (obsługuje parametr `?student_id=`)
- `POST /api/internships` - Rejestruje nową praktykę (walidacja dat chronologicznych)
- `PUT /api/internships/<id>` - Aktualizuje status istniejącej praktyki
- `DELETE /api/internships/<id>` - Usuwa praktykę z bazy

**Dokumenty:**

- `GET /api/documents` - Pobiera listę dokumentów (obsługuje parametr `?internship_id=`)
- `POST /api/documents` - Przesyła nowy dokument (wymaga istniejącej praktyki)
- `DELETE /api/documents/<id>` - Usuwa załączony dokument

---

## Kody statusów HTTP

API korzysta ze standardowych kodów odpowiedzi:

- **200 OK** - Żądanie wykonane pomyślnie.
- **201 Created** - Zasób został poprawnie utworzony.
- **400 Bad Request** - Błąd walidacji danych wejściowych (np. błędne daty).
- **404 Not Found** - Wskazany zasób nie istnieje w bazie.
- **500 Internal Server Error** - Krytyczny błąd serwera.

---

## Przykładowe zapytania (cURL)

**1. Dodawanie studenta (POST):**

```bash
curl -X POST http://localhost:5000/api/students \
-H "Content-Type: application/json" \
-d '{"imie": "Adam", "nazwisko": "Nowak", "numer_indeksu": "987654", "email": "adam@uczelnia.pl"}'
```

_(Oczekiwany status: 201 Created)_

**2. Pobieranie praktyk dla konkretnego studenta (GET z parametrem):**

```bash
curl -X GET "http://localhost:5000/api/internships?student_id=1"
```

_(Oczekiwany status: 200 OK)_

---

## Przykładowe formaty odpowiedzi JSON

Poniższe struktury odzwierciedlają realne dane zwracane przez serwer dla poszczególnych metod HTTP.

### 1. Zasób: Studenci (`/api/students`)

- **Pobranie listy wszystkich studentów (GET /api/students) - Status: 200 OK**

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

- **Utworzenie nowego studenta (POST /api/students) - Status: 201 Created**

```json
{
  "id": 3,
  "message": "Student utworzony"
}
```

### 2. Zasób: Praktyki (`/api/internships`)

- **Pobranie listy praktyk (GET /api/internships) - Status: 200 OK**

```json
[
  {
    "id": 1,
    "student_id": 1,
    "nazwa_firmy": "Google Polska",
    "data_rozpoczecia": "2026-07-01",
    "data_zakonczenia": "2026-09-30",
    "status": "Zatwierdzona"
  }
]
```

### 3. Zasób: Dokumenty (`/api/documents`)

- **Pobranie listy dokumentów (GET /api/documents) - Status: 200 OK**

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

### 4. Obsługa błędów

- **Błąd: Nie znaleziono zasobu (Status: 404 Not Found)**

```json
{
  "error": "Resource not found"
}
```
