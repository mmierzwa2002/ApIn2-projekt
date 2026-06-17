"""
Generowanie przykładowych dokumentów PDF (ETAP 11A — efekt końcowy).

Skrypt jest w pełni odtwarzalny: dla każdej praktyki w bazie generuje komplet
dostępnych załączników (Zał. 1–8) przy użyciu produkcyjnej funkcji
`app.api.pdf._render_pdf_bytes` — czyli dokładnie tego samego kodu, który
obsługuje pobieranie z poziomu aplikacji. Pliki trafiają do podkatalogów
`_pdfout/Praktyka_<id>_<Nazwisko_Imie>/`.

Na końcu drukuje tabelę podsumowującą (liczba stron, rozmiar) — przydatną do
dokumentacji testów.

Uruchomienie:
    .\\venv\\Scripts\\python.exe tools\\generate_pdf_samples.py
"""

import sys, os, re
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.internship import Internship
from app.models.user import User
from app.api.pdf import _render_pdf_bytes, _available_keys, ZALACZNIKI
from flask_login import login_user

OUT_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '_pdfout')
LABELS = dict(ZALACZNIKI)


def _count_pages(pdf_bytes):
    return len(re.findall(rb'/Type\s*/Page[^s]', pdf_bytes))


def main():
    app = create_app()
    with app.test_request_context():
        # render_template korzysta z context processora (current_user) — logujemy admina
        admin = User.query.filter_by(role='administrator').first()
        login_user(admin)

        internships = Internship.query.order_by(Internship.id_formularza).all()
        if not internships:
            print('Brak praktyk w bazie — uruchom aplikację (seed) oraz tools/seed_extra.py.')
            return

        os.makedirs(OUT_ROOT, exist_ok=True)
        rows = []
        for p in internships:
            s = p.student_record
            slug = f'{s.nazwisko}_{s.imie}'.replace(' ', '_')
            out_dir = os.path.join(OUT_ROOT, f'Praktyka_{p.id_formularza}_{slug}')
            os.makedirs(out_dir, exist_ok=True)
            print(f'\n=== Praktyka #{p.id_formularza} — {s.imie} {s.nazwisko} (faza {p.faza_procesu}) ===')
            for zal_key in _available_keys(p):
                fname = f'{LABELS[zal_key]}.pdf'
                try:
                    data = _render_pdf_bytes(p.id_formularza, zal_key)
                    with open(os.path.join(out_dir, fname), 'wb') as f:
                        f.write(data)
                    pages = _count_pages(data)
                    rows.append((p.id_formularza, zal_key, pages, len(data), 'OK'))
                    print(f'  [OK]  {fname:28} {pages} str  {len(data)//1024} KB')
                except Exception as e:
                    rows.append((p.id_formularza, zal_key, 0, 0, f'BŁĄD: {e}'))
                    print(f'  [BŁĄD] {fname:28} {e}')

        ok = sum(1 for r in rows if r[4] == 'OK')
        print(f'\n──────────────────────────────────────────────')
        print(f'Wygenerowano {ok}/{len(rows)} dokumentów do: {OUT_ROOT}')
        if ok != len(rows):
            print('UWAGA: część dokumentów zgłosiła błąd — zob. log powyżej.')


if __name__ == '__main__':
    main()
