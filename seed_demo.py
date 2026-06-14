"""
Seed demonstracyjny — tworzy studenta z całkowicie wypełnioną praktyką
(faza 4, usos_wpisany=True, wszystkie załączniki kompletne).

Uruchomienie:
    .\\venv\\Scripts\\python.exe seed_demo.py

Dane logowania:
    email:  demo@ans.elblag.pl
    hasło:  Demo1234!

Skrypt jest idempotentny — jeśli rekord już istnieje, nie tworzy duplikatu.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from datetime import date, timedelta
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.user import User
from app.models.student import Student
from app.models.company import Firma
from app.models.internship import Internship
from app.models.outcome import EfektKsztalcenia, EfektFormularza, PotwierdzenieEfektu
from app.models.schedule import HarmonogramPraktyki
from app.models.card import KartaPraktyki
from app.models.diary import DziennikPraktyki, WpisDziennika
from app.models.report import Sprawozdanie
from app.models.survey import Ankieta
from app.models.protocol import ProtokolZaliczenia, _round_grade

# ── konfiguracja danych demonstracyjnych ─────────────────────────────────────
EMAIL      = 'demo@ans.elblag.pl'
HASLO      = 'Demo1234!'
IMIE       = 'Anna'
NAZWISKO   = 'Demonstracyjna'
NR_ALBUMU  = 'DEMO001'
KIERUNEK   = 'Informatyka'
DATA_OD    = date(2025, 9, 1)
DATA_DO    = date(2026, 2, 28)


def _next_biz_days(start: date, count: int):
    """Generuje `count` kolejnych dni roboczych (pon–pt) zaczynając od `start`."""
    days, cur = [], start
    while len(days) < count:
        if cur.weekday() < 5:
            days.append(cur)
        cur += timedelta(days=1)
    return days


def seed():
    app = create_app()
    with app.app_context():

        # ── 1. Użytkownik ─────────────────────────────────────────────────────
        user = User.query.filter_by(email=EMAIL).first()
        if not user:
            user = User(
                email=EMAIL,
                full_name=f'{IMIE} {NAZWISKO}',
                auth_provider='local',
                external_id=f'local:{EMAIL}',
                role='student',
                is_active=True,
                password_hash=generate_password_hash(HASLO),
            )
            db.session.add(user)
            db.session.flush()
            print(f'  [OK]Użytkownik: {EMAIL}')
        else:
            print(f'  [--]Użytkownik już istnieje: {EMAIL}')

        # ── 2. Student ────────────────────────────────────────────────────────
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            student = Student(
                user_id=user.id,
                imie=IMIE,
                nazwisko=NAZWISKO,
                nr_albumu=NR_ALBUMU,
                kierunek=KIERUNEK,
                specjalnosc='Inżynieria Oprogramowania',
            )
            db.session.add(student)
            db.session.flush()
            print(f'  [OK]Student: {IMIE} {NAZWISKO} ({NR_ALBUMU})')
        else:
            print(f'  [--]Student już istnieje')

        # ── 3. Firma ──────────────────────────────────────────────────────────
        firma = Firma.query.filter_by(nazwa='Demo Software Sp. z o.o.').first()
        if not firma:
            firma = Firma(
                nazwa='Demo Software Sp. z o.o.',
                adres='ul. Informatyczna 5, 82-300 Elbląg',
                przedstawiciel='Krzysztof Wiśniewski',
            )
            db.session.add(firma)
            db.session.flush()
            print(f'  [OK]Firma: {firma.nazwa}')
        else:
            print(f'  [--]Firma już istnieje')

        # ── 4. Formularz praktyki ─────────────────────────────────────────────
        existing = Internship.query.filter_by(id_studenta=student.id_studenta).first()
        if existing:
            print(f'  [--]Formularz praktyki już istnieje (id={existing.id_formularza}), seed pomija.')
            db.session.commit()
            return existing.id_formularza

        p = Internship(
            id_studenta=student.id_studenta,
            id_firmy=firma.id_firmy,
            data_od=DATA_OD,
            data_do=DATA_DO,
            liczba_dni_roboczych=120,
            status='zakończona',
            faza_procesu=4,
            nr_porozumienia='2025/IIS/DEMO',
            data_porozumienia=date(2025, 8, 15),
            # Faza 1
            zal1_zopz=True,
            zal1_dyrektor=True,
            zal2a_zopz=True,
            zal2a_student=True,
            zal2a_uopz=True,
            zal31_dyrektor=True,
            zal32_zgloszenie_zopz=True,
            zal32_bhp_zopz=True,
            # Faza 2
            dziennik_zatwierdzony=True,
            # Faza 3
            zal3_strona2_zopz=True,
            zal3_strona2_uopz=True,
            zal4_zopz=True,
            zal4_uopz=True,
            zal4_opinia_uopz='Wszystkie efekty kształcenia zostały osiągnięte na poziomie dobrym.',
            zal5_student=True,
            zal7_student=True,
            zal7_zopz=True,
            # Faza 4
            zal8_dyrektor=True,
            usos_wpisany=True,
        )
        db.session.add(p)
        db.session.flush()
        fid = p.id_formularza
        print(f'  [OK]Formularz praktyki (id={fid})')

        # ── 5. Efekty kształcenia (Zał. 2a — harmonogram efektów) ────────────
        efekty = EfektKsztalcenia.query.order_by(EfektKsztalcenia.id_efektu).all()
        opisy_prac = [
            'Realizacja zadań inżynierskich zgodnych z normami technicznymi',
            'Obsługa narzędzi programistycznych i technologii webowych',
            'Analiza skutków prawnych i ekonomicznych wytwarzanego oprogramowania',
            'Projektowanie systemów informatycznych i dobór algorytmów',
            'Programowanie aplikacji z użyciem języka Python i frameworka Flask',
            'Testowanie oprogramowania — testy jednostkowe i integracyjne',
            'Tworzenie dokumentacji technicznej i użytkownika',
            'Komunikacja z klientem, zbieranie wymagań i analiza biznesowa',
            'Administrowanie bazą danych PostgreSQL, pisanie zapytań SQL',
            'Stosowanie wzorców projektowych i zasad clean code',
            'Wdrożenie aplikacji na serwer, konfiguracja środowiska produkcyjnego',
            'Praca z systemem kontroli wersji Git i GitHubem',
            'Uczestnictwo w zebraniach zespołu, raportowanie postępów',
        ]
        for efekt, opis in zip(efekty, opisy_prac):
            db.session.add(EfektFormularza(
                id_formularza=fid,
                id_efektu=efekt.id_efektu,
                opis_prac=opis,
            ))
        print(f'  [OK]EfektyFormularza (13 wpisów)')

        # ── 6. Harmonogram (Zał. 2a — działy) ───────────────────────────────
        dzialy = [
            ('Dział Programowania Aplikacji',   30),
            ('Dział Testowania i QA',            20),
            ('Dział Zarządzania Bazami Danych',  20),
            ('Dział DevOps i Wdrożeń',           20),
            ('Dział Analizy Biznesowej',         15),
            ('Zadania projektowe — praca własna', 15),
        ]
        for i, (dzial, dni) in enumerate(dzialy, 1):
            db.session.add(HarmonogramPraktyki(
                id_formularza=fid, lp=i, dzial_komorka=dzial, planowana_liczba_dni=dni
            ))
        print(f'  [OK]Harmonogram ({sum(d for _, d in dzialy)} dni)')

        # ── 7. Karta praktyki (Zał. 3.2) ─────────────────────────────────────
        db.session.add(KartaPraktyki(
            id_formularza=fid,
            data_szkolenia_bhp=date(2025, 9, 1),
            data_podpisu=date(2026, 2, 20),
            uwagi_odbycie='Student odbył praktykę w pełnym wymiarze, sumiennie wywiązując się z powierzonych zadań.',
            ocena_zopz_param='4',
            ocena_zopz_opis='Student wykazał się bardzo dobrą znajomością technologii oraz dużą samodzielnością.',
            ocena_uopz_param='4',
            ocena_uopz_opis='Efekty kształcenia zostały osiągnięte w stopniu dobrym.',
            ocena_sprawozdania='4',
        ))
        print('  ✓ KartaPraktyki (Zał. 3.2)')

        # ── 8. Dziennik (Zał. 6) — 120 dni roboczych ─────────────────────────
        dziennik = DziennikPraktyki(id_formularza=fid, status='Zamknięty')
        db.session.add(dziennik)
        db.session.flush()

        opisy_dni = [
            'Zapoznanie się ze strukturą organizacyjną firmy, środowiskiem pracy oraz narzędziami używanymi przez zespół.',
            'Konfiguracja środowiska deweloperskiego, instalacja wymaganych zależności i zapoznanie się z repozytorium Git.',
            'Analiza dokumentacji projektowej i omówienie architektury systemu z opiekunem zakładowym.',
            'Uczestnictwo w spotkaniu zespołu, przegląd backlogu zadań, pierwsze zadania programistyczne.',
            'Implementacja modułu autoryzacji użytkowników z użyciem Flask-Login.',
            'Pisanie testów jednostkowych dla zaimplementowanych endpointów API.',
            'Refaktoryzacja kodu zgodnie z komentarzami code review, poprawa czytelności.',
            'Projektowanie schematu bazy danych dla nowego modułu raportowania.',
            'Implementacja zapytań SQL oraz ORM dla modelu danych raportowania.',
            'Dokumentowanie API z użyciem Swagger/OpenAPI.',
        ]
        biz_days = _next_biz_days(DATA_OD, 120)
        efekt_kody = [e.kod for e in efekty]
        for i, day in enumerate(biz_days, 1):
            opis = opisy_dni[i % len(opisy_dni)]
            kody = ','.join(efekt_kody[(i-1) % 13:((i-1) % 13)+2] or efekt_kody[:2])
            db.session.add(WpisDziennika(
                id_dziennika=dziennik.id_dziennika,
                nr_dnia=i,
                data_wpisu=day,
                opis_wykonanych_prac=f'Dzień {i}: {opis}',
                nr_efektow=kody,
            ))
        print(f'  [OK]Dziennik praktyki (120 wpisów)')

        # ── 9. Sprawozdanie (Zał. 7) ─────────────────────────────────────────
        db.session.add(Sprawozdanie(
            id_formularza=fid,
            charakterystyka_miejsca=(
                'Praktyka zawodowa odbyła się w firmie Demo Software Sp. z o.o. z siedzibą w Elblągu, '
                'specjalizującej się w tworzeniu oprogramowania webowego dla klientów z branży logistycznej '
                'i e-commerce. Firma zatrudnia ok. 30 programistów pracujących w metodologii Scrum. '
                'Środowisko pracy jest nowoczesne — praca zdalna/hybrydowa, narzędzia Jira, Confluence, '
                'GitLab. Opiekunem zakładowym był starszy programista z pięcioletnim doświadczeniem.'
            ),
            opis_i_analiza_prac=(
                'W trakcie praktyki uczestniczyłam w rozwijaniu aplikacji webowej opartej na Pythonie (Flask) '
                'i bazodanowym backendzie PostgreSQL. Główne zadania obejmowały: implementację REST API, '
                'projektowanie i migrację schematu bazy danych, pisanie testów jednostkowych (pytest) '
                'oraz integracyjnych, a także udział w procesie code review. Zaznajomiłam się z '
                'narzędziami DevOps: Docker, GitLab CI/CD i wdrożeniami na serwery VPS. '
                'Realizacja zadań wymagała samodzielności, precyzji i umiejętności pracy w zespole.'
            ),
            samoocena_kompetencji=(
                'Praktyka w znacznym stopniu rozwinęła moje umiejętności programistyczne i projektowe. '
                'Nabyłam praktyczną wiedzę dotyczącą architektury REST, wzorców projektowych (Repository, '
                'Factory) oraz zasad SOLID. Udoskonaliłam umiejętności pracy z Git w środowisku '
                'wieloosobowym (feature branches, merge requests). Uznałam, że praktyka zawodowa jest '
                'nieodzownym uzupełnieniem kształcenia akademickiego i polecam tę formę kształcenia '
                'wszystkim studentom kierunków technicznych.'
            ),
        ))
        print('  ✓ Sprawozdanie (Zał. 7)')

        # ── 10. Ankieta (Zał. 5) ─────────────────────────────────────────────
        db.session.add(Ankieta(
            id_formularza=fid,
            q1='zd_tak', q2='zd_tak', q3='rk_tak', q4='zd_tak', q5='zd_tak',
            q6='zd_tak', q7='rk_tak', q8='rk_tak', q9='zd_tak', q10='rk_tak',
            q11='zd_tak', q12='zd_tak', q13='rk_tak', q14='rk_tak',
            uwagi='Praktyka bardzo dobrze zorganizowana, polecam to miejsce kolejnym studentom.',
            rok_akademicki='2025/2026',
            forma_studiow='stacjonarne',
            semestr='7',
            liczba_godzin=960,
        ))
        print('  ✓ Ankieta (Zał. 5)')

        # ── 11. Potwierdzenia efektów (Zał. 4) ───────────────────────────────
        for efekt in efekty:
            db.session.add(PotwierdzenieEfektu(
                id_formularza=fid,
                id_efektu=efekt.id_efektu,
                czy_uzyskany=1,
            ))
        print(f'  [OK]Potwierdzenia efektów (Zał. 4, 13 efektów)')

        # ── 12. Protokół zaliczenia (Zał. 8) ─────────────────────────────────
        ocena_p1, ocena_p2, ocena_p3, ocena_s = '4', '4.5', '4', '4'
        ocena_u = float(4)   # uopz (zal32 ocena_uopz_param)
        ocena_z = float(4)   # zopz (zal32 ocena_zopz_param)
        ocena_e = (float(ocena_p1) + float(ocena_p2) + float(ocena_p3)) / 3
        ocena_k = 0.4 * ocena_e + 0.1 * float(ocena_s) + 0.2 * ocena_u + 0.3 * ocena_z
        db.session.add(ProtokolZaliczenia(
            id_formularza=fid,
            data_zaliczenia=date(2026, 3, 5),
            czlonek_1='dr hab. Marek Kowalski, prof. ANS (Przewodniczący)',
            czlonek_2='mgr inż. Jan Nowak (UOPZ)',
            czlonek_3='mgr inż. Piotr Zieliński',
            czlonek_4='',
            pytanie_1='Omów architekturę aplikacji webowej zrealizowanej podczas praktyki.',
            pytanie_2='Jakie wzorce projektowe zastosowałaś i dlaczego?',
            pytanie_3='Opisz proces testowania oprogramowania w miejscu praktyki.',
            ocena_p1=ocena_p1,
            ocena_p2=ocena_p2,
            ocena_p3=ocena_p3,
            ocena_s=ocena_s,
            ocena_e=f'{ocena_e:.2f}',
            ocena_k=f'{ocena_k:.2f}',
            ocena_finalna=_round_grade(ocena_k),
        ))
        print(f'  [OK]Protokół zaliczenia (Zał. 8), ocena końcowa: {_round_grade(ocena_k)}')

        db.session.commit()
        print(f'\n  Seed zakończony. Formularz id={fid}')
        print(f'  Logowanie: {EMAIL} / {HASLO}')
        return fid


if __name__ == '__main__':
    fid = seed()
