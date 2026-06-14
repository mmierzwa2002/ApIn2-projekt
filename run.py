import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from flask import redirect
from werkzeug.security import generate_password_hash
from app import create_app, db

app = create_app()


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/auth/login')


def ensure_schema():
    """Dodaje brakujące kolumny do istniejącej bazy (prosta migracja)."""
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    migrations = {
        'formularze_praktyk': {
            'zal32_zgloszenie_zopz': 'BOOLEAN DEFAULT FALSE',
            'zal32_bhp_zopz': 'BOOLEAN DEFAULT FALSE',
            'zal7_zopz': 'BOOLEAN DEFAULT FALSE',
            'zal3_strona2_zopz': 'BOOLEAN DEFAULT FALSE',
            'zal3_strona2_uopz': 'BOOLEAN DEFAULT FALSE',
        },
        'wpisy_dziennika': {
            'nr_efektow': 'VARCHAR(50)',
        },
        'karty_praktyki': {
            'uwagi_odbycie': 'TEXT',
            'ocena_zopz_param': 'VARCHAR(4)',
            'ocena_zopz_opis': 'TEXT',
            'ocena_uopz_param': 'VARCHAR(4)',
            'ocena_uopz_opis': 'TEXT',
            'ocena_sprawozdania': 'VARCHAR(4)',
        },
    }
    added = []
    for table, cols in migrations.items():
        if table not in tables:
            continue
        existing = {c['name'] for c in inspector.get_columns(table)}
        for name, ddl in cols.items():
            if name not in existing:
                db.session.execute(text(f'ALTER TABLE {table} ADD COLUMN {name} {ddl}'))
                added.append(f'{table}.{name}')
    if added:
        db.session.commit()
        print(f"[SCHEMA] Dodano kolumny: {', '.join(added)}\n")


def seed_test_accounts():
    from app.models.user import User

    test_accounts = [
        {'email': 'admin@test.local',    'full_name': 'Admin Testowy',    'role': 'administrator', 'password': 'admin123'},
        {'email': 'uopz@test.local',     'full_name': 'Jan Kowalski',     'role': 'uopz',          'password': 'uopz123'},
        {'email': 'zopz@test.local',     'full_name': 'Piotr Zielinski',  'role': 'zopz',          'password': 'zopz123'},
        {'email': 'dyrektor@test.local', 'full_name': 'Anna Nowak',       'role': 'dyrektor',      'password': 'dyrektor123'},
        {'email': 'student@test.local',  'full_name': 'Marek Testowy',    'role': 'student',       'password': 'student123'},
        {'email': 'pending@test.local',  'full_name': 'Nowy Pracownik',   'role': 'konto_do_zatwierdzenia', 'password': 'pending123'},
    ]

    created = []
    for acc in test_accounts:
        if not User.query.filter_by(email=acc['email']).first():
            user = User(
                email=acc['email'],
                full_name=acc['full_name'],
                auth_provider='local',
                role=acc['role'],
                password_hash=generate_password_hash(acc['password']),
            )
            db.session.add(user)
            created.append(f"  {acc['role']:15} {acc['email']}  /  {acc['password']}")

    if created:
        db.session.commit()
        print("\n[SEED] Utworzono konta testowe:")
        for line in created:
            print(line)
        print()
    else:
        print("[SEED] Konta testowe już istnieją — pominięto.\n")


def seed_efekty_ksztalcenia():
    from app.models.outcome import EfektKsztalcenia
    efekty = [
        ('01', 'Ma wiedzę na temat sposobu realizacji zadań inżynierskich dotyczących informatyki z zachowaniem standardów i norm technicznych'),
        ('02', 'Zna technologie, narzędzia, metody, techniki oraz sprzęt stosowane w informatyce'),
        ('03', 'Zna ekonomiczne, prawne skutki własnych działań podejmowanych w ramach praktyki oraz ograniczenia wynikające z prawa autorskiego i kodeksu pracy'),
        ('04', 'Zna zasady bezpieczeństwa pracy i ergonomii w zawodzie informatyka'),
        ('05', 'Pozyskuje informacje odnośnie technologii, metod, technik, sprzętu wymaganego do realizacji powierzonego zadania, posługując się rozmaitymi źródłami literaturowymi i zasobami publikowanymi w języku polskim jak i angielskim'),
        ('06', 'W oparciu o kontakty ze środowiskiem inżynierskim zakładu, potrafi podnieść swoje kompetencje, wiedzę i umiejętności, co najmniej z dwóch zakresów: zadania dotyczące sprzętu i oprogramowania: np.: programowania, administrowanie siecią komputerową, konserwacja sprzętu i oprogramowania, bieżące usuwanie usterek, administrowanie zasobami informatycznymi, zakładu pracy / instytucji, (e)-usługami'),
        ('07', 'Opracowuje dokumentację dotyczącą realizacji podejmowanych zadań w ramach praktyki, a także referuje ustnie prezentowane w niej zagadnienia'),
        ('08', 'Potrafi zidentyfikować problem informatyczny występujący w zakładzie pracy / instytucji, opisać go, przedstawić koncepcję rozwiązania i ją zrealizować'),
        ('09', 'Potrafi rozwiązać rzeczywiste zadanie inżynierskie z zakresu działalności informatycznej zakładu pracy/instytucji stosując normy i standardy stosowane w informatyce oraz biorąc pod uwagę aspekty środowiskowe i etyczne'),
        ('10', 'Pracuje w zespole zajmującym się zawodowo branżą IT'),
        ('11', 'Przestrzega zasad etyki zawodowej i zgodnie z tymi zasadami korzysta z wiedzy i pomocy doświadczonych kolegów'),
        ('12', 'Kontaktując się z osobami spoza branży potrafi zarówno pozyskać od nich niezbędne informacje do realizacji planowanego zadania, jak i przekazać im w sposób zrozumiały informacje i opinie z zakresu informatyki'),
        ('13', 'Dostrzega w praktyce tempo deaktualizacji wiedzy informatycznej oraz skutki działalności informatyków w szczególności ekonomiczne i społeczne'),
    ]
    created = []
    for kod, opis in efekty:
        if not EfektKsztalcenia.query.filter_by(kod=kod).first():
            db.session.add(EfektKsztalcenia(kod=kod, opis=opis))
            created.append(kod)
    if created:
        db.session.commit()
        print(f"[SEED] Dodano efekty kształcenia: {', '.join(created)}\n")
    else:
        print("[SEED] Efekty kształcenia już istnieją — pominięto.\n")


def seed_test_data():
    from datetime import date
    from app.models.user import User
    from app.models.student import Student
    from app.models.company import Firma
    from app.models.internship import Internship

    student_user = User.query.filter_by(email='student@test.local').first()
    if not student_user:
        print("[SEED] Konto studenta nie istnieje — pomiń seed danych.\n")
        return

    created = []

    if not Student.query.filter_by(user_id=student_user.id).first():
        student = Student(
            user_id=student_user.id,
            imie='Marek',
            nazwisko='Testowy',
            nr_albumu='21000',
            kierunek='Informatyka',
            specjalnosc='Aplikacje internetowe',
        )
        db.session.add(student)
        db.session.flush()
        created.append('  studenci    Marek Testowy (21000)')
    else:
        student = Student.query.filter_by(user_id=student_user.id).first()

    firma = Firma.query.filter_by(nazwa='ABC Software Sp. z o.o.').first()
    if not firma:
        firma = Firma(
            nazwa='ABC Software Sp. z o.o.',
            adres='ul. Informatyczna 5, 82-300 Elbląg',
            przedstawiciel='Krzysztof Wiśniewski',
        )
        db.session.add(firma)
        db.session.flush()
        created.append('  firmy       ABC Software Sp. z o.o.')

    if not Internship.query.filter_by(id_studenta=student.id_studenta).first():
        internship = Internship(
            id_studenta=student.id_studenta,
            id_firmy=firma.id_firmy,
            data_od=date(2025, 9, 1),
            data_do=date(2026, 2, 28),
            faza_procesu=1,
            status='roboczy',
            nr_porozumienia='2025/IIS/001',
            data_porozumienia=date(2025, 8, 15),
        )
        db.session.add(internship)
        created.append(f'  praktyka    Marek Testowy → ABC Software (2025/IIS/001)')

    if created:
        db.session.commit()
        print("[SEED] Utworzono dane testowe:")
        for line in created:
            print(line)
        print()
    else:
        print("[SEED] Dane testowe już istnieją — pominięto.\n")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_schema()
        seed_test_accounts()
        seed_test_data()
        seed_efekty_ksztalcenia()

    app.run(debug=True, port=5000)
