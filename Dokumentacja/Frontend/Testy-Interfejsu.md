# ETAP 10A – Testowanie i weryfikacja interfejsu użytkownika

Dokument obejmuje weryfikację interfejsu aplikacji do rozliczania praktyk zawodowych
(ANS Elbląg). Interfejs zrealizowano jako renderowane po stronie serwera widoki
Jinja2 (SSR) z jednym arkuszem `static/css/style.css` i skryptami inline.

---

## Weryfikacja struktury interfejsu

### Lista widoków i ich funkcje

| Widok (szablon)                                | Ścieżka                       | Funkcja                                                                                                                                               |
| ---------------------------------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Logowanie / rejestracja (`login.html`)         | `/auth/login`                 | Logowanie Microsoft OAuth lub lokalne; rejestracja nowego konta                                                                                       |
| Konto oczekujące (`pending.html`)              | `/auth/pending`               | Informacja, że konto czeka na zatwierdzenie przez administratora                                                                                      |
| Pulpit (`dashboard.html`)                      | `/auth/dashboard`             | Konsola zależna od roli: student widzi swoją praktykę i dokumenty; personel (UOPZ/ZOPZ/Dyrektor) – listę praktyk i akcje; administrator – zarządzanie |
| Zatwierdzanie kont (`admin_approvals.html`)    | `/auth/admin/approvals`       | Administrator nadaje rolę i akceptuje/odrzuca nowe konta                                                                                              |
| Porozumienie – Zał. 1 (`zal1.html`)            | `/auth/formularze/<id>/zal1`  | Podgląd i podpis Porozumienia (ZOPZ, Dyrektor) + metadane                                                                                             |
| Program i harmonogram – Zał. 2a (`zal2a.html`) | `/auth/formularze/<id>/zal2a` | Wypełnienie 13 efektów i harmonogramu (suma 120 dni), podpisy                                                                                         |
| Karta str. 1 – Zał. 3.1 (`zal31.html`)         | `/auth/formularze/<id>/zal31` | Skierowanie i potwierdzenia zakładu (zgłoszenie, BHP)                                                                                                 |
| Karta str. 2 – Zał. 3.2 (`zal32.html`)         | `/auth/formularze/<id>/zal32` | Zaświadczenie odbycia i oceny zakładowa/uczelniana                                                                                                    |
| Potwierdzenie efektów – Zał. 4 (`zal4.html`)   | `/auth/formularze/<id>/zal4`  | Potwierdzenie 13 efektów (ZOPZ) + opinia UOPZ                                                                                                         |
| Ankieta – Zał. 5 (`zal5.html`)                 | `/auth/formularze/<id>/zal5`  | Kwestionariusz 14 pytań wypełniany przez studenta                                                                                                     |
| Dziennik – Zał. 6 (`zal6.html`)                | `/auth/formularze/<id>/zal6`  | Dynamiczna tabela 120 wpisów dziennych z efektami                                                                                                     |
| Sprawozdanie – Zał. 7 (`zal7.html`)            | `/auth/formularze/<id>/zal7`  | Trzy sekcje sprawozdania studenta + potwierdzenie ZOPZ                                                                                                |
| Protokół zaliczenia – Zał. 8 (`zal8.html`)     | `/auth/formularze/<id>/zal8`  | Protokół komisji, oceny cząstkowe, ocena końcowa K                                                                                                    |
| Szablon bazowy (`base.html`)                   | –                             | Wspólna nawigacja, przełącznik motywu (jasny/ciemny), stopka                                                                                          |

### Tabela stanu działania interfejsu

| Widok                   | Status działania | Uwagi                                                                                  |
| ----------------------- | ---------------- | -------------------------------------------------------------------------------------- |
| Logowanie / rejestracja | OK               | Walidacja e-mail i hasła po stronie klienta; rejestracja kieruje do ekranu oczekiwania |
| Konto oczekujące        | OK               | –                                                                                      |
| Pulpit (student)        | OK               | Karta postępu faz, stan załączników, pobieranie PDF/ZIP                                |
| Pulpit (personel)       | OK               | Lista praktyk, akcje wg fazy i roli, pobieranie ZIP po zakończeniu                     |
| Pulpit (administrator)  | OK               | Zarządzanie kontami, praktykami, firmami                                               |
| Zatwierdzanie kont      | OK               | Wybór roli (student/uopz/zopz/dyrektor), akceptacja/odrzucenie                         |
| Zał. 1 – Porozumienie   | OK               | –                                                                                      |
| Zał. 2a – Harmonogram   | OK               | Walidacja sumy dni = 120 i kompletu 13 efektów                                         |
| Zał. 3.1 – Karta str. 1 | OK               | –                                                                                      |
| Zał. 3.2 – Karta str. 2 | OK               | Oceny w skali 2–5, opisy min. 10 znaków                                                |
| Zał. 4 – Efekty         | OK               | –                                                                                      |
| Zał. 5 – Ankieta        | OK               | Wszystkie 14 pytań wymagane                                                            |
| Zał. 6 – Dziennik       | OK               | Walidacja dat (dni robocze, w okresie praktyki)                                        |
| Zał. 7 – Sprawozdanie   | OK               | Trzy sekcje min. 30 znaków                                                             |
| Zał. 8 – Protokół       | OK               | Automatyczne wyliczenie ocen E i K                                                     |
| Nawigacja / motyw       | OK               | Przełącznik jasny/ciemny zapamiętywany w `localStorage`                                |

**Wniosek:** wszystkie zaprojektowane widoki są dostępne, nawigacja między nimi działa
poprawnie, a nazwy przycisków i sekcji są spójne z formularzami urzędowymi (Zał. 1–8).

---

## Testowanie formularzy

Dla każdego formularza przygotowano przypadki testowe z danymi poprawnymi i błędnymi.

| Formularz             | Dane testowe                                      | Oczekiwany rezultat                                                                 | Wynik |
| --------------------- | ------------------------------------------------- | ----------------------------------------------------------------------------------- | ----- |
| Nowa praktyka         | Komplet: student, firma, zakres 120 dni roboczych | Komunikat sukcesu „Praktyka … zarejestrowana (ID: N)" + przekierowanie (302)        | OK    |
| Nowa praktyka         | Brak wyboru firmy (`required`)                    | Przeglądarka blokuje wysłanie, podświetla pole                                      | OK    |
| Nowa praktyka         | Zakres dat ≠ 120 dni roboczych                    | Komunikat błędu „Praktyka musi obejmować dokładnie 120 dni…" + przekierowanie (302) | OK    |
| Nowa praktyka         | `data_od` > `data_do`                             | Komunikat: „Data rozpoczęcia nie może być późniejsza…"                              | OK    |
| Nowa praktyka         | Student ma już praktykę                           | Komunikat: „Student ma już zarejestrowaną praktykę"                                 | OK    |
| Dodaj firmę           | Pusta nazwa (`required`)                          | Przeglądarka blokuje wysłanie                                                       | OK    |
| Dziennik – dodaj wpis | Data, opis ≥10 zn., ≥1 efekt                      | Wpis zapisany, licznik n/120                                                        | OK    |
| Dziennik – dodaj wpis | Data spoza zakresu praktyki                       | Pole `date` ograniczone `min`/`max`; serwer odrzuca                                 | OK    |
| Dziennik – dodaj wpis | Dzień weekendowy                                  | Komunikat: „tylko dla dnia roboczego (pon–pt)"                                      | OK    |
| Dziennik – dodaj wpis | Brak zaznaczonego efektu                          | Komunikat: „Zaznacz co najmniej jeden efekt"                                        | OK    |
| Zał. 2a               | Suma dni harmonogramu ≠ 120                       | Komunikat: „Suma dni harmonogramu musi wynosić 120"                                 | OK    |
| Zał. 2a               | Pusty opis efektu                                 | Komunikat: „Efekt XX: opis prac jest wymagany"                                      | OK    |
| Zał. 3.2 (ZOPZ)       | Ocena spoza skali 2–5                             | Komunikat: „Ocena parametryczna musi być w skali 2–5"                               | OK    |
| Zał. 4                | Brak odpowiedzi dla efektu                        | Komunikat: „Brakuje odpowiedzi dla efektu XX"                                       | OK    |
| Zał. 7                | Sekcja < 30 znaków                                | Komunikat: „Sekcja … musi mieć minimum 30 znaków"                                   | OK    |
| Zał. 5                | Brak odpowiedzi na pytanie                        | Komunikat: „Brakuje odpowiedzi na pytanie N"                                        | OK    |

> **Uwaga dot. „edycji praktyki":** aplikacja nie udostępnia ogólnego formularza edycji
> praktyki – zmiana stanu praktyki odbywa się przez podpisy kolejnych załączników
> (workflow faz), a nie przez ręczną edycję pól. Korekta błędnego dokumentu realizowana
> jest mechanizmem odrzucenia (np. `POST /api/internships/<id>/zal2a/reject`).

---

## Zadanie 3 – Weryfikacja komunikacji frontend ↔ API

Interfejs działa w modelu **SSR (Server-Side Rendering)** – strony renderuje serwer Flask,
więc widoki (np. pulpit) **nie** wykonują osobnych zapytań AJAX do API; dane wstrzykiwane są
bezpośrednio w szablon. W praktyce komunikacja frontend ↔ API obserwowalna w przeglądarce
przebiega wg wzorca **Post/Redirect/Get**: formularz wysyła `POST`, serwer odpowiada
przekierowaniem `302`, a wynik operacji prezentowany jest jako komunikat `flash`.

Weryfikację wykonano w narzędziach developerskich (zakładka **Network**) – udokumentowano
zrzutami ekranu (patrz instrukcja na końcu dokumentu).

| Metoda      | Akcja w interfejsie                              | Endpoint                                  | Zaobserwowany wynik                                                            |
| ----------- | ------------------------------------------------ | ----------------------------------------- | ------------------------------------------------------------------------------ |
| GET         | Wejście bezpośrednio na adres API w przeglądarce | `GET /api/internships`                    | 200 OK + JSON listy praktyk                                                    |
| POST        | Rejestracja praktyki (dane poprawne)             | `POST /api/internships`                   | 302 → przekierowanie + flash „Praktyka … zarejestrowana (ID: N)"               |
| POST        | Rejestracja praktyki (zły zakres dat)            | `POST /api/internships`                   | 302 → przekierowanie + flash błędu „Data rozpoczęcia nie może być późniejsza…" |
| POST        | Dodanie wpisu dziennika                          | `POST /api/journal/add`                   | 302 → przekierowanie + flash                                                   |
| POST        | Podpis dokumentu                                 | `POST /api/internships/<id>/sign`         | 302 → przekierowanie + flash                                                   |
| POST        | Usunięcie praktyki (administrator)               | `POST /auth/admin/internship/<id>/delete` | 302 → przekierowanie + flash „Praktyka #N została usunięta"                    |
| GET         | Próba pobrania nieistniejącego zasobu            | `GET /api/internships/9999`               | 404 + JSON `{"error": "Resource not found"}`                                   |
| PUT / PATCH | –                                                | –                                         | nie występuje (patrz uwaga poniżej)                                            |

### Zrzuty ekranu

| Akcja                                                      | Zrzut                                                                  |
| ---------------------------------------------------------- | ---------------------------------------------------------------------- |
| POST – rejestracja praktyki (dane poprawne, flash sukcesu) | [Zrzuty/PrawidlowyWpis.png](Zrzuty/PrawidlowyWpis.png)                 |
| POST – rejestracja praktyki (dane błędne, flash błędu)     | [Zrzuty/BlednyWpis.png](Zrzuty/BlednyWpis.png)                         |
| DELETE (jako POST) – usunięcie zasobu przez administratora | [Zrzuty/UsuniecieUzytkownika.png](Zrzuty/UsuniecieUzytkownika.png)     |
| GET – błąd API 404 (nieistniejący zasób)                   | [Zrzuty/PodstronaNieZnaleziona.png](Zrzuty/PodstronaNieZnaleziona.png) |

> **Uwaga – status 302 vs 400/JSON:** wszystkie akcje wywoływane z formularzy HTML zwracają
> `302` (Post/Redirect/Get), a błąd prezentowany jest komunikatem `flash`, **nie** jako
> odpowiedź JSON ze statusem 400. Odpowiedzi `400`/`404` z ciałem JSON `{"error": "..."}`
> (moduł `app/api/errors.py`) zwracane są tylko przy bezpośrednim wywołaniu API
> (Postman/curl) – przetestowano w Lab09. Wpisanie adresu API w pasku przeglądarki to
> żądanie `GET`, na którym można zaobserwować zarówno poprawną odpowiedź `200`, jak i błąd `404`.

> **Uwaga – brak PUT/PATCH:** aplikacja nie wykorzystuje metod `PUT`/`PATCH`. Aktualizacja
> stanu praktyki realizowana jest dedykowanymi endpointami `POST` (workflow podpisów kolejnych
> załączników), co eliminuje potrzebę pełnej/cząstkowej podmiany zasobu.

> **Uwaga – DELETE z interfejsu:** usunięcie praktyki przez UI wysyła `POST`
> na `/auth/admin/internship/<id>/delete` (formularze HTML nie obsługują metody `DELETE`),
> z odpowiedzią `302` + flash. Właściwy endpoint REST `DELETE /api/internships/<id>`
> istnieje w API i został przetestowany kolekcją Postman (Lab09).

**Reakcja interfejsu na błędy API:** błędy walidacji i uprawnień prezentowane są jako
komunikaty `flash` (kolorowe alerty na górze widoku); przy bezpośrednim wywołaniu API błędy
404/500 zwracają jednolity JSON `{"error": "..."}` z modułu `app/api/errors.py`.

---

## Testowanie walidacji po stronie klienta

Walidacja po stronie klienta zrealizowana atrybutami HTML5 (`required`, `type`,
`minlength`, `min`/`max`). Poniżej 12 przypadków testowych.

| #   | Pole / formularz             | Dane błędne                      | Mechanizm                | Oczekiwany rezultat                  |
| --- | ---------------------------- | -------------------------------- | ------------------------ | ------------------------------------ |
| 1   | Logowanie – e-mail           | puste                            | `required`               | Blokada wysłania, podświetlenie pola |
| 2   | Logowanie – e-mail           | `janekuczelnia.pl` (brak @)      | `type="email"`           | Komunikat „Wprowadź adres e-mail"    |
| 3   | Rejestracja – hasło          | `123` (3 znaki)                  | `minlength="6"`          | Komunikat o min. długości            |
| 4   | Nowa praktyka – student      | nie wybrano                      | `required` (select)      | Blokada wysłania                     |
| 5   | Nowa praktyka – firma        | nie wybrano                      | `required` (select)      | Blokada wysłania                     |
| 6   | Nowa praktyka – data         | puste pole daty                  | `required` `type="date"` | Blokada wysłania                     |
| 7   | Dziennik – data wpisu        | data < `data_od` lub > `data_do` | `min`/`max`              | Selektor blokuje wybór               |
| 8   | Dziennik – opis prac         | `praca` (5 znaków)               | `minlength="10"`         | Komunikat o min. długości            |
| 9   | Zał. 2a – liczba dni         | `0` lub `200`                    | `min="1" max="120"`      | Selektor blokuje wartość             |
| 10  | Zał. 3.2 – ocena opisowa     | `ok` (2 znaki)                   | `minlength="10"`         | Komunikat o min. długości            |
| 11  | Zał. 7 – sekcja sprawozdania | `krótko` (6 znaków)              | `minlength="30"`         | Komunikat o min. długości            |
| 12  | Dodaj firmę – nazwa          | puste                            | `required`               | Blokada wysłania                     |

**Ocena czytelności komunikatów:** komunikaty natywne przeglądarki są zrozumiałe
(„Wypełnij to pole", „Wprowadź adres e-mail", „Użyj co najmniej N znaków"). Walidacja
biznesowa (120 dni, 13 efektów, skala ocen) realizowana jest dodatkowo po stronie serwera
i prezentowana czytelnymi komunikatami `flash` w języku polskim.

---

## Testowanie UX i responsywności

Testy przeprowadzono w dwóch przeglądarkach (**Opera GX** i **Microsoft Edge**) oraz w trybie
urządzenia mobilnego (DevTools, szerokość ~375 px).

| Przeglądarka   | Zrzut                                                                |
| -------------- | -------------------------------------------------------------------- |
| Opera GX       | [Zrzuty/Przegladarka1-operagx.png](Zrzuty/Przegladarka1-operagx.png) |
| Microsoft Edge | [Zrzuty/Przegladarka2-edge.png](Zrzuty/Przegladarka2-edge.png)       |
| Motyw jasny    | [Zrzuty/tryb-jasny.png](Zrzuty/tryb-jasny.png)                       |

| Kryterium UX                            | Pulpit           | Formularze | Uwagi                                       |
| --------------------------------------- | ---------------- | ---------- | ------------------------------------------- |
| Interfejs intuicyjny                    | OK               | OK         | Czytelny podział na fazy i stan załączników |
| Czytelne komunikaty                     | OK               | OK         | Komunikaty `flash` w języku polskim         |
| Poprawność na różnych rozdzielczościach | OK (po naprawie) | OK         | Patrz „Problem mobilny" poniżej             |
| Wygoda formularzy                       | OK               | OK         | Natywne kontrolki HTML5 (`date`, `select`)  |
| Informowanie o sukcesie operacji        | OK               | OK         | Zielony alert po każdej operacji            |

### Zauważony problem UX (tryb mobilny) i jego naprawa

**Problem (przed naprawą):** na ekranie o szerokości ~375 px pulpit studenta wyświetlał się
w dwóch kolumnach (sztywny układ `1fr 2fr`), przez co karty „Aktualne zadanie" i „Stan
załączników" były nadmiernie ściśnięte. W tabeli „Stan załączników":

- plakietki statusu (`ZOPZ: ✓  Dyrektor: ✓`) zawijały się i „pękały" na fragmenty,
- trzykolumnowy układ (Dokument / Status / Otwórz) nie mieścił się w szerokości ekranu,
  przez co odnośniki „Otwórz →" i plakietki się rozjeżdżały,
- etykiety osi faz (1–4) były ściśnięte i słabo czytelne.

Zrzut „przed naprawą": [Zrzuty/TestMobilnyBladUX.png](Zrzuty/TestMobilnyBladUX.png)

**Naprawa:** rozszerzono regułę `@media (max-width: 680px)` w `static/css/style.css`:

- układ pulpitu studenta zwijany jest do **jednej kolumny** (klasa `.dashboard-split`),
- tabele dokumentów przełączane są na **układ kafelkowy** – nagłówek tabeli jest ukrywany,
  a każdy wiersz staje się blokiem (nazwa załącznika / plakietka statusu / odnośnik),
- plakietki statusu są `inline-block` na pełną szerokość wiersza, więc nie pękają,
- oś faz ma mniejsze kółka i etykiety, dzięki czemu mieści się w jednym rzędzie,
- siatka wyboru załączników do ZIP (`.zip-grid`) zwijana jest do jednej kolumny.

**Wynik (po naprawie):** przy szerokości ~375 px wszystkie elementy układają się pionowo
i są w pełni czytelne – żaden element się nie rozjeżdża.

Zrzut „po naprawie": [Zrzuty/TestMobilnyNaprawiony.png](Zrzuty/TestMobilnyNaprawiony.png)

Aplikacja korzysta z jednostek względnych, siatek `grid` i reguł `@media`, oraz posiada
przełącznik motywu jasny/ciemny. Każda operacja kończy się komunikatem `flash`
(sukces/ostrzeżenie/błąd).

---

## Analiza błędów interfejsu

Raport błędów do uzupełnienia po testach (procedura na końcu dokumentu):

| #   | Opis błędu                                                                                                                                                             | Sposób odtworzenia                                                               | Propozycja rozwiązania                                                                                                        | Status                   |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| 1   | Rozjeżdżający się układ pulpitu i tabeli „Stan załączników" w trybie mobilnym (~375 px): plakietki statusu pękały, kolumny tabeli i odnośniki „Otwórz →" nakładały się | DevTools → tryb urządzenia (Ctrl+Shift+M), szerokość ~375 px, zalogowany student | Rozszerzenie `@media (max-width: 680px)`: zwinięcie pulpitu do 1 kolumny, kafelkowy układ tabel, plakietki na pełną szerokość | ✅ Naprawione            |
| 2   | Brak błędów JavaScript – konsola czysta                                                                                                                                | Przejście przez wszystkie widoki z otwartą zakładką **Console**                  | –                                                                                                                             | OK                       |
| 3   | Po utracie połączenia z API (zatrzymany backend) próba wysłania formularza kończy się standardowym błędem połączenia przeglądarki                                      | Zatrzymać `run.py`, wysłać dowolny formularz                                     | Aplikacja nie „wywala się" po stronie JS (SSR, brak AJAX); ewentualne usprawnienie – dedykowana strona błędu 5xx              | OK (zachowanie poprawne) |
| 4   | Odporność na niepoprawne dane                                                                                                                                          | Ręczne wpisanie błędnych wartości / ominięcie walidacji HTML5 przez DevTools     | Dane odrzucane przez walidację serwerową (komunikat `flash`), aplikacja pozostaje stabilna                                    | OK                       |

**Wniosek:** nie wykryto błędów krytycznych. Jedyny zauważony problem (responsywność mobilna,
wiersz 1) został naprawiony. Interfejs jest odporny na niepoprawne dane dzięki dwuwarstwowej
walidacji (HTML5 + serwer), a brak warstwy AJAX powoduje, że utrata połączenia z backendem nie
wywołuje błędów JavaScript.

---
