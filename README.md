# System Rozliczania Praktyk (ApIn2-projekt)

Autor: **Michał Mierzwa, nr albumu 21273**
Przedmiot: Aplikacje Internetowe II — projekt zaliczeniowy.

Aplikacja webowa do obsługi dokumentacji studenckich praktyk zawodowych (ANS Elbląg):
prowadzi praktykę przez cały proces — od porozumienia, przez dziennik i sprawozdanie,
aż po protokół zaliczenia — i generuje komplet załączników urzędowych (Zał. 1–8) w PDF.

## Funkcje

- **Workflow 4 faz** praktyki (Inicjacja → Realizacja → Podsumowanie → Zaliczenie)
  sterowany podpisami kolejnych załączników.
- **Role i uprawnienia:** student, ZOPZ (opiekun zakładowy), UOPZ (opiekun uczelniany),
  dyrektor, administrator oraz konto oczekujące na zatwierdzenie.
- **Formularze załączników 1–8** z walidacją (m.in. 120 dni roboczych, 13 efektów uczenia,
  skala ocen 2–5).
- **Dziennik praktyki** (120 wpisów dziennych z przypisaniem efektów).
- **Generowanie PDF** pojedynczych załączników oraz archiwum ZIP (headless Edge/Chromium,
  z `xhtml2pdf` jako rozwiązaniem zapasowym).
- **REST API** (38 endpointów) z dokumentacją Swagger UI pod `/apidocs/`.
- **Logowanie** lokalne oraz przez Microsoft OAuth.

## Technologie

- Backend: **Python / Flask**, **SQLAlchemy**, **Flask-Login**
- Baza danych: **PostgreSQL** (schemat uzupełniany automatycznie przez `ensure_schema()`)
- Frontend: **SSR (Jinja2)**, HTML5, CSS3, vanilla JavaScript (bez frameworków/CDN)
- Generowanie PDF: headless Edge/Chromium (`--print-to-pdf`) + `xhtml2pdf`

## Uruchomienie

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
# skonfiguruj DATABASE_URL w pliku .env (PostgreSQL)
.\venv\Scripts\python.exe run.py
```

Aplikacja startuje pod `http://localhost:5000/auth/login`. Przy starcie wykonywane jest
`ensure_schema()` i seed kont testowych. Dane demonstracyjne:
`.\venv\Scripts\python.exe seed_demo.py` (konto `demo@ans.elblag.pl` / `Demo1234!`).

## Struktura projektu

```
app/            # logika backendu (modele, API, auth)
templates/      # widoki Jinja2 (frontend SSR)
static/css/     # arkusz stylów aplikacji
Dokumentacja/   # dokumentacja projektu (API, frontend, diagramy, baza)
run.py          # punkt wejścia aplikacji
seed_demo.py    # dane demonstracyjne
swagger.yaml    # specyfikacja OpenAPI API
```

## Dokumentacja

- **Frontend:** [Dokumentacja/Frontend/README.md](Dokumentacja/Frontend/README.md)
  — dokumentacja techniczna interfejsu oraz testy i raport błędów.
- **API backendu:** [Dokumentacja/Backend/API.md](Dokumentacja/Backend/API.md)
  oraz specyfikacja [swagger.yaml](swagger.yaml).
- **Baza danych:** [Dokumentacja/Szkielet-Bazy-Danych.sql](Dokumentacja/Szkielet-Bazy-Danych.sql).
- **Diagramy (procesy, ERD, uprawnienia):** [Dokumentacja/Diagramy/](Dokumentacja/Diagramy/).
