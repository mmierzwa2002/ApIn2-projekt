# Dokumentacja techniczna frontendu

Dokument opisuje warstwę interfejsu użytkownika aplikacji do rozliczania praktyk
zawodowych (ANS Elbląg).

## Architektura

Frontend zrealizowano w modelu **Server-Side Rendering (SSR)** – szablony Jinja2
renderowane przez backend Flask. Nie ma osobnego frameworka JS (SPA); strony są
generowane na serwerze i wzbogacone niewielką ilością skryptów inline. Takie podejście
upraszcza wdrożenie i zapewnia spójność danych z backendem.

## Struktura katalogów

```
templates/                 # widoki Jinja2 (HTML)
├── base.html              # szablon bazowy: nawigacja, motyw, stopka
├── login.html             # logowanie + rejestracja
├── pending.html           # konto oczekujące na zatwierdzenie
├── dashboard.html         # pulpit (konsola wg roli)
├── admin_approvals.html   # zatwierdzanie kont (administrator)
└── formularze/            # widoki załączników 1–8
    ├── zal1.html          # Porozumienie
    ├── zal2a.html         # Program i harmonogram
    ├── zal31.html         # Karta praktyki – strona 1
    ├── zal32.html         # Karta praktyki – strona 2
    ├── zal4.html          # Potwierdzenie efektów
    ├── zal5.html          # Ankieta
    ├── zal6.html          # Dziennik praktyk
    ├── zal7.html          # Sprawozdanie
    └── zal8.html          # Protokół zaliczenia

static/
└── css/
    └── style.css          # jeden arkusz stylów całej aplikacji
```

## Komponenty interfejsu

- **Szablon bazowy (`base.html`)** – wspólny nagłówek z nawigacją, przełącznik motywu
  jasny/ciemny (zapamiętywany w `localStorage`, atrybut `data-theme` na elemencie `<html>`),
  blok `{% block content %}` dla treści podstron oraz obsługa komunikatów `flash`.
- **Pulpit (`dashboard.html`)** – adaptacyjna konsola, której zawartość zależy od roli
  zalogowanego użytkownika:
  - *student* – karta postępu (fazy 1–4), stan załączników, panel pobierania PDF/ZIP;
  - *personel (UOPZ/ZOPZ/Dyrektor)* – tabela praktyk z dokumentami i akcjami zależnymi od fazy;
  - *administrator* – zarządzanie kontami, praktykami i firmami.
- **Widoki załączników (`formularze/*.html`)** – każdy łączy podgląd dokumentu w układzie
  zbliżonym do oryginału urzędowego z panelami akcji (podpis, ocena) widocznymi zależnie od
  roli i fazy. Wszystkie mają reguły `@media print` oraz przycisk „Drukuj / PDF".
- **Komponenty wspólne (klasy CSS)** – `academic-card`, `academic-table`, `btn-academic`,
  `badge`, `doc-link`, `dok-pieczatka`, `form-group`, `custom-input` / `custom-select`.

## Komunikacja z API

- **Formularze** wysyłają dane metodą `POST` (kodowanie `x-www-form-urlencoded`) do
  endpointów `/api/*`; po zapisie serwer wykonuje przekierowanie (`redirect`) i wyświetla
  komunikat `flash` (wzorzec Post/Redirect/Get).
- **Dane do widoków** pobierane są bezpośrednio w warstwie serwera (ORM SQLAlchemy) i
  wstrzykiwane do szablonów – nie ma osobnych zapytań AJAX do renderowania stron.
- **Generowanie dokumentów** – odnośniki/formularze do `/api/pdf/<id>/<zal_key>` (pojedynczy
  PDF), `/api/pdf/<id>/zip` (wybrane załączniki) oraz `/api/pdf/generate-pdf/<id>` (komplet).
- **Walidacja** dwuwarstwowa: po stronie klienta atrybutami HTML5 (`required`, `type`,
  `minlength`, `min`/`max`), a po stronie serwera regułami biznesowymi (120 dni, 13 efektów,
  skala ocen 2–5), z komunikatami `flash`.
- Pełna specyfikacja endpointów: `swagger.yaml` oraz `Dokumentacja/Backend/API.md`.

## Użyte technologie

- **Jinja2** – silnik szablonów (SSR), dziedziczenie przez `base.html`.
- **HTML5** – formularze z natywną walidacją.
- **CSS3** – własny arkusz `style.css`; zmienne CSS (custom properties) dla motywów
  jasny/ciemny, układy `flexbox` i `grid`, reguły responsywne `@media`, style `@media print`.
- **JavaScript (vanilla, inline)** – przełącznik motywu, rozwijanie paneli (`classList.toggle`),
  wywołanie `window.print()`. Bez zewnętrznych bibliotek (brak Bootstrap/jQuery/CDN).
- **Flask-Login** – sesyjne uwierzytelnianie; widoki chronione zależnie od roli.

## Instrukcja uruchomienia (część frontendowa)

Frontend uruchamia się razem z backendem (jeden serwer Flask):

1. Aktywuj środowisko i zainstaluj zależności:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Skonfiguruj połączenie z bazą w pliku `.env` (zmienna `DATABASE_URL`, np. PostgreSQL).
3. Uruchom aplikację:
   ```bash
   .\venv\Scripts\python.exe run.py
   ```
   Przy starcie wykonywane jest `ensure_schema()` (uzupełnienie brakujących kolumn) oraz
   seed kont testowych.
4. Otwórz w przeglądarce `http://localhost:5000/auth/login`.
5. (Opcjonalnie) załaduj dane demonstracyjne (zakończona przykładowa praktyka):
   `.\venv\Scripts\python.exe seed_demo.py` – konto `demo@ans.elblag.pl` / `Demo1234!`.

### Konta testowe

Zakładane automatycznie przy starcie aplikacji:

| Rola | E-mail | Hasło |
|---|---|---|
| Administrator | `admin@test.local` | `admin123` |
| UOPZ (opiekun uczelniany) | `uopz@test.local` | `uopz123` |
| ZOPZ (opiekun zakładowy) | `zopz@test.local` | `zopz123` |
| Dyrektor | `dyrektor@test.local` | `dyrektor123` |
| Student | `student@test.local` | `student123` |
| Konto oczekujące na zatwierdzenie | `pending@test.local` | `pending123` |

Interfejs nie wymaga osobnego procesu budowania (brak bundlera) – wszystkie zasoby
serwowane są statycznie przez Flask z katalogu `static/`.
