"""
Seed uzupełniający — tworzy trzecią, w pełni wypełnioną praktykę dla studenta
Michał Mierzwa (nr albumu 21273), aby moduł weryfikacji PDF dysponował
minimum trzema różnymi użytkownikami z kompletem danych (Zadanie 1 i 2 z lab11).

Dane tej praktyki różnią się od demonstracyjnej (inna firma, inne oceny, inne
opisy) — dzięki temu porównanie PDF - baza danych jest miarodajne.

Uruchomienie:
    .\\venv\\Scripts\\python.exe tools\\seed_extra.py

Skrypt jest idempotentny — jeśli praktyka już istnieje, nie tworzy duplikatu.
"""

import sys, os
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta

from app import create_app, db
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

NR_ALBUMU = '21273'
DATA_OD = date(2025, 7, 1)
DATA_DO = date(2025, 12, 19)


def _next_biz_days(start, count):
    days, cur = [], start
    while len(days) < count:
        if cur.weekday() < 5:
            days.append(cur)
        cur += timedelta(days=1)
    return days


def seed():
    app = create_app()
    with app.app_context():
        student = Student.query.filter_by(nr_albumu=NR_ALBUMU).first()
        if not student:
            print(f'  [BŁĄD] Brak studenta o nr albumu {NR_ALBUMU}. Uruchom najpierw aplikację (seed kont).')
            return None

        # Uzupełnij brakujące pola studenta (były „Nieznany"/None)
        if student.kierunek in (None, '', 'Nieznany'):
            student.kierunek = 'Informatyka'
        if not student.specjalnosc:
            student.specjalnosc = 'Inżynieria Oprogramowania'

        existing = Internship.query.filter_by(id_studenta=student.id_studenta).first()
        if existing:
            print(f'  [--] Praktyka dla {student.imie} {student.nazwisko} już istnieje (id={existing.id_formularza}).')
            db.session.commit()
            return existing.id_formularza

        firma = Firma.query.filter_by(nazwa='InnoTech Solutions Sp. z o.o.').first()
        if not firma:
            firma = Firma(
                nazwa='InnoTech Solutions Sp. z o.o.',
                adres='al. Grunwaldzka 120, 80-244 Gdańsk',
                przedstawiciel='Barbara Lewandowska',
            )
            db.session.add(firma)
            db.session.flush()

        p = Internship(
            id_studenta=student.id_studenta,
            id_firmy=firma.id_firmy,
            data_od=DATA_OD,
            data_do=DATA_DO,
            liczba_dni_roboczych=120,
            status='zakończona',
            faza_procesu=4,
            nr_porozumienia='2025/IIS/00127',
            data_porozumienia=date(2025, 6, 16),
            zal1_zopz=True, zal1_dyrektor=True,
            zal2a_zopz=True, zal2a_student=True, zal2a_uopz=True,
            zal31_dyrektor=True, zal32_zgloszenie_zopz=True, zal32_bhp_zopz=True,
            dziennik_zatwierdzony=True,
            zal3_strona2_zopz=True, zal3_strona2_uopz=True,
            zal4_zopz=True, zal4_uopz=True,
            zal4_opinia_uopz='Efekty kształcenia osiągnięte na poziomie bardzo dobrym — student wykazał się dużą samodzielnością.',
            zal5_student=True, zal7_student=True, zal7_zopz=True,
            zal8_dyrektor=True, zal8_uopz=True, usos_wpisany=True,
        )
        db.session.add(p)
        db.session.flush()
        fid = p.id_formularza

        efekty = EfektKsztalcenia.query.order_by(EfektKsztalcenia.id_efektu).all()
        opisy_prac = [
            'Wytwarzanie oprogramowania zgodnie z normami jakości ISO',
            'Praca z chmurą Azure i konteneryzacją (Docker, Kubernetes)',
            'Analiza wymagań licencyjnych i prawnych komponentów open-source',
            'Projektowanie mikroserwisów i architektury zdarzeniowej',
            'Programowanie w językach Python oraz TypeScript',
            'Automatyzacja testów end-to-end (Playwright, pytest)',
            'Tworzenie dokumentacji API w standardzie OpenAPI 3.0',
            'Udział w warsztatach Design Thinking z klientem',
            'Optymalizacja zapytań i indeksów w bazie PostgreSQL',
            'Refaktoryzacja zgodnie z zasadami SOLID i clean architecture',
            'Konfiguracja potoków CI/CD w GitHub Actions',
            'Code review i mentoring młodszych członków zespołu',
            'Prowadzenie demonstracji sprintowych dla interesariuszy',
        ]
        for efekt, opis in zip(efekty, opisy_prac):
            db.session.add(EfektFormularza(id_formularza=fid, id_efektu=efekt.id_efektu, opis_prac=opis))

        dzialy = [
            ('Zespół Backend (Python)',          35),
            ('Zespół Frontend (TypeScript)',     20),
            ('Zespół QA / Automatyzacja testów', 20),
            ('Zespół Platform / DevOps',         25),
            ('Zadania projektowe — praca własna', 20),
        ]
        for i, (dzial, dni) in enumerate(dzialy, 1):
            db.session.add(HarmonogramPraktyki(
                id_formularza=fid, lp=i, dzial_komorka=dzial, planowana_liczba_dni=dni))

        db.session.add(KartaPraktyki(
            id_formularza=fid,
            data_szkolenia_bhp=DATA_OD,
            data_podpisu=date(2025, 12, 15),
            uwagi_odbycie='Praktyka zrealizowana w pełnym wymiarze; student zaangażowany i samodzielny.',
            ocena_zopz_param='5',
            ocena_zopz_opis='Wzorowa postawa, bardzo wysokie kompetencje techniczne i interpersonalne.',
            ocena_uopz_param='5',
            ocena_uopz_opis='Wszystkie efekty kształcenia osiągnięte w stopniu bardzo dobrym.',
            ocena_sprawozdania='5',
        ))

        dziennik = DziennikPraktyki(id_formularza=fid, status='Zamknięty')
        db.session.add(dziennik)
        db.session.flush()
        opisy_dni = [
            'Wdrożenie do projektu, konfiguracja środowiska i dostępów do repozytoriów.',
            'Analiza architektury mikroserwisowej systemu wraz z opiekunem.',
            'Implementacja endpointu REST w usłudze zamówień (FastAPI).',
            'Pokrycie nowego kodu testami jednostkowymi i integracyjnymi.',
            'Konfiguracja potoku CI w GitHub Actions dla usługi.',
            'Optymalizacja zapytań SQL i dodanie indeksów w PostgreSQL.',
            'Udział w przeglądzie kodu (code review) i nanoszenie poprawek.',
            'Przygotowanie dokumentacji OpenAPI dla nowych endpointów.',
            'Praca nad widokiem frontendowym w React/TypeScript.',
            'Demonstracja sprintowa wyników pracy dla zespołu i klienta.',
        ]
        biz_days = _next_biz_days(DATA_OD, 120)
        efekt_kody = [e.kod for e in efekty]
        for i, day in enumerate(biz_days, 1):
            opis = opisy_dni[i % len(opisy_dni)]
            kody = ','.join(efekt_kody[(i-1) % 13:((i-1) % 13)+2] or efekt_kody[:2])
            db.session.add(WpisDziennika(
                id_dziennika=dziennik.id_dziennika, nr_dnia=i, data_wpisu=day,
                opis_wykonanych_prac=f'Dzień {i}: {opis}', nr_efektow=kody))

        db.session.add(Sprawozdanie(
            id_formularza=fid,
            charakterystyka_miejsca=(
                'Praktykę odbyłem w firmie InnoTech Solutions Sp. z o.o. w Gdańsku — software house '
                'realizującym projekty dla sektora fintech i przemysłu 4.0. Firma pracuje w metodyce '
                'Scrum, wykorzystuje chmurę Microsoft Azure oraz architekturę mikroserwisową. '
                'Zespół, do którego zostałem przydzielony, liczył ośmiu inżynierów.'),
            opis_i_analiza_prac=(
                'W czasie praktyki rozwijałem usługi backendowe w językach Python i TypeScript, '
                'projektowałem i implementowałem REST API, konfigurowałem potoki CI/CD w GitHub Actions '
                'oraz automatyzowałem testy end-to-end (Playwright). Optymalizowałem zapytania bazodanowe '
                'w PostgreSQL i uczestniczyłem w przeglądach kodu. Praca wymagała znajomości konteneryzacji '
                '(Docker) i podstaw orkiestracji (Kubernetes).'),
            samoocena_kompetencji=(
                'Praktyka pozwoliła mi zastosować wiedzę akademicką w realnych projektach komercyjnych. '
                'Rozwinąłem kompetencje w zakresie architektury rozproszonej, testowania automatycznego oraz '
                'pracy zespołowej z wykorzystaniem Git. Uważam, że osiągnąłem wszystkie zakładane efekty '
                'uczenia się i jestem lepiej przygotowany do pracy zawodowej inżyniera oprogramowania.'),
        ))

        db.session.add(Ankieta(
            id_formularza=fid,
            q1='zd_tak', q2='zd_tak', q3='zd_tak', q4='zd_tak', q5='zd_tak',
            q6='zd_tak', q7='zd_tak', q8='zd_tak', q9='rk_tak', q10='zd_tak',
            q11='zd_tak', q12='zd_tak', q13='zd_tak', q14='zd_tak',
            uwagi='Bardzo dobrze zorganizowana praktyka, profesjonalny zespół i ciekawe zadania.',
            rok_akademicki='2025/2026', forma_studiow='stacjonarne', semestr='7', liczba_godzin=960,
        ))

        for efekt in efekty:
            db.session.add(PotwierdzenieEfektu(id_formularza=fid, id_efektu=efekt.id_efektu, czy_uzyskany=1))

        ocena_p1, ocena_p2, ocena_p3, ocena_s = '5', '4.5', '5', '5'
        ocena_u, ocena_z = 5.0, 5.0
        ocena_e = (float(ocena_p1) + float(ocena_p2) + float(ocena_p3)) / 3
        ocena_k = 0.4 * ocena_e + 0.1 * float(ocena_s) + 0.2 * ocena_u + 0.3 * ocena_z
        db.session.add(ProtokolZaliczenia(
            id_formularza=fid,
            data_zaliczenia=date(2025, 12, 22),
            czlonek_1='dr hab. Marek Kowalski, prof. ANS (Przewodniczący)',
            czlonek_2='mgr inż. Jan Nowak (UOPZ)',
            czlonek_3='dr inż. Katarzyna Wójcik',
            czlonek_4='',
            pytanie_1='Omów architekturę mikroserwisową systemu, przy którym pracowałeś.',
            pytanie_2='Jak skonfigurowałeś potok CI/CD i jakie testy w nim uruchamiano?',
            pytanie_3='Opisz proces optymalizacji zapytań bazodanowych w trakcie praktyki.',
            ocena_p1=ocena_p1, ocena_p2=ocena_p2, ocena_p3=ocena_p3, ocena_s=ocena_s,
            ocena_e=f'{ocena_e:.2f}', ocena_k=f'{ocena_k:.2f}', ocena_finalna=_round_grade(ocena_k),
        ))

        db.session.commit()
        print(f'  [OK] Praktyka dla {student.imie} {student.nazwisko} ({NR_ALBUMU}) utworzona, id={fid}, '
              f'ocena końcowa {_round_grade(ocena_k)}')
        return fid


if __name__ == '__main__':
    seed()
