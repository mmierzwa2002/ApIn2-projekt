import io
import os
import re
import zipfile
from flask import Blueprint, request, send_file, abort, render_template, redirect, flash, current_app
from flask_login import login_required, current_user
from xhtml2pdf import pisa
from xhtml2pdf.default import DEFAULT_FONT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from app.models.internship import Internship
from app.models.student import Student
from app import db

# ── Rejestracja czcionki z polskimi znakami ──────────────────────────────────
# xhtml2pdf domyślnie używa Helvetiki (Type1) bez glifów PL → polskie litery
# renderują się jako czarne kwadraty. Rejestrujemy TTF w reportlab ORAZ mapujemy
# nazwy font-family w słowniku xhtml2pdf, by 'font-family: Arial' wskazywał na
# osadzony font Unicode.
_fonts_registered = False
_symbol_font = None   # nazwa zarejestrowanego fontu z glifami ✓ ☐ ☑ ✗ (lub None)

# Kandydaci na pliki czcionek (Windows; pierwszy istniejący wygrywa)
_FONT_FILES = {
    'normal': [r'C:\Windows\Fonts\arial.ttf', r'C:\Windows\Fonts\segoeui.ttf'],
    'bold':   [r'C:\Windows\Fonts\arialbd.ttf', r'C:\Windows\Fonts\segoeuib.ttf'],
    'italic': [r'C:\Windows\Fonts\ariali.ttf', r'C:\Windows\Fonts\segoeuii.ttf'],
    # Font z symbolami (checkbox/ptaszek) — Arial ich nie ma, więc używamy osobnego
    'symbol': [r'C:\Windows\Fonts\seguisym.ttf', r'C:\Windows\Fonts\DejaVuSans.ttf'],
}

# Symbole wymagające osobnego fontu (Arial renderuje je jako puste kwadraty)
_SYMBOLE = '✓✔✗☐☑●'

def _first_existing(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def _ensure_fonts():
    """Rejestruje czcionkę PL raz na proces. Cicho pomija, gdy brak plików."""
    global _fonts_registered, _symbol_font
    if _fonts_registered:
        return
    _fonts_registered = True  # nie próbuj ponownie nawet przy częściowym braku
    normal = _first_existing(_FONT_FILES['normal'])
    if not normal:
        return  # brak czcionki TTF — render użyje domyślnej (bez polskich znaków)
    try:
        pdfmetrics.registerFont(TTFont('Arial', normal))
        family = {'normal': 'Arial'}
        bold = _first_existing(_FONT_FILES['bold'])
        if bold:
            pdfmetrics.registerFont(TTFont('Arial-Bold', bold))
            family['bold'] = 'Arial-Bold'
        italic = _first_existing(_FONT_FILES['italic'])
        if italic:
            pdfmetrics.registerFont(TTFont('Arial-Italic', italic))
            family['italic'] = 'Arial-Italic'
        pdfmetrics.registerFontFamily('Arial', **family)
        # Mapuj typowe nazwy rodzin na osadzony font (spójny wygląd + glify PL)
        for name in ('arial', 'helvetica', 'sans-serif', 'sans'):
            DEFAULT_FONT[name] = 'Arial'
    except Exception:
        current_app.logger.exception('Rejestracja czcionki PDF nie powiodła się')

    # Font z symbolami (✓ ☐ ☑ ✗) — Arial ich nie zawiera
    symbol = _first_existing(_FONT_FILES['symbol'])
    if symbol:
        try:
            pdfmetrics.registerFont(TTFont('SymbolPL', symbol))
            DEFAULT_FONT['symbolpl'] = 'SymbolPL'
            _symbol_font = 'SymbolPL'
        except Exception:
            current_app.logger.exception('Rejestracja fontu symboli nie powiodła się')

# Wartości jasnego motywu — xhtml2pdf nie obsługuje CSS custom properties
_CSS_VARS = {
    '--bg-main': '#e7ecf3',
    '--surface': '#ffffff',
    '--surface-alt': '#eef2f8',
    '--text-main': '#0f172a',
    '--text-muted': '#64748b',
    '--primary': '#0f766e',
    '--primary-hover': '#115e59',
    '--accent-blue': '#1d4ed8',
    '--warning': '#b45309',
    '--border': '#cbd5e1',
    '--shadow-card': 'none',
    '--radius': '8px',
}

def _resolve_vars(html: str) -> str:
    """Zastępuje var(--x) i var(--x, fallback) wartościami literalnymi."""
    def _sub(m):
        name = m.group(1)
        fallback = (m.group(2) or '').strip()
        return _CSS_VARS.get(name, fallback or '#000')
    return re.sub(r'var\((--[\w-]+)(?:,([^)]*))?\)', _sub, html)


def _strip_for_pdf(html: str) -> str:
    """Usuwa linki do arkuszy CSS i bloki <style>, następnie wstrzykuje _PDF_CSS."""
    html = re.sub(r'<link[^>]+>', '', html)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = _resolve_vars(html)
    # Elementy .no-print z inline 'display:flex/grid' nie znikają w PDF, bo inline
    # nadpisuje regułę CSS. Dopisz 'display:none' na końcu ich stylu (wygrywa
    # ostatnia deklaracja — działa też w xhtml2pdf).
    html = re.sub(r'class="no-print"(\s+style=")([^"]*)"',
                  lambda m: f'class="no-print"{m.group(1)}{m.group(2)};display:none"', html)
    # xhtml2pdf nie obsługuje rem/em w szerokościach — konwertuj na px (1rem=16px)
    html = re.sub(r'(\d*\.?\d+)rem', lambda m: f'{round(float(m.group(1))*16)}px', html)
    html = re.sub(r'(\d*\.?\d+)em', lambda m: f'{round(float(m.group(1))*16)}px', html)
    # Puste komórki <td></td>/<th></th> psują obliczanie szerokości kolumn w xhtml2pdf
    # (cała tabela zwija się do minimalnej szerokości) — wypełnij je twardą spacją.
    html = re.sub(r'<(td|th)([^>]*)>(\s*)</\1>', r'<\1\2>&nbsp;</\1>', html)
    # Symbole (✓ ☐ ☑ ✗) renderuj osobnym fontem — Arial pokazuje je jako kwadraty.
    if _symbol_font:
        for ch in _SYMBOLE:
            html = html.replace(ch, f'<font face="{_symbol_font}">{ch}</font>')
    html = html.replace('</head>', f'<style>{_PDF_CSS}</style></head>', 1)
    # Stopka z numeracją stron (xhtml2pdf renderuje ją w ramce footer_frame)
    footer = ('<div id="pdfFooter" style="text-align:center;font-size:8pt;color:#555">'
              'Strona <pdf:pagenumber> z <pdf:pagecount></div>')
    html = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + footer, html, count=1)
    return html


pdf_bp = Blueprint('pdf', __name__, url_prefix='/api/pdf')

# Które załączniki obsługujemy i w jakiej kolejności
ZALACZNIKI = [
    ('zal1',  'Zal1_Porozumienie'),
    ('zal2a', 'Zal2a_Harmonogram'),
    ('zal31', 'Zal31_Karta_str1'),
    ('zal32', 'Zal32_Karta_str2'),
    ('zal6',  'Zal6_Dziennik'),
    ('zal7',  'Zal7_Sprawozdanie'),
    ('zal4',  'Zal4_Efekty'),
    ('zal5',  'Zal5_Ankieta'),
    ('zal8',  'Zal8_Protokol'),
]


def _build_context(internship_id, zal_key):
    """Buduje kontekst szablonu dla danego załącznika."""
    from app.models.internship import Internship
    p = Internship.query.get_or_404(internship_id)

    ctx = {'p': p}

    if zal_key == 'zal2a':
        from app.models.outcome import EfektKsztalcenia, EfektFormularza
        from app.models.schedule import HarmonogramPraktyki
        all_efekty = EfektKsztalcenia.query.order_by(EfektKsztalcenia.id_efektu).all()
        efekty_map = {ef.id_efektu: ef.opis_prac
                      for ef in EfektFormularza.query.filter_by(id_formularza=internship_id).all()}
        harmonogram = HarmonogramPraktyki.query.filter_by(
            id_formularza=internship_id).order_by(HarmonogramPraktyki.lp).all()
        suma_dni = sum(h.planowana_liczba_dni for h in harmonogram)
        ctx.update(all_efekty=all_efekty, efekty_map=efekty_map,
                   harmonogram=harmonogram, zal2a_filled=(len(efekty_map) == 13 and suma_dni == 120))

    elif zal_key == 'zal32':
        from app.models.card import KartaPraktyki
        ctx['k'] = KartaPraktyki.query.filter_by(id_formularza=internship_id).first()
        ctx['oceny'] = ['2', '3', '3.5', '4', '4.5', '5']

    elif zal_key == 'zal6':
        from datetime import timedelta
        from app.models.diary import DziennikPraktyki
        from app.models.outcome import EfektKsztalcenia
        dziennik = DziennikPraktyki.query.filter_by(id_formularza=internship_id).first()
        wpisy = sorted(dziennik.wpisy, key=lambda w: w.nr_dnia) if dziennik else []
        all_efekty = EfektKsztalcenia.query.order_by(EfektKsztalcenia.kod).all()
        efekty_pokryte = set()
        for w in wpisy:
            for kod in (w.nr_efektow or '').replace(';', ',').split(','):
                kod = kod.strip()
                if kod:
                    efekty_pokryte.add(kod)
        ctx.update(wpisy=wpisy, all_efekty=all_efekty, wpisy_count=len(wpisy),
                   next_date=None, efekty_pokryte=sorted(efekty_pokryte),
                   brakujace_efekty=sorted({f'{i:02d}' for i in range(1, 14)} - efekty_pokryte))

    elif zal_key == 'zal7':
        from app.models.report import Sprawozdanie
        ctx['s'] = Sprawozdanie.query.filter_by(id_formularza=internship_id).first()

    elif zal_key == 'zal4':
        from app.models.outcome import EfektKsztalcenia, PotwierdzenieEfektu
        all_efekty = EfektKsztalcenia.query.order_by(EfektKsztalcenia.kod).all()
        potwierdzenia = {pe.id_efektu: pe
                         for pe in PotwierdzenieEfektu.query.filter_by(id_formularza=internship_id).all()}
        ctx.update(efekty=all_efekty, potwierdzenia=potwierdzenia)

    elif zal_key == 'zal5':
        from app.models.survey import Ankieta, PYTANIA_ZAL5, ODPOWIEDZI, ODPOWIEDZI_LABELS
        ankieta = Ankieta.query.filter_by(id_formularza=internship_id).first()
        d = p.data_od
        rok_ak = f'{d.year}/{d.year+1}' if d.month >= 9 else f'{d.year-1}/{d.year}'
        ctx.update(a=ankieta, pytania=PYTANIA_ZAL5, odpowiedzi=ODPOWIEDZI,
                   odpowiedzi_labels=ODPOWIEDZI_LABELS, rok_ak=rok_ak)

    elif zal_key == 'zal8':
        from app.models.protocol import ProtokolZaliczenia, OCENY_PROTOKOL
        from app.models.card import KartaPraktyki
        from app.models.user import User
        pr = ProtokolZaliczenia.query.filter_by(id_formularza=internship_id).first()
        karta = KartaPraktyki.query.filter_by(id_formularza=internship_id).first()
        uopz_users = User.query.filter_by(role='uopz').all()
        uopz_name = uopz_users[0].full_name if len(uopz_users) == 1 else ''
        ctx.update(pr=pr, k=karta, oceny=OCENY_PROTOKOL,
                   uopz_name=uopz_name, uopz_users=uopz_users)

    return ctx


_PDF_CSS = """
@page {
  size: a4 portrait;
  margin: 1.2cm 1.3cm 1.7cm 1.3cm;
  @frame footer_frame {
    -pdf-frame-content: pdfFooter;
    left: 40pt; right: 40pt; bottom: 20pt; height: 14pt;
  }
}
body { font-family: Arial; font-size: 9.5pt; color: #000; background: #fff; line-height: 1.3; }

/* Elementy interfejsu — w PDF zostaje sam dokument */
.nav-container, nav, .dok-toolbar, .dok-meta-panel, .academic-card,
.panel, .alert, .dok-blokada, .theme-toggle, .no-print,
form, button, .btn-academic, .btn-sm { display: none !important; }

/* Kontener dokumentu */
.dokument { max-width: 100%; margin: 0; padding: 0; border: none; box-shadow: none;
            font-size: 10pt; color: #000; }

/* Nagłówki dokumentu */
.dok-naglowek { text-align: right; font-size: 9pt; font-weight: bold; margin-bottom: 6pt; }
.dok-tytul { text-align: center; margin-bottom: 10pt; }
.dok-tytul h2 { font-size: 12pt; font-weight: bold; margin: 0 0 2pt; }
.dok-tytul p { font-size: 9.5pt; font-style: italic; margin: 0; }
h2 { font-size: 12pt; text-align: center; }
h3 { font-size: 10.5pt; }

/* Treść */
.dok-tresc p { margin: 0 0 3pt; text-align: justify; }
.dok-tresc ol, .dok-tresc ul { margin: 1pt 0 5pt 16pt; }
.dok-tresc li { margin-bottom: 1pt; }

/* Tabele */
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #333; padding: 2pt 4pt; vertical-align: top; font-size: 8.5pt; }
th { background: #e8edf3; font-weight: bold; text-align: center; }
thead { display: table-header-group; }   /* powtarzaj nagłówek na każdej stronie */

/* Linie / pola do wpisania */
.dok-blank { border-bottom: 1px solid #888; display: inline-block; min-width: 90px; }

/* ── Podpisy (czarno-białe, drukowalne) ── */
/* Cała sekcja podpisów trzymana razem, by nie „sierociała" na osobnej stronie */
.dok-podpisy { margin-top: 10pt; padding-top: 6pt; border-top: 1px solid #ccc; page-break-inside: avoid; }
.dok-podpis-box, .dok-podpis-blok, .dok-conf-box, .dok-ocena-blok {
  page-break-inside: avoid;
}
.dok-podpis-box { text-align: center; margin: 0 0 8pt; }
.dok-podpis-blok { margin-top: 10pt; }
.dok-podpis-osoba { font-weight: bold; font-size: 9.5pt; }
.dok-podpis-linia, .podpis-uopz-linia { border-top: 1px solid #333; width: 70%; margin: 14pt auto 2pt; }
.dok-podpis-opis, .podpis-uopz-opis, .podpis-opis { font-size: 8pt; color: #333; }

/* Neutralizacja dawnych „pieczątek" (gdyby gdzieś pozostały) */
.dok-pieczatka { padding: 0; font-weight: bold; background: none !important; color: #000 !important; }
.pieczatka-ok, .pieczatka-czeka { background: none !important; color: #000 !important; }
"""


def _render_pdf_bytes(internship_id, zal_key):
    """Renderuje szablon załącznika do PDF (xhtml2pdf) i zwraca bytes.

    Rzuca RuntimeError, gdy renderowanie się nie powiedzie — wywołujący decyduje,
    czy zgłosić błąd (pojedynczy PDF), czy odnotować w manifeście (ZIP).
    """
    _ensure_fonts()
    ctx = _build_context(internship_id, zal_key)
    html_str = render_template(f'formularze/{zal_key}.html', **ctx)
    html_str = _strip_for_pdf(html_str)

    result = io.BytesIO()
    status = pisa.CreatePDF(html_str, dest=result, encoding='utf-8')
    if status.err:
        raise RuntimeError(f'xhtml2pdf zgłosił {status.err} błąd(ów)')
    data = result.getvalue()
    if not data:
        raise RuntimeError('xhtml2pdf wygenerował pusty dokument')
    return data


def _zip_attachments(internship_id, keys):
    """Pakuje wybrane załączniki do archiwum ZIP.

    Zwraca (BytesIO, errors). Załączniki, których nie da się wygenerować, są
    pomijane, a ich opis trafia do pliku _BLEDY.txt wewnątrz archiwum — dzięki
    temu jeden uszkodzony dokument nie psuje całej paczki (odporność modułu).
    """
    labels = dict(ZALACZNIKI)
    zip_buffer = io.BytesIO()
    errors = []
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for zal_key in keys:
            label = labels.get(zal_key, zal_key)
            try:
                zf.writestr(f'{label}.pdf', _render_pdf_bytes(internship_id, zal_key))
            except Exception as e:
                current_app.logger.warning('PDF %s (#%s) pominięty: %s', zal_key, internship_id, e)
                errors.append(f'{label}: {e}')
        if errors:
            zf.writestr('_BLEDY.txt',
                        'Nie udało się wygenerować następujących załączników:\r\n\r\n'
                        + '\r\n'.join(errors))
    zip_buffer.seek(0)
    return zip_buffer, errors


def _check_access(internship):
    """Sprawdza dostęp — student może widzieć tylko własne praktyki."""
    if current_user.role == 'student':
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student or internship.id_studenta != student.id_studenta:
            abort(403)


# ── Pojedynczy PDF ────────────────────────────────────────────────────────────

def _available_keys(internship):
    """Lista załączników dostępnych dla danej fazy praktyki."""
    faza = internship.faza_procesu
    keys = ['zal1', 'zal2a', 'zal31']
    if faza >= 2:
        keys.append('zal6')
    if faza >= 3:
        keys += ['zal32', 'zal7', 'zal4', 'zal5']
    if faza >= 4:
        keys.append('zal8')
    return keys


def _name_slug(internship):
    s = internship.student_record
    return f'{s.nazwisko}_{s.imie}'.replace(' ', '_')


@pdf_bp.route('/<int:id>/<zal_key>')
@login_required
def generate_pdf(id, zal_key):
    """Generuje PDF dla jednego załącznika."""
    valid_keys = {k for k, _ in ZALACZNIKI}
    if zal_key not in valid_keys:
        abort(404)
    internship = Internship.query.get_or_404(id)
    _check_access(internship)

    try:
        pdf_bytes = _render_pdf_bytes(id, zal_key)
    except Exception as e:
        current_app.logger.exception('Błąd generowania PDF %s (#%s)', zal_key, id)
        flash(f'Nie udało się wygenerować dokumentu: {e}', 'danger')
        return redirect('/auth/dashboard')

    label = dict(ZALACZNIKI)[zal_key]
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        download_name=f'Praktyka_{id}_{label}.pdf',
        as_attachment=True
    )


# ── ZIP z wybranymi załącznikami ──────────────────────────────────────────────

@pdf_bp.route('/<int:id>/zip', methods=['POST'])
@login_required
def download_zip(id):
    """Generuje ZIP z załącznikami zaznaczonymi w panelu."""
    internship = Internship.query.get_or_404(id)
    _check_access(internship)

    valid_keys = {k for k, _ in ZALACZNIKI}
    selected = [k for k in request.form.getlist('zalaczniki') if k in valid_keys]
    if not selected:
        flash('Zaznacz co najmniej jeden załącznik.', 'warning')
        return redirect('/auth/dashboard')

    zip_buffer, errors = _zip_attachments(id, selected)
    # Gdy żaden dokument się nie wygenerował, nie wysyłaj pustej paczki
    if len(errors) == len(selected):
        flash('Nie udało się wygenerować żadnego z zaznaczonych załączników.', 'danger')
        return redirect('/auth/dashboard')

    return send_file(
        zip_buffer,
        mimetype='application/zip',
        download_name=f'Praktyka_{id}_{_name_slug(internship)}.zip',
        as_attachment=True
    )


# ── /generate-pdf/<id> ────────────────────────────

@pdf_bp.route('/generate-pdf/<int:id>')
@login_required
def generate_pdf_all(id):
    """Generuje ZIP ze wszystkimi dostępnymi załącznikami (eksport zbiorczy)."""
    internship = Internship.query.get_or_404(id)
    _check_access(internship)

    keys = _available_keys(internship)
    zip_buffer, errors = _zip_attachments(id, keys)
    if len(errors) == len(keys):
        flash('Nie udało się wygenerować żadnego załącznika.', 'danger')
        return redirect('/auth/dashboard')

    return send_file(
        zip_buffer,
        mimetype='application/zip',
        download_name=f'Praktyka_{id}_{_name_slug(internship)}_komplet.zip',
        as_attachment=True
    )
