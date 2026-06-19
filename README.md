# System Rozliczania Praktyk (ApIn2-projekt)

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
- **Generowanie PDF** pojedynczych załączników (Zał. 1–8) oraz eksport zbiorczy do
  archiwum ZIP — w całości w Pythonie (`xhtml2pdf` + `reportlab`), bez zależności od
  przeglądarki. Zob. sekcję [Moduł generowania PDF](#moduł-generowania-pdf).
- **REST API** (38 endpointów) z dokumentacją Swagger UI pod `/apidocs/`.
- **Logowanie** lokalne oraz przez Microsoft OAuth.

## Technologie

- Backend: **Python / Flask**, **SQLAlchemy**, **Flask-Login**
- Baza danych: **PostgreSQL** (schemat uzupełniany automatycznie przez `ensure_schema()`)
- Frontend: **SSR (Jinja2)**, HTML5, CSS3, vanilla JavaScript (bez frameworków/CDN)
- Generowanie PDF: **`xhtml2pdf` (pisa) + `reportlab`** — czysty Python, bez przeglądarki

## Uruchomienie

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # skopiuj szablon konfiguracji
# uzupełnij .env (co najmniej DATABASE_URL i SECRET_KEY — patrz komentarze w pliku)
# należy również utworzyć pustą bazę danych w pgAdmin o tej samej nazwie co w DATABASE_URL
.\venv\Scripts\python.exe run.py
```

Aplikacja startuje pod `http://localhost:5000/auth/login`. Przy starcie wykonywane jest
`ensure_schema()` i seed kont testowych. Dane demonstracyjne:
`.\venv\Scripts\python.exe seed_demo.py` (konto `demo@ans.elblag.pl` / `Demo1234!`).

### Konfiguracja `.env`

Szablon ze wszystkimi zmiennymi i opisami: [`.env.example`](.env.example).
Minimalny zestaw do uruchomienia lokalnie:

| Zmienna                                | Opis                                                            | Wymagana?                                         |
| -------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------- |
| `DATABASE_URL`                         | Connection string PostgreSQL (`postgresql://user:pass@host/db`) | tak                                               |
| `SECRET_KEY`                           | Losowy ciąg chroniący podpis sesji (min. 32 znaki)              | tak w produkcji                                   |
| `MICROSOFT_CLIENT_ID/SECRET/TENANT_ID` | Dane aplikacji z Azure AD — do logowania kontem uczelni         | tak                                               |
| `GOOGLE_CLIENT_ID/SECRET`              | Dane z Google Cloud Console — do logowania kontem Google        | tylko jeśli OAuth Google ma działać (nie używany) |

Logowanie lokalne (e-mail + hasło) działa bez żadnych kluczy OAuth, lecz wymaga potwierdzenia przez administratora, natomiast aby stworzyć nowe konto studenta wymagane jest logowanie przez Microsoft, rejestracja lokalna jest dla UOPZ, ZOPZ bądź dyrektora.

## Moduł generowania PDF

System tworzy urzędowe załączniki praktyki (Zał. 1–8) jako pliki PDF na podstawie
tych samych szablonów Jinja2, które renderują widoki HTML — dzięki temu wersja na
ekranie i wersja do druku pochodzą z jednego źródła.

### Architektura i biblioteki

Cały moduł mieści się w pliku [app/api/pdf.py](app/api/pdf.py). Wykorzystuje wyłącznie
biblioteki Pythona — **nie uruchamia procesów zewnętrznych**:

- **`xhtml2pdf` (pisa)** — silnik renderujący HTML/CSS → PDF,
- **`reportlab`** — warstwa niższego poziomu (osadzanie czcionek TrueType, rysowanie),
- **`zipfile`** (biblioteka standardowa) — pakowanie eksportu zbiorczego do ZIP.

### Proces generowania (krok po kroku)

1. **Żądanie** trafia do endpointu w blueprincie `pdf_bp` (`/api/pdf/...`).
2. **`_ensure_fonts()`** rejestruje (raz na proces) czcionki TrueType: _Arial_ dla
   polskich znaków oraz _Segoe UI Symbol_ dla glifów ✓ ☐ ✗ — domyślna Helvetica w
   xhtml2pdf nie zawiera tych znaków i renderowałaby je jako puste kwadraty.
3. **`_build_context()`** pobiera z bazy dane potrzebne danemu załącznikowi
   (wpisy dziennika, efekty, oceny, protokół itd.) i buduje kontekst szablonu.
4. **`render_template()`** renderuje szablon `templates/formularze/<zal>.html` do HTML.
5. **`_strip_for_pdf()`** dostosowuje HTML do ograniczeń xhtml2pdf:
   usuwa arkusze i bloki `<style>`, podmienia zmienne CSS `var(--x)` na wartości,
   ukrywa elementy interfejsu (`.no-print`), konwertuje jednostki `rem`/`em` na `px`,
   **wypełnia puste komórki `<td></td>` twardą spacją** (puste komórki psują
   obliczanie szerokości kolumn), owija symbole w font symboli oraz wstrzykuje
   wspólny arkusz `_PDF_CSS` i stopkę z numeracją stron (`<pdf:pagenumber>`).
6. **`pisa.CreatePDF()`** zamienia gotowy HTML na bajty PDF.
7. **`send_file()`** zwraca dokument z nagłówkiem `Content-Disposition: attachment`
   i poprawną nazwą pliku (`Praktyka_<id>_<Załącznik>.pdf`).

Eksport zbiorczy (`_zip_attachments()`) generuje wybrane załączniki w pętli i pakuje
je do ZIP; dokument, którego nie uda się wygenerować, jest pomijany, a jego opis
trafia do pliku `_BLEDY.txt` w archiwum — jeden uszkodzony załącznik nie psuje
całej paczki (odporność modułu).

### Endpointy PDF

| Metoda | Ścieżka                      | Opis                                                         |
| ------ | ---------------------------- | ------------------------------------------------------------ |
| `GET`  | `/api/pdf/<id>/<zal_key>`    | pojedynczy załącznik (`zal_key` = `zal1`…`zal8`)             |
| `POST` | `/api/pdf/<id>/zip`          | ZIP z załącznikami zaznaczonymi w panelu                     |
| `GET`  | `/api/pdf/generate-pdf/<id>` | ZIP ze wszystkimi dostępnymi załącznikami (eksport zbiorczy) |

### Uruchomienie i odtwarzanie testów modułu PDF

```bash
# 1. (opcjonalnie) trzecia kompletna praktyka — daje min. 3 użytkowników do testów
.\venv\Scripts\python.exe tools\seed_extra.py

# 2. wygenerowanie przykładowych dokumentów do _pdfout/ (wszystkie praktyki × Zał. 1–8)
.\venv\Scripts\python.exe tools\generate_pdf_samples.py

# 3. testy odporności modułu (puste/brakujące/długie/błędne dane, obsługa wyjątków)
.\venv\Scripts\python.exe tools\test_pdf_resilience.py
```

Pełna dokumentacja testów i weryfikacji modułu:
[Dokumentacja/PDF/ETAP11-Weryfikacja-PDF.md](Dokumentacja/PDF/Weryfikacja-PDF.md).

## Struktura projektu

```
app/            # logika backendu (modele, API, auth); moduł PDF: app/api/pdf.py
templates/      # widoki Jinja2 (frontend SSR); szablony załączników: templates/formularze/
static/css/     # arkusz stylów aplikacji
tools/          # skrypty pomocnicze (seed, generowanie i testy PDF)
_pdfout/        # przykładowe wygenerowane dokumenty PDF (po uruchomieniu skryptu)
Dokumentacja/   # dokumentacja projektu (API, frontend, PDF, diagramy, baza)
run.py          # punkt wejścia aplikacji
seed_demo.py    # dane demonstracyjne
swagger.yaml    # specyfikacja OpenAPI API
```

## Pozostała dokumentacja:

- **Frontend:** [Dokumentacja/Frontend/README.md](Dokumentacja/Frontend/README.md)
  — dokumentacja techniczna interfejsu oraz testy i raport błędów.
- **Moduł PDF:** [Dokumentacja/PDF/Weryfikacja-PDF.md](Dokumentacja/PDF/ETAP11-Weryfikacja-PDF.md)
  — testy generowania, analiza techniczna, raport błędów i podglądy dokumentów.
- **API backendu:** [Dokumentacja/Backend/API.md](Dokumentacja/Backend/API.md)
  oraz specyfikacja [swagger.yaml](swagger.yaml).
- **Baza danych:** [Dokumentacja/Szkielet-Bazy-Danych.sql](Dokumentacja/Szkielet-Bazy-Danych.sql).
- **Diagramy (procesy, ERD, uprawnienia) oraz wybór bazy danych:** [Dokumentacja/Opis(lab4-7).pdf](<Dokumentacja/Opis(lab4-7).pdf>).
