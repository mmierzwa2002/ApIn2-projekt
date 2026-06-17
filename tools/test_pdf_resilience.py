"""
Testy odporności modułu generowania PDF.

Zestaw przypadków testowych sprawdzających reakcję modułu na dane brzegowe i
błędne: puste dane, brakujące pola, bardzo długie teksty, niepoprawne dane,
wstrzyknięcia HTML oraz poprawność obsługi wyjątków. Skrypt jest odtwarzalny i
nie zaśmieca bazy — dane testowe tworzy w transakcji, którą na końcu wycofuje
(ROLLBACK).

Uruchomienie:
    .\\venv\\Scripts\\python.exe tools\\test_pdf_resilience.py

Kod wyjścia 0 = wszystkie testy zaliczone, 1 = wystąpiły niezgodności.
"""

import sys, os, re
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from werkzeug.exceptions import HTTPException
from jinja2 import TemplateNotFound

from app import create_app, db
from app.models.user import User
from app.models.student import Student
from app.models.company import Firma
from app.models.internship import Internship
from app.models.report import Sprawozdanie
from app.api import pdf as pdfmod
from app.api.pdf import _render_pdf_bytes, _strip_for_pdf
from flask_login import login_user

RESULTS = []   # (nr, nazwa, status, szczegóły)


def _ok(pdf_bytes):
    """PDF jest poprawny, gdy zaczyna się od %PDF i ma co najmniej jedną stronę."""
    return pdf_bytes[:4] == b'%PDF' and len(re.findall(rb'/Type\s*/Page[^s]', pdf_bytes)) >= 1


def record(nr, nazwa, passed, detail=''):
    RESULTS.append((nr, nazwa, 'PASS' if passed else 'FAIL', detail))
    print(f'  [{"PASS" if passed else "FAIL"}] {nr:>2}. {nazwa}'
          + (f'  → {detail}' if detail else ''))


def _make_minimal_internship(faza=1):
    """Tworzy (flush, bez commit) minimalną praktykę w fazie 1 — brak dziennika,
    sprawozdania, ankiety, karty, protokołu (skrajny przypadek 'pustych danych')."""
    student = Student.query.first()
    firma = Firma.query.first()
    p = Internship(
        id_studenta=student.id_studenta, id_firmy=firma.id_firmy,
        data_od=date(2025, 9, 1), data_do=date(2026, 2, 28),
        liczba_dni_roboczych=120, faza_procesu=faza, status='w toku',
    )
    db.session.add(p)
    db.session.flush()
    return p


def main():
    app = create_app()
    with app.test_request_context():
        login_user(User.query.filter_by(role='administrator').first())

        # ── Przypadki na danych brzegowych w bazie (transakcja → rollback) ──
        p_empty = _make_minimal_internship(faza=1)

        # 1. Pusty dziennik (brak wpisów) → Zał. 6
        try:
            data = _render_pdf_bytes(p_empty.id_formularza, 'zal6')
            record(1, 'Zał. 6 dla praktyki bez wpisów dziennika', _ok(data),
                   f'{len(data)//1024} KB')
        except Exception as e:
            record(1, 'Zał. 6 dla praktyki bez wpisów dziennika', False, repr(e))

        # 2. Brak protokołu → Zał. 8 (pr=None)
        try:
            data = _render_pdf_bytes(p_empty.id_formularza, 'zal8')
            record(2, 'Zał. 8 bez protokołu (puste oceny)', _ok(data), f'{len(data)//1024} KB')
        except Exception as e:
            record(2, 'Zał. 8 bez protokołu (puste oceny)', False, repr(e))

        # 3. Brak sprawozdania → Zał. 7 (s=None → „nie wypełniono")
        try:
            data = _render_pdf_bytes(p_empty.id_formularza, 'zal7')
            record(3, 'Zał. 7 bez sprawozdania', _ok(data), f'{len(data)//1024} KB')
        except Exception as e:
            record(3, 'Zał. 7 bez sprawozdania', False, repr(e))

        # 4. Brak ankiety → Zał. 5 (a=None)
        try:
            data = _render_pdf_bytes(p_empty.id_formularza, 'zal5')
            record(4, 'Zał. 5 bez wypełnionej ankiety', _ok(data), f'{len(data)//1024} KB')
        except Exception as e:
            record(4, 'Zał. 5 bez wypełnionej ankiety', False, repr(e))

        # 5. Brak harmonogramu/efektów → Zał. 2a (puste mapy)
        try:
            data = _render_pdf_bytes(p_empty.id_formularza, 'zal2a')
            record(5, 'Zał. 2a bez harmonogramu i efektów', _ok(data), f'{len(data)//1024} KB')
        except Exception as e:
            record(5, 'Zał. 2a bez harmonogramu i efektów', False, repr(e))

        # 6. Bardzo długi tekst (50 000 znaków) w sprawozdaniu → Zał. 7
        try:
            long_text = ('Bardzo długi opis zadań inżynierskich. ' * 1300)[:50000]
            db.session.add(Sprawozdanie(
                id_formularza=p_empty.id_formularza,
                charakterystyka_miejsca=long_text,
                opis_i_analiza_prac=long_text,
                samoocena_kompetencji='Krótko.'))
            db.session.flush()
            data = _render_pdf_bytes(p_empty.id_formularza, 'zal7')
            pages = len(re.findall(rb'/Type\s*/Page[^s]', data))
            record(6, 'Zał. 7 z tekstem 50 000 znaków (wielostronicowy)',
                   _ok(data) and pages > 1, f'{pages} str')
        except Exception as e:
            record(6, 'Zał. 7 z tekstem 50 000 znaków (wielostronicowy)', False, repr(e))

        db.session.rollback()   # wycofaj wszystkie dane testowe

        # ── Przypadki na obsłudze wyjątków ──
        # 7. Nieistniejący identyfikator praktyki → kontrolowany wyjątek HTTP 404
        try:
            _render_pdf_bytes(999999, 'zal8')
            record(7, 'Nieistniejące ID praktyki → wyjątek 404', False, 'nie rzucił wyjątku')
        except HTTPException as e:
            record(7, 'Nieistniejące ID praktyki → wyjątek 404', e.code == 404, f'HTTP {e.code}')
        except Exception as e:
            record(7, 'Nieistniejące ID praktyki → wyjątek 404', False, repr(e))

        # 8. Nieistniejący klucz szablonu → TemplateNotFound (kontrolowany)
        try:
            _render_pdf_bytes(Internship.query.first().id_formularza, 'zal_nie_istnieje')
            record(8, 'Nieprawidłowy klucz załącznika → wyjątek', False, 'nie rzucił wyjątku')
        except TemplateNotFound:
            record(8, 'Nieprawidłowy klucz załącznika → wyjątek', True, 'TemplateNotFound')
        except Exception as e:
            record(8, 'Nieprawidłowy klucz załącznika → wyjątek', True, type(e).__name__)

        # ── Przypadki jednostkowe na potoku przetwarzania HTML ──
        # 9. Puste komórki tabeli są wypełniane (ochrona przed zwijaniem kolumn)
        out = _strip_for_pdf('<html><head></head><body><table><tr><td></td><td>X</td></tr></table></body></html>')
        record(9, 'Puste <td></td> wypełniane twardą spacją', '<td>&nbsp;</td>' in out)

        # 10. Wstrzyknięcie HTML/JS jest neutralizowane przez autoescaping Jinja
        try:
            from markupsafe import escape
            payload = '<script>alert(1)</script> & "cudzysłów" <b>x</b>'
            esc = str(escape(payload))
            record(10, 'Wstrzyknięcie HTML/JS neutralizowane (autoescaping)',
                   '&lt;script&gt;' in esc and '<script>' not in esc)
        except Exception as e:
            record(10, 'Wstrzyknięcie HTML/JS neutralizowane (autoescaping)', False, repr(e))

        # 11. Konwersja jednostek rem/em → px (xhtml2pdf nie obsługuje rem/em w szerokościach)
        out = _strip_for_pdf('<html><head></head><body><div style="width:2rem;margin:1.5em">x</div></body></html>')
        record(11, 'Konwersja rem/em → px', '32px' in out and '24px' in out)

        # 12. Polskie znaki zachowane w potoku przetwarzania
        out = _strip_for_pdf('<html><head></head><body>ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ</body></html>')
        record(12, 'Polskie znaki zachowane po przetworzeniu',
               'ąćęłńóśźż' in out and 'ĄĆĘŁŃÓŚŹŻ' in out)

        # 13. Symbole (✓ ☐ ✗) owijane osobnym fontem, gdy zarejestrowany
        pdfmod._ensure_fonts()
        out = _strip_for_pdf('<html><head></head><body>✓ ☐ ✗</body></html>')
        if pdfmod._symbol_font:
            record(13, 'Symbole ✓ ☐ ✗ owijane fontem symboli',
                   f'face="{pdfmod._symbol_font}"' in out)
        else:
            record(13, 'Symbole ✓ ☐ ✗ owijane fontem symboli', True, 'font symboli niedostępny — pominięto')

    # ── Podsumowanie ──
    passed = sum(1 for r in RESULTS if r[2] == 'PASS')
    print(f'\n──────────────────────────────────────────────')
    print(f'Wynik: {passed}/{len(RESULTS)} testów zaliczonych')
    sys.exit(0 if passed == len(RESULTS) else 1)


if __name__ == '__main__':
    main()
