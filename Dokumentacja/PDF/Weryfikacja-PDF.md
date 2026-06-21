# Testowanie i weryfikacja generowania dokumentów PDF

Dokument opisuje weryfikację modułu generowania dokumentów PDF w systemie rozliczania
praktyk. Obejmuje, raport błędów oraz instrukcję odtworzenia testów.

Moduł generowania PDF: [app/api/pdf.py](../../app/api/pdf.py).
Szablony dokumentów: [templates/formularze/](../../templates/formularze/).
Opis architektury i procesu generowania: [README → Moduł generowania PDF](../../README.md#moduł-generowania-pdf).

---

## Środowisko testowe

| Element     | Wartość                                                       |
| ----------- | ------------------------------------------------------------- |
| Silnik PDF  | `xhtml2pdf` (pisa) 0.2.17 + `reportlab` 4.5.1 – czysty Python |
| Czcionki    | Arial (polskie znaki) + Segoe UI Symbol (glify ✓ ☐ ✗)         |
| Baza danych | PostgreSQL                                                    |
| System      | Windows 11, Python (venv)                                     |

### Dane wejściowe – trzy kompletne praktyki

Wszystkie testy oparto o trzy praktyki różnych studentów, każda w fazie 4
(zakończona) z kompletem danych.

| Praktyka | Student             | Nr albumu | Firma                         | Wpisy dziennika | Ocena końcowa |
| -------- | ------------------- | --------- | ----------------------------- | --------------- | ------------- |
| #1       | Marek Testowy       | 21000     | ABC Software Sp. z o.o.       | 120             | 4,5           |
| #4       | Anna Demonstracyjna | DEMO001   | Demo Software Sp. z o.o.      | 120             | 4             |
| #7       | Michał Mierzwa      | 21273     | InnoTech Solutions Sp. z o.o. | 120             | 5             |

Praktyki #1 i #4 pochodzą z seedów aplikacji; praktykę #7 tworzy skrypt
[tools/seed_extra.py](../../tools/seed_extra.py). Wygenerowane dokumenty znajdują się
w katalogu [`_pdfout/`](../../_pdfout/) (podkatalog na każdą praktykę).

---

## Weryfikacja generowania dziennika praktyk (Zał. 6)

**Dane wejściowe:** dziennik praktyki z 120 wpisami dziennymi (data, opis prac,
przypisane kody efektów uczenia się) dla każdego z trzech studentów.

**Weryfikacja automatyczna (PDF ↔ baza danych):**

| Praktyka               | Wpisy w bazie | Nazwisko studenta w PDF | Widoczny „Dzień 120" | Liczba stron |
| ---------------------- | ------------- | ----------------------- | -------------------- | ------------ |
| #1 Marek Testowy       | 120           | ✓                       | ✓                    | 4            |
| #4 Anna Demonstracyjna | 120           | ✓                       | ✓                    | 5            |
| #7 Michał Mierzwa      | 120           | ✓                       | ✓                    | 4            |

**Analiza poprawności:**

| Element dokumentu                     | Status | Uwagi                                                         |
| ------------------------------------- | ------ | ------------------------------------------------------------- |
| Pobieranie danych z bazy              | OK     | Wszystkie 120 wpisów obecnych w PDF                           |
| Układ dokumentu                       | OK     | Tabela wpisów z powtarzanym nagłówkiem na każdej stronie      |
| Zgodność danych z wpisami użytkownika | OK     | Daty, opisy i kody efektów zgodne z rekordami `WpisDziennika` |
| Formatowanie tekstu                   | OK     | Długie opisy zawijane, brak ucięć                             |
| Numeracja stron                       | OK     | Stopka „Strona X z Y" na każdej stronie                       |
| Polskie znaki                         | OK     | ą, ć, ę, ł, ń, ó, ś, ź, ż renderowane poprawnie (font Arial)  |

> Podgląd: [Podglady/Zal6.png](Podglady/Zal6.png)

---

## Weryfikacja generowania potwierdzenia efektów (Zał. 4)

**Dane wejściowe:** 13 efektów uczenia się wraz z potwierdzeniem ich uzyskania
(`PotwierdzenieEfektu`) oraz opinią opiekuna uczelnianego, dla 3 różnych studentów.

**Porównanie PDF ↔ rekordy bazy danych:**

| Praktyka               | Efekty potwierdzone w bazie | Ptaszki „✓" w PDF | Nr albumu w PDF |
| ---------------------- | --------------------------- | ----------------- | --------------- |
| #1 Marek Testowy       | 13                          | 13                | ✓               |
| #4 Anna Demonstracyjna | 13                          | 13                | ✓               |
| #7 Michał Mierzwa      | 13                          | 13                | ✓               |

Liczba potwierdzeń w bazie jest równa liczbie zaznaczeń „✓" w wygenerowanym
dokumencie dla wszystkich trzech użytkowników – dane są zgodne.

**Analiza poprawności:**

| Element dokumentu             | Status | Uwagi                                                 |
| ----------------------------- | ------ | ----------------------------------------------------- |
| Dane studenta                 | OK     | Imię, nazwisko, nr albumu, kierunek zgodne z bazą     |
| Lista efektów                 | OK     | Wszystkie 13 efektów (kod + opis) wraz ze statusem    |
| Zgodność z bazą danych        | OK     | 13/13 potwierdzeń = 13 zaznaczeń w PDF                |
| Układ dokumentu               | OK     | Tabela pełnej szerokości, kolumna statusu z ptaszkami |
| Komplet wymaganych informacji | OK     | Opinia opiekuna + podpisy ZOPZ/UOPZ obecne            |

> Podgląd: [Podglady/Zal4.png](Podglady/Zal4.png)

---

## Weryfikacja raportu końcowego (Zał. 8 – Protokół zaliczenia)

Protokół zaliczenia praktyki zawodowej pełni rolę raportu końcowego – podsumowuje
oceny cząstkowe, składowe (S, U, Z, E) oraz ocenę końcową K wyliczaną wg wzoru
`K = 0,4·E + 0,1·S + 0,2·U + 0,3·Z`.

**Opis procesu generowania:** pełny, krokowy opis znajduje się w głównym README
projektu – [README → Moduł generowania PDF](../../README.md#moduł-generowania-pdf).

**Weryfikacja danych (PDF ↔ baza):**

| Praktyka               | Ocena końcowa (K) zgodna | Data zaliczenia zgodna | Liczba stron |
| ---------------------- | ------------------------ | ---------------------- | ------------ |
| #1 Marek Testowy       | ✓ (4,5)                  | ✓ (04.06.2026)         | 1            |
| #4 Anna Demonstracyjna | ✓ (4)                    | ✓ (05.03.2026)         | 1            |
| #7 Michał Mierzwa      | ✓ (5)                    | ✓ (22.12.2025)         | 1            |

**Analiza poprawności:**

| Element dokumentu                | Status | Uwagi                                                           |
| -------------------------------- | ------ | --------------------------------------------------------------- |
| Kompletność raportu              | OK     | Miejsce praktyki, oceny S/U/Z/E/K, skład komisji, pytania       |
| Poprawność podsumowań            | OK     | Ocena K wyliczona wg wzoru zgodna z wartością w bazie           |
| Poprawność dat                   | OK     | Data zaliczenia zgodna z rekordem `ProtokolZaliczenia`          |
| Zgodność z dokumentacją praktyki | OK     | Oceny U/Z pobierane z Karty praktyki (Zał. 3.2)                 |
| Formatowanie dokumentu           | OK     | Cały protokół mieści się na **jednej stronie** (wzór oryginału) |

> Podgląd: [Podglady/Zal8.png](Podglady/Zal8.png)

---

## Testowanie szablonów dokumentów PDF

Wszystkie szablony korzystają ze wspólnego arkusza `_PDF_CSS` (zdefiniowanego w
[app/api/pdf.py](../../app/api/pdf.py)) – zapewnia to spójny wygląd: te same marginesy
strony (`@page margin: 1,2cm 1,3cm 1,7cm 1,3cm`), tę samą czcionkę, jednolite tabele
i wspólną stopkę z numeracją stron.

**Zrzuty ekranu dokumentów** (pierwsza strona każdego typu, praktyka #7):
katalog [Podglady/](Podglady/) – `Zal1.png` … `Zal8.png`.

**Porównanie typów dokumentów:**

| Załącznik                      | Typ układu                    | Strony | Spójność stylu |
| ------------------------------ | ----------------------------- | ------ | -------------- |
| Zał. 1 – Porozumienie          | tekst + tabela §              | 1      | OK             |
| Zał. 2a – Harmonogram          | dwie tabele (działy + efekty) | 2      | OK             |
| Zał. 3.1 – Karta str. 1        | tekst + potwierdzenia         | 1      | OK             |
| Zał. 3.2 – Karta str. 2        | tabele ocen                   | 1      | OK             |
| Zał. 4 – Potwierdzenie efektów | tabela 13 efektów             | 2      | OK             |
| Zał. 5 – Ankieta               | tabela pytań (skala)          | 2      | OK             |
| Zał. 6 – Dziennik              | tabela 120 wpisów             | 4–5    | OK             |
| Zał. 7 – Sprawozdanie          | sekcje opisowe                | 1      | OK             |
| Zał. 8 – Protokół              | formularz złożony             | 1      | OK             |

**Wskazane elementy poprawione w ramach etapu** (historia w sekcji _Raport błędów_):
marginesy i łamanie stron (eliminacja stron-sierot), czytelność tabel (pełna
szerokość kolumn), spójny styl podpisów (imię i nazwisko zamiast „pieczątek").

**Elementy do ewentualnej dalszej poprawy (niski priorytet):**

- tła nagłówków tabel (`#e8edf3`) wymagają drukarki kolorowej – przy druku mono są
  jasnoszare, ale czytelne; można rozważyć wzmocnienie obramowań,
- przy bardzo długich nazwach działów/firm tabela Zał. 2a może wymagać dostrojenia
  proporcji kolumn.

---

## Weryfikacja pobierania plików PDF

**Weryfikacja po stronie aplikacji:**

| Element                        | Status | Uwagi                                                                        |
| ------------------------------ | ------ | ---------------------------------------------------------------------------- |
| Działanie przycisku pobierania | OK     | „Otwórz →" / „Pobierz PDF/ZIP" na pulpicie                                   |
| Poprawność nazw plików         | OK     | `Praktyka_<id>_<Załącznik>.pdf`, ZIP: `Praktyka_<id>_<Nazwisko_Imie>.zip`    |
| Poprawność rozszerzeń          | OK     | `application/pdf` oraz `application/zip`                                     |
| Endpoint generujący PDF        | OK     | `/api/pdf/<id>/<zal_key>`, `/api/pdf/<id>/zip`, `/api/pdf/generate-pdf/<id>` |
| Reakcja na błąd generowania    | OK     | komunikat flash + przekierowanie na pulpit; w ZIP – plik `_BLEDY.txt`        |
| Kontrola dostępu               | OK     | student pobiera wyłącznie własne dokumenty (`_check_access` → 403)           |

Odporność endpointu na błędne dane została potwierdzona automatycznie – zob. poniżej
(przypadki 7–8: nieistniejące ID praktyki → HTTP 404, nieprawidłowy
klucz załącznika → kontrolowany wyjątek).

**Weryfikacja z różnych przeglądarek:**

| Przeglądarka | Pobranie pojedynczego PDF | Pobranie ZIP | Nazwa/rozszerzenie pliku | Zrzut                                       |
| ------------ | ------------------------- | ------------ | ------------------------ | ------------------------------------------- |
| Opera GX     | OK                        | OK           | operagx-zbiorczy         | [Link](./Zrzuty/zbiorcze/operagx-zbiorczy/) |
| Edge         | OK                        | OK           | edge-zbiorczy            | [Link](./Zrzuty/zbiorcze/edge-zbiorczy/)    |

---

## Testowanie odporności modułu PDF

Zautomatyzowany zestaw testów: [tools/test_pdf_resilience.py](../../tools/test_pdf_resilience.py).
Skrypt tworzy dane brzegowe w transakcji i wycofuje ją (ROLLBACK) – nie zaśmieca bazy.
Wykonano **13 przypadków testowych** (wymóg: min. 10), wszystkie zaliczone:

| Nr  | Przypadek testowy                        | Oczekiwany wynik                        | Status |
| --- | ---------------------------------------- | --------------------------------------- | ------ |
| 1   | Zał. 6 dla praktyki bez wpisów dziennika | poprawny PDF (pusta tabela)             | PASS   |
| 2   | Zał. 8 bez protokołu (puste oceny)       | poprawny PDF z polami pustymi           | PASS   |
| 3   | Zał. 7 bez sprawozdania                  | poprawny PDF („nie wypełniono")         | PASS   |
| 4   | Zał. 5 bez wypełnionej ankiety           | poprawny PDF                            | PASS   |
| 5   | Zał. 2a bez harmonogramu i efektów       | poprawny PDF                            | PASS   |
| 6   | Zał. 7 z tekstem 50 000 znaków           | poprawny PDF wielostronicowy (16 str.)  | PASS   |
| 7   | Nieistniejące ID praktyki                | kontrolowany wyjątek HTTP 404           | PASS   |
| 8   | Nieprawidłowy klucz załącznika           | kontrolowany wyjątek (TemplateNotFound) | PASS   |
| 9   | Puste komórki `<td></td>`                | wypełniane twardą spacją                | PASS   |
| 10  | Wstrzyknięcie HTML/JS w danych           | neutralizowane (autoescaping Jinja)     | PASS   |
| 11  | Konwersja jednostek `rem`/`em`           | poprawna zamiana na `px`                | PASS   |
| 12  | Polskie znaki w danych                   | zachowane po przetworzeniu              | PASS   |
| 13  | Symbole ✓ ☐ ✗                            | owijane osobnym fontem symboli          | PASS   |

**Opis błędów (wykrytych i zabezpieczonych):**

- _puste komórki tabel_ zwijały całą tabelę do minimalnej szerokości w xhtml2pdf –
  zabezpieczone automatycznym wypełnianiem twardą spacją (`_strip_for_pdf`),
- _symbole ✓ ☐ ✗_ renderowały się jako puste kwadraty (Arial nie ma tych glifów) –
  zabezpieczone rejestracją osobnego fontu Segoe UI Symbol,
- _brakujące rekordy powiązane_ (dziennik/ankieta/protokół) – szablony obsługują
  wartości `None` i wyświetlają puste pola / „nie wypełniono".

**Propozycje zabezpieczeń modułu (zrealizowane):**

1. obsługa wartości `None` we wszystkich szablonach (brak wyjątków przy pustych danych),
2. eksport zbiorczy odporny na pojedynczy błąd – uszkodzony załącznik trafia do
   `_BLEDY.txt`, reszta paczki generuje się normalnie,
3. autoescaping Jinja chroni przed wstrzyknięciem HTML/JS przez dane użytkownika,
4. kontrola dostępu (`_check_access`) – student nie pobierze cudzych dokumentów.

---

## Analiza techniczna modułu PDF

**Struktura kodu.** Cały moduł to jeden, uporządkowany plik
[app/api/pdf.py](../../app/api/pdf.py) (~430 linii) z wyraźnym podziałem:
rejestracja czcionek (`_ensure_fonts`), przetwarzanie HTML (`_resolve_vars`,
`_strip_for_pdf`), budowa kontekstu (`_build_context`), rdzeń renderujący
(`_render_pdf_bytes`), pakowanie ZIP (`_zip_attachments`) oraz endpointy (`pdf_bp`).

**Sposób generowania.** HTML z szablonu Jinja2 → dostosowanie do xhtml2pdf →
`pisa.CreatePDF()` → bajty PDF. Bez przeglądarki i procesów zewnętrznych – pełen
proces opisano w [README → Moduł generowania PDF](../../README.md#moduł-generowania-pdf).

**Organizacja szablonów.** Szablony w [templates/formularze/](../../templates/formularze/)
są współdzielone przez widok HTML i wersję PDF; elementy interfejsu (`.no-print`,
przyciski, panele) są ukrywane wspólnym arkuszem `_PDF_CSS` – jedno źródło prawdy.

**Komunikacja backendu z modułem.** Endpointy blueprinta `pdf_bp` przyjmują żądania,
weryfikują dostęp, wołają `_render_pdf_bytes()` i zwracają plik przez `send_file()`.
Funkcja `_render_pdf_bytes()` jest też wywoływana bezpośrednio przez skrypty w
`tools/` – ten sam kod obsługuje aplikację i testy (odtwarzalność).

**Lista bibliotek.**

| Biblioteka     | Wersja | Rola                                             |
| -------------- | ------ | ------------------------------------------------ |
| xhtml2pdf      | 0.2.17 | silnik HTML/CSS → PDF                            |
| reportlab      | 4.5.1  | osadzanie czcionek TTF, niskopoziomowy rendering |
| Flask / Jinja2 | 3.1.x  | routing endpointów i szablony                    |
| zipfile        | stdlib | eksport zbiorczy do ZIP                          |

**Wydajność** (czcionki rozgrzane; pomiar na maszynie deweloperskiej):

| Dokument                    | Czas    | Rozmiar |
| --------------------------- | ------- | ------- |
| Zał. 1 (1 str.)             | ~80 ms  | 106 KB  |
| Zał. 5 (2 str.)             | ~150 ms | 131 KB  |
| Zał. 8 (1 str.)             | ~110 ms | 126 KB  |
| Zał. 6 (4 str., 120 wpisów) | ~500 ms | 92 KB   |
| ZIP – komplet 9 załączników | ~1,2 s  | –       |

**Propozycje optymalizacji:**

- _cache czcionek_ – `_ensure_fonts()` już rejestruje czcionki raz na proces (flaga
  `_fonts_registered`); to główny zysk, dalsze cache'owanie zbędne,
- generowanie ZIP można by zrównoleglić (`concurrent.futures`), ale przy ~1,2 s dla
  kompletu nie jest to konieczne,
- dla bardzo dużych dzienników (>200 wpisów) można rozważyć stronicowanie zapytania,
  obecnie 120 wpisów generuje się w ~0,5 s.

---

## Rozszerzenia funkcjonalne

| Funkcjonalność                            | Status | Realizacja                                                               |
| ----------------------------------------- | ------ | ------------------------------------------------------------------------ |
| Generowanie wielu dokumentów jednocześnie | OK     | `_zip_attachments()` w pętli po wybranych załącznikach                   |
| Podpisy tekstowe                          | OK     | imię i nazwisko + linia na datę (zamiast „pieczątek" – druk mono)        |
| Eksport zbiorczy                          | OK     | panel na pulpicie + endpoint `/api/pdf/<id>/zip`                         |
| Poprawność nazw generowanych plików       | OK     | `Praktyka_<id>_<Nazwisko_Imie>.zip`, pliki w środku z czytelnymi nazwami |
| Pobranie archiwum ZIP                     | OK     | `mimetype application/zip`, `Content-Disposition: attachment`            |

**Przykładowe dokumenty zbiorcze:** katalog [`_pdfout/`](../../_pdfout/) zawiera
komplet załączników dla 3 praktyk; eksport ZIP odtwarzalny skryptem
[tools/generate_pdf_samples.py](../../tools/generate_pdf_samples.py).

**Analiza poprawności:** eksport zbiorczy jest odporny na pojedynczy błąd – gdy
jednego załącznika nie da się wygenerować, pozostałe trafiają do ZIP, a opis błędu
do pliku `_BLEDY.txt` (potwierdzone w _Zadaniu 6_).

---

## Raport błędów (historia napraw modułu PDF)

| #   | Objaw                                          | Przyczyna                                 | Naprawa                                         |
| --- | ---------------------------------------------- | ----------------------------------------- | ----------------------------------------------- |
| 1   | Polskie znaki jako czarne kwadraty             | domyślna Helvetica bez glifów PL          | rejestracja czcionki Arial (TTF)                |
| 2   | Ptaszki/checkboxy jako puste kwadraty          | Arial nie ma glifów ✓ ☐ ✗                 | osobny font Segoe UI Symbol + owijanie symboli  |
| 3   | Tabele „rozjechane" (Zał. 8)                   | puste komórki `<td></td>` zwijają kolumny | automatyczne wypełnianie twardą spacją          |
| 4   | Strony-sieroty (sam podpis na osobnej stronie) | brak `page-break-inside: avoid`           | reguły CSS + zagęszczenie układu                |
| 5   | Zielone „pieczątki" podpisów                   | nieczytelne przy druku mono               | podpis = imię i nazwisko + linia na datę        |
| 6   | Zał. 8 rozlewał się na 2. stronę               | zbyt duże odstępy/`line-height`           | zagęszczenie układu → 1 strona (wzór oryginału) |
| 7   | Przycisk „Powrót" widoczny w PDF               | inline `display:flex` nadpisywał ukrycie  | dopisywanie `display:none` do `.no-print`       |

---

## Odtworzenie wszystkich testów

```bash
# (raz) trzecia kompletna praktyka – daje min. 3 użytkowników
.\venv\Scripts\python.exe tools\seed_extra.py

# przykładowe dokumenty PDF → _pdfout/
.\venv\Scripts\python.exe tools\generate_pdf_samples.py

# testy odporności (13 przypadków, kod wyjścia 0 = OK)
.\venv\Scripts\python.exe tools\test_pdf_resilience.py
```
