# ETAP 10A — Testowanie i weryfikacja interfejsu użytkownika

Dokument obejmuje weryfikację interfejsu aplikacji do rozliczania praktyk zawodowych
(ANS Elbląg). Interfejs zrealizowano jako renderowane po stronie serwera widoki
Jinja2 (SSR) z jednym arkuszem `static/css/style.css` i skryptami inline.

---

## Zadanie 1 — Weryfikacja struktury interfejsu

### Lista widoków i ich funkcje

| Widok (szablon) | Ścieżka | Funkcja |
|---|---|---|
| Logowanie / rejestracja (`login.html`) | `/auth/login` | Logowanie Microsoft OAuth lub lokalne; rejestracja nowego konta |
| Konto oczekujące (`pending.html`) | `/auth/pending` | Informacja, że konto czeka na zatwierdzenie przez administratora |
| Pulpit (`dashboard.html`) | `/auth/dashboard` | Konsola zależna od roli: student widzi swoją praktykę i dokumenty; personel (UOPZ/ZOPZ/Dyrektor) — listę praktyk i akcje; administrator — zarządzanie |
| Zatwierdzanie kont (`admin_approvals.html`) | `/auth/admin/approvals` | Administrator nadaje rolę i akceptuje/odrzuca nowe konta |
| Porozumienie — Zał. 1 (`zal1.html`) | `/auth/formularze/<id>/zal1` | Podgląd i podpis Porozumienia (ZOPZ, Dyrektor) + metadane |
| Program i harmonogram — Zał. 2a (`zal2a.html`) | `/auth/formularze/<id>/zal2a` | Wypełnienie 13 efektów i harmonogramu (suma 120 dni), podpisy |
| Karta str. 1 — Zał. 3.1 (`zal31.html`) | `/auth/formularze/<id>/zal31` | Skierowanie i potwierdzenia zakładu (zgłoszenie, BHP) |
| Karta str. 2 — Zał. 3.2 (`zal32.html`) | `/auth/formularze/<id>/zal32` | Zaświadczenie odbycia i oceny zakładowa/uczelniana |
| Potwierdzenie efektów — Zał. 4 (`zal4.html`) | `/auth/formularze/<id>/zal4` | Potwierdzenie 13 efektów (ZOPZ) + opinia UOPZ |
| Ankieta — Zał. 5 (`zal5.html`) | `/auth/formularze/<id>/zal5` | Kwestionariusz 14 pytań wypełniany przez studenta |
| Dziennik — Zał. 6 (`zal6.html`) | `/auth/formularze/<id>/zal6` | Dynamiczna tabela 120 wpisów dziennych z efektami |
| Sprawozdanie — Zał. 7 (`zal7.html`) | `/auth/formularze/<id>/zal7` | Trzy sekcje sprawozdania studenta + potwierdzenie ZOPZ |
| Protokół zaliczenia — Zał. 8 (`zal8.html`) | `/auth/formularze/<id>/zal8` | Protokół komisji, oceny cząstkowe, ocena końcowa K |
| Szablon bazowy (`base.html`) | — | Wspólna nawigacja, przełącznik motywu (jasny/ciemny), stopka |

### Tabela stanu działania interfejsu

| Widok | Status działania | Uwagi |
|---|---|---|
| Logowanie / rejestracja | OK | Walidacja e-mail i hasła po stronie klienta; rejestracja kieruje do ekranu oczekiwania |
| Konto oczekujące | OK | — |
| Pulpit (student) | OK | Karta postępu faz, stan załączników, pobieranie PDF/ZIP |
| Pulpit (personel) | OK | Lista praktyk, akcje wg fazy i roli, pobieranie ZIP po zakończeniu |
| Pulpit (administrator) | OK | Zarządzanie kontami, praktykami, firmami |
| Zatwierdzanie kont | OK | Wybór roli (student/uopz/zopz/dyrektor), akceptacja/odrzucenie |
| Zał. 1 – Porozumienie | OK | — |
| Zał. 2a – Harmonogram | OK | Walidacja sumy dni = 120 i kompletu 13 efektów |
| Zał. 3.1 – Karta str. 1 | OK | — |
| Zał. 3.2 – Karta str. 2 | OK | Oceny w skali 2–5, opisy min. 10 znaków |
| Zał. 4 – Efekty | OK | — |
| Zał. 5 – Ankieta | OK | Wszystkie 14 pytań wymagane |
| Zał. 6 – Dziennik | OK | Walidacja dat (dni robocze, w okresie praktyki) |
| Zał. 7 – Sprawozdanie | OK | Trzy sekcje min. 30 znaków |
| Zał. 8 – Protokół | OK | Automatyczne wyliczenie ocen E i K |
| Nawigacja / motyw | OK | Przełącznik jasny/ciemny zapamiętywany w `localStorage` |

**Wniosek:** wszystkie zaprojektowane widoki są dostępne, nawigacja między nimi działa
poprawnie, a nazwy przycisków i sekcji są spójne z formularzami urzędowymi (Zał. 1–8).

---

## Zadanie 2 — Testowanie formularzy

Dla każdego formularza przygotowano przypadki testowe z danymi poprawnymi i błędnymi.

| Formularz | Dane testowe | Oczekiwany rezultat | Wynik |
|---|---|---|---|
| Nowa praktyka | Komplet: student, firma, zakres 120 dni roboczych | Praktyka zarejestrowana (201) | OK |
| Nowa praktyka | Brak wyboru firmy (`required`) | Przeglądarka blokuje wysłanie, podświetla pole | OK |
| Nowa praktyka | Zakres dat ≠ 120 dni roboczych | Komunikat: „Praktyka musi obejmować dokładnie 120 dni…" (400) | OK |
| Nowa praktyka | `data_od` > `data_do` | Komunikat: „Data rozpoczęcia nie może być późniejsza…" | OK |
| Nowa praktyka | Student ma już praktykę | Komunikat: „Student ma już zarejestrowaną praktykę" | OK |
| Dodaj firmę | Pusta nazwa (`required`) | Przeglądarka blokuje wysłanie | OK |
| Dziennik – dodaj wpis | Data, opis ≥10 zn., ≥1 efekt | Wpis zapisany, licznik n/120 | OK |
| Dziennik – dodaj wpis | Data spoza zakresu praktyki | Pole `date` ograniczone `min`/`max`; serwer odrzuca | OK |
| Dziennik – dodaj wpis | Dzień weekendowy | Komunikat: „tylko dla dnia roboczego (pon–pt)" | OK |
| Dziennik – dodaj wpis | Brak zaznaczonego efektu | Komunikat: „Zaznacz co najmniej jeden efekt" | OK |
| Zał. 2a | Suma dni harmonogramu ≠ 120 | Komunikat: „Suma dni harmonogramu musi wynosić 120" | OK |
| Zał. 2a | Pusty opis efektu | Komunikat: „Efekt XX: opis prac jest wymagany" | OK |
| Zał. 3.2 (ZOPZ) | Ocena spoza skali 2–5 | Komunikat: „Ocena parametryczna musi być w skali 2–5" | OK |
| Zał. 4 | Brak odpowiedzi dla efektu | Komunikat: „Brakuje odpowiedzi dla efektu XX" | OK |
| Zał. 7 | Sekcja < 30 znaków | Komunikat: „Sekcja … musi mieć minimum 30 znaków" | OK |
| Zał. 5 | Brak odpowiedzi na pytanie | Komunikat: „Brakuje odpowiedzi na pytanie N" | OK |

> **Uwaga dot. „edycji praktyki":** aplikacja nie udostępnia ogólnego formularza edycji
> praktyki — zmiana stanu praktyki odbywa się przez podpisy kolejnych załączników
> (workflow faz), a nie przez ręczną edycję pól. Korekta błędnego dokumentu realizowana
> jest mechanizmem odrzucenia (np. `POST /api/internships/<id>/zal2a/reject`).

---

## Zadanie 3 — Weryfikacja komunikacji frontend ↔ API

Procedura weryfikacji w narzędziach developerskich przeglądarki (zakładka **Network**).
Tę część należy udokumentować zrzutami ekranu (patrz instrukcja na końcu dokumentu).

| Metoda | Akcja w interfejsie | Endpoint | Oczekiwany status |
|---|---|---|---|
| GET | Wejście na pulpit / listę | `GET /api/internships`, `/api/journal` | 200 OK |
| POST | Rejestracja praktyki | `POST /api/internships` | 201 / 400 / 404 |
| POST | Dodanie wpisu dziennika | `POST /api/journal/add` | 302 (redirect + flash) |
| POST | Podpis dokumentu | `POST /api/internships/<id>/sign` | 200 / 403 |
| DELETE | Usunięcie zasobu (admin) | `DELETE /api/students/<id>` | 200 / 404 |
| — | Reakcja na błąd API | dowolny błąd | komunikat flash / strona błędu |

**Reakcja interfejsu na błędy API:** błędy walidacji i uprawnień prezentowane są jako
komunikaty `flash` (kolorowe alerty na górze widoku); błędy 404/500 zwracają jednolity
JSON `{"error": "..."}` z modułu `app/api/errors.py`.

---

## Zadanie 4 — Testowanie walidacji po stronie klienta

Walidacja po stronie klienta zrealizowana atrybutami HTML5 (`required`, `type`,
`minlength`, `min`/`max`). Poniżej 12 przypadków testowych.

| # | Pole / formularz | Dane błędne | Mechanizm | Oczekiwany rezultat |
|---|---|---|---|---|
| 1 | Logowanie – e-mail | puste | `required` | Blokada wysłania, podświetlenie pola |
| 2 | Logowanie – e-mail | `janekuczelnia.pl` (brak @) | `type="email"` | Komunikat „Wprowadź adres e-mail" |
| 3 | Rejestracja – hasło | `123` (3 znaki) | `minlength="6"` | Komunikat o min. długości |
| 4 | Nowa praktyka – student | nie wybrano | `required` (select) | Blokada wysłania |
| 5 | Nowa praktyka – firma | nie wybrano | `required` (select) | Blokada wysłania |
| 6 | Nowa praktyka – data | puste pole daty | `required` `type="date"` | Blokada wysłania |
| 7 | Dziennik – data wpisu | data < `data_od` lub > `data_do` | `min`/`max` | Selektor blokuje wybór |
| 8 | Dziennik – opis prac | `praca` (5 znaków) | `minlength="10"` | Komunikat o min. długości |
| 9 | Zał. 2a – liczba dni | `0` lub `200` | `min="1" max="120"` | Selektor blokuje wartość |
| 10 | Zał. 3.2 – ocena opisowa | `ok` (2 znaki) | `minlength="10"` | Komunikat o min. długości |
| 11 | Zał. 7 – sekcja sprawozdania | `krótko` (6 znaków) | `minlength="30"` | Komunikat o min. długości |
| 12 | Dodaj firmę – nazwa | puste | `required` | Blokada wysłania |

**Ocena czytelności komunikatów:** komunikaty natywne przeglądarki są zrozumiałe
(„Wypełnij to pole", „Wprowadź adres e-mail", „Użyj co najmniej N znaków"). Walidacja
biznesowa (120 dni, 13 efektów, skala ocen) realizowana jest dodatkowo po stronie serwera
i prezentowana czytelnymi komunikatami `flash` w języku polskim.

---

## Zadanie 5 — Testowanie UX i responsywności

Lista kontrolna do wykonania ręcznie (procedura na końcu dokumentu). Tabela do wypełnienia
podczas testów:

| Kryterium UX | Pulpit | Formularze | Uwagi |
|---|---|---|---|
| Interfejs intuicyjny | | | |
| Czytelne komunikaty | | | |
| Poprawność na różnych rozdzielczościach | | | |
| Wygoda formularzy | | | |
| Informowanie o sukcesie operacji | | | |

Aplikacja jest responsywna (CSS z jednostkami względnymi, siatki `grid` zwijające się na
wąskich ekranach, `@media` w `style.css`) i posiada przełącznik motywu jasny/ciemny.
Każda operacja kończy się komunikatem `flash` (sukces/ostrzeżenie/błąd).

---

## Zadanie 6 — Analiza błędów interfejsu

Raport błędów do uzupełnienia po testach (procedura na końcu dokumentu):

| # | Opis błędu | Sposób odtworzenia | Propozycja rozwiązania | Status |
|---|---|---|---|---|
| 1 | (np. brak — konsola czysta) | | | |

**Punkty do sprawdzenia:**
- błędy JavaScript w konsoli (zakładka **Console**),
- zachowanie po utracie połączenia z API (tryb offline / wyłączony backend),
- odporność na niepoprawne dane (ręczne wpisanie błędnych wartości).

---

## Instrukcja krok po kroku — części wymagające wykonania ręcznego

### A. Zrzuty ekranu komunikacji frontend ↔ API (Zadanie 3)
1. Uruchom aplikację (`run.py`) i zaloguj się.
2. Otwórz **DevTools** (F12) → zakładka **Network**, zaznacz **Preserve log**.
3. Wykonaj kolejno akcje z tabeli Zadania 3 (wejście na pulpit = GET, rejestracja praktyki = POST, itd.).
4. Dla każdej akcji kliknij wpis w Network i zrób zrzut: **Headers** (metoda + status), **Payload** (dane wysłane), **Response** (odpowiedź).
5. Zrób też zrzut komunikatu błędu — np. spróbuj zarejestrować praktykę z zakresem ≠ 120 dni (status 400) i sfotografuj alert + odpowiedź.
6. Zapisz zrzuty w katalogu na zrzuty (np. utwórz `Dokumentacja/Frontend/Screeny/`; istniejące zrzuty API znajdują się w `Dokumentacja/Backend/EndpointScreen/`).

### B. Testy UX i responsywności (Zadanie 5)
1. Uruchom aplikację w **dwóch przeglądarkach** (np. Chrome/Edge i Firefox).
2. W DevTools włącz **tryb urządzenia mobilnego** (Ctrl+Shift+M) i przetestuj pulpit + jeden formularz na szerokości ~375 px.
3. Wypełnij tabelę UX (Zadanie 5) wpisując OK / uwagi dla każdego kryterium w obu przeglądarkach.
4. Zrób 2–3 zrzuty: widok desktop, widok mobilny, przełączony motyw ciemny.
5. Opisz zauważone problemy UX (jeśli brak — zaznacz, że interfejs działa poprawnie).

### C. Raport błędów interfejsu (Zadanie 6)
1. Przejdź przez wszystkie widoki z otwartą zakładką **Console** — zanotuj ewentualne błędy/ostrzeżenia JS.
2. Zatrzymaj backend (lub odłącz sieć) i spróbuj wykonać akcję — opisz, jak zachowuje się interfejs.
3. Wpisz błędne dane w kilka formularzy i sprawdź, czy aplikacja się nie „wywala".
4. Uzupełnij tabelę raportu (Zadanie 6); jeśli błędów nie ma — wpisz „Nie wykryto błędów krytycznych".
