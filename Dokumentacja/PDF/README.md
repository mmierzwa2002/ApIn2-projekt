# Dokumentacja modułu generowania PDF

Weryfikacja i testy modułu generowania dokumentów PDF (załączniki praktyki Zał. 1–8).

## Zawartość

- **[Weryfikacja-PDF.md](Weryfikacja-PDF.md)** – pełna dokumentacja
  testów i weryfikacji: generowanie dziennika, potwierdzenia efektów,
  protokołu, testy szablonów, pobierania, odporności, analiza techniczna i
  rozszerzenia funkcjonalne. Zawiera raport błędów i instrukcję odtworzenia testów.
- **[Podglady/](Podglady/)** – podglądy (PNG) pierwszych stron wszystkich typów
  dokumentów (Zał. 1–8).

## Powiązane

- Kod modułu: [app/api/pdf.py](../../app/api/pdf.py)
- Szablony dokumentów: [templates/formularze/](../../templates/formularze/)
- Opis architektury i procesu generowania: [README → Moduł generowania PDF](../../README.md#moduł-generowania-pdf)
- Skrypty: [tools/seed_extra.py](../../tools/seed_extra.py),
  [tools/generate_pdf_samples.py](../../tools/generate_pdf_samples.py),
  [tools/test_pdf_resilience.py](../../tools/test_pdf_resilience.py)

## Przykładowe dokumenty

Wygenerowane pliki PDF znajdują się w katalogu [`_pdfout/`](../../_pdfout/)
(podkatalog na każdą praktykę). Odtworzenie:

```bash
.\venv\Scripts\python.exe tools\generate_pdf_samples.py
```
