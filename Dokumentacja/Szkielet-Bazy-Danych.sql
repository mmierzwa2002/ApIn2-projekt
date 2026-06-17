CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255),
    password_hash VARCHAR(255),
    auth_provider VARCHAR(50) DEFAULT 'microsoft',
    external_id VARCHAR(255) UNIQUE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('student', 'zopz', 'uopz', 'dyrektor', 'administrator', 'konto_do_zatwierdzenia')),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE studenci (
    id_studenta SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE,                 -- powiązanie z kontem logowania
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    nr_albumu VARCHAR(20) NOT NULL UNIQUE,
    kierunek VARCHAR(100) NOT NULL,
    specjalnosc VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE firmy (
    id_firmy SERIAL PRIMARY KEY,
    nazwa VARCHAR(255) NOT NULL,
    adres VARCHAR(255)
);

CREATE TABLE opiekunowie (
    id_opiekuna SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE,                 -- powiązanie z kontem logowania
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    typ_opiekuna VARCHAR(30) NOT NULL CHECK (typ_opiekuna IN ('uczelniany', 'zakladowy')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE efekty_ksztalcenia (
    id_efektu SERIAL PRIMARY KEY,
    kod VARCHAR(2) NOT NULL UNIQUE,
    opis TEXT NOT NULL
);

-- 2. ENCJA CENTRALNA — FORMULARZ PRAKTYKI (silnik faz + cyfrowe podpisy)
CREATE TABLE formularze_praktyk (
    id_formularza SERIAL PRIMARY KEY,
    id_studenta INTEGER NOT NULL,
    id_firmy INTEGER NOT NULL,
    data_od DATE NOT NULL,
    data_do DATE NOT NULL,
    liczba_dni_roboczych INTEGER,           -- uzupełniane po zakończeniu Fazy 2 (= 120)
    status VARCHAR(30) DEFAULT 'roboczy',

    -- KONTROLA FAZ (1=Inicjacja, 2=Realizacja, 3=Podsumowanie, 4=Zaliczenie/Zakończone)
    faza_procesu INTEGER NOT NULL DEFAULT 1 CHECK (faza_procesu BETWEEN 1 AND 4),

    -- Metadane Porozumienia (Zał. 1)
    nr_porozumienia VARCHAR(50),
    data_porozumienia DATE,

    -- FAZA 1: INICJACJA
    zal1_zopz BOOLEAN DEFAULT FALSE,             -- Porozumienie (Zakład)
    zal1_dyrektor BOOLEAN DEFAULT FALSE,         -- Porozumienie (Uczelnia)
    zal2a_zopz BOOLEAN DEFAULT FALSE,            -- Harmonogram (Zakład)
    zal2a_student BOOLEAN DEFAULT FALSE,         -- Harmonogram (Student)
    zal2a_uopz BOOLEAN DEFAULT FALSE,            -- Harmonogram (Uczelnia)
    zal31_dyrektor BOOLEAN DEFAULT FALSE,        -- Skierowanie / Karta str. 1 (Dyrektor)
    zal32_zgloszenie_zopz BOOLEAN DEFAULT FALSE, -- Potwierdzenie zgłoszenia studenta (Zakład)
    zal32_bhp_zopz BOOLEAN DEFAULT FALSE,        -- Potwierdzenie szkolenia BHP (Zakład)

    -- FAZA 2: REALIZACJA
    dziennik_zatwierdzony BOOLEAN DEFAULT FALSE, -- 120 dni wpisane i zatwierdzone przez ZOPZ

    -- FAZA 3: PODSUMOWANIE
    zal3_strona2_zopz BOOLEAN DEFAULT FALSE,     -- Karta str. 2: zaświadczenie + ocena zakładowa (ZOPZ)
    zal3_strona2_uopz BOOLEAN DEFAULT FALSE,     -- Karta str. 2: ocena uczelniana + ocena sprawozdania (UOPZ)
    zal4_zopz BOOLEAN DEFAULT FALSE,             -- Potwierdzenie efektów (Zakład)
    zal4_opinia_uopz TEXT,                       -- Opinia UOPZ do Zał. 4
    zal4_uopz BOOLEAN DEFAULT FALSE,             -- Potwierdzenie efektów (Uczelnia)
    zal5_student BOOLEAN DEFAULT FALSE,          -- Kwestionariusz ankiety (Student)
    zal7_student BOOLEAN DEFAULT FALSE,          -- Sprawozdanie złożone (Student)
    zal7_zopz BOOLEAN DEFAULT FALSE,             -- Sprawozdanie potwierdzone (Zakład)

    -- FAZA 4: ZALICZENIE
    zal8_dyrektor BOOLEAN DEFAULT FALSE,         -- Protokół końcowy — Przewodniczący Komisji (Dyrektor)
    zal8_uopz BOOLEAN DEFAULT FALSE,             -- Protokół — podpis uczelnianego opiekuna (UOPZ)
    usos_wpisany BOOLEAN DEFAULT FALSE,          -- Wpis zaliczenia do USOS (UOPZ) -> praktyka zakończona

    FOREIGN KEY (id_studenta) REFERENCES studenci(id_studenta) ON DELETE CASCADE,
    FOREIGN KEY (id_firmy) REFERENCES firmy(id_firmy) ON DELETE CASCADE,
    CHECK (data_do >= data_od)
);

CREATE TABLE formularz_opiekunowie (
    id_formularza INTEGER NOT NULL,
    id_opiekuna INTEGER NOT NULL,
    PRIMARY KEY (id_formularza, id_opiekuna),
    FOREIGN KEY (id_formularza) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE,
    FOREIGN KEY (id_opiekuna) REFERENCES opiekunowie(id_opiekuna) ON DELETE CASCADE
);

-- 3. HARMONOGRAM I EFEKTY (Zał. 2a)
CREATE TABLE harmonogram_praktyki (
    id_harmonogramu SERIAL PRIMARY KEY,
    id_formularza INTEGER NOT NULL,
    lp INTEGER NOT NULL,
    dzial_komorka VARCHAR(255) NOT NULL,
    planowana_liczba_dni INTEGER NOT NULL CHECK (planowana_liczba_dni > 0),
    FOREIGN KEY (id_formularza) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE,
    UNIQUE (id_formularza, lp)
);

CREATE TABLE efekty_formularza (
    id_formularza INTEGER NOT NULL,
    id_efektu INTEGER NOT NULL,
    opis_prac TEXT NOT NULL,
    PRIMARY KEY (id_formularza, id_efektu),
    FOREIGN KEY (id_formularza) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE,
    FOREIGN KEY (id_efektu) REFERENCES efekty_ksztalcenia(id_efektu) ON DELETE CASCADE
);

-- 4. KARTA PRAKTYKI (Zał. 3.1 / 3.2)
CREATE TABLE karty_praktyki (
    id_karty SERIAL PRIMARY KEY,
    id_formularza INTEGER NOT NULL UNIQUE,
    data_szkolenia_bhp DATE,
    ocena_zakladowa INTEGER CHECK (ocena_zakladowa BETWEEN 2 AND 5),
    ocena_uczelniana INTEGER CHECK (ocena_uczelniana BETWEEN 2 AND 5),
    data_podpisu DATE,

    -- Zał. 3.2 = Karta praktyki STRONA 2 (po praktyce)
    uwagi_odbycie TEXT,                 -- zaświadczenie odbycia — uwagi
    ocena_zopz_param VARCHAR(4),        -- ocena ZOPZ parametryczna (2–5)
    ocena_zopz_opis TEXT,              -- ocena ZOPZ opisowa
    ocena_uopz_param VARCHAR(4),        -- ocena UOPZ parametryczna (2–5)
    ocena_uopz_opis TEXT,              -- ocena UOPZ opisowa
    ocena_sprawozdania VARCHAR(4),      -- ocena sprawozdania (UOPZ, 2–5)

    FOREIGN KEY (id_formularza) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE
);

-- 5. POTWIERDZENIA EFEKTÓW (Zał. 4)
CREATE TABLE potwierdzenia_efektow (
    id_potwierdzenia SERIAL PRIMARY KEY,
    id_formularza INTEGER NOT NULL,
    id_efektu INTEGER NOT NULL,
    czy_uzyskany SMALLINT CHECK (czy_uzyskany IN (0, 1)),
    FOREIGN KEY (id_formularza) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE,
    FOREIGN KEY (id_efektu) REFERENCES efekty_ksztalcenia(id_efektu) ON DELETE CASCADE,
    UNIQUE (id_formularza, id_efektu)
);

-- 6. DZIENNIK PRAKTYK (Zał. 6)
CREATE TABLE dzienniki_praktyk (
    id_dziennika SERIAL PRIMARY KEY,
    id_formularza INTEGER NOT NULL UNIQUE,
    status VARCHAR(50) DEFAULT 'Draft',
    FOREIGN KEY (id_formularza) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE
);

CREATE TABLE wpisy_dziennika (
    id_wpisu SERIAL PRIMARY KEY,
    id_dziennika INTEGER NOT NULL,
    nr_dnia INTEGER CHECK (nr_dnia BETWEEN 1 AND 120),
    data_wpisu DATE NOT NULL,
    opis_wykonanych_prac TEXT NOT NULL,
    nr_efektow VARCHAR(50),             -- kody efektów uczenia się, np. "01, 05, 09"
    id_efektu INTEGER,
    FOREIGN KEY (id_dziennika) REFERENCES dzienniki_praktyk(id_dziennika) ON DELETE CASCADE,
    FOREIGN KEY (id_efektu) REFERENCES efekty_ksztalcenia(id_efektu) ON DELETE SET NULL,
    UNIQUE (id_dziennika, nr_dnia)
);

-- 7. SPRAWOZDANIE (Zał. 7)
CREATE TABLE sprawozdania (
    id_sprawozdania SERIAL PRIMARY KEY,
    id_formularza INTEGER NOT NULL UNIQUE,
    charakterystyka_miejsca TEXT NOT NULL,
    opis_i_analiza_prac TEXT NOT NULL,
    samoocena_kompetencji TEXT NOT NULL,
    FOREIGN KEY (id_formularza) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE
);

-- 8. ANKIETA / KWESTIONARIUSZ (Zał. 5)
CREATE TABLE ankiety (
    id SERIAL PRIMARY KEY,
    id_formularza INTEGER NOT NULL UNIQUE,
    q1 VARCHAR(10), q2 VARCHAR(10), q3 VARCHAR(10), q4 VARCHAR(10), q5 VARCHAR(10),
    q6 VARCHAR(10), q7 VARCHAR(10), q8 VARCHAR(10), q9 VARCHAR(10), q10 VARCHAR(10),
    q11 VARCHAR(10), q12 VARCHAR(10), q13 VARCHAR(10), q14 VARCHAR(10),
    uwagi TEXT,
    rok_akademicki VARCHAR(20),
    forma_studiow VARCHAR(20),
    semestr VARCHAR(10),
    liczba_godzin INTEGER,
    FOREIGN KEY (id_formularza) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE
);

-- 9. PROTOKÓŁ ZALICZENIA (Zał. 8)
CREATE TABLE protokoly_zaliczenia (
    id SERIAL PRIMARY KEY,
    id_formularza INTEGER NOT NULL UNIQUE,
    data_zaliczenia DATE,
    czlonek_1 VARCHAR(200),            -- Przewodniczący
    czlonek_2 VARCHAR(200),            -- UOPZ
    czlonek_3 VARCHAR(200),
    czlonek_4 VARCHAR(200),
    -- Pytania / mini-zadania + oceny cząstkowe
    pytanie_1 TEXT, pytanie_2 TEXT, pytanie_3 TEXT,
    ocena_p1 VARCHAR(5), ocena_p2 VARCHAR(5), ocena_p3 VARCHAR(5),
    ocena_s VARCHAR(5),                -- ocena za sprawozdanie
    ocena_e VARCHAR(6),               -- E = avg(p1,p2,p3)
    ocena_k VARCHAR(6),               -- K = 0.4E + 0.1S + 0.2U + 0.3Z
    ocena_finalna VARCHAR(5),          -- K zaokrąglone do skali
    FOREIGN KEY (id_formularza) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE
);

-- 10. ZAŁĄCZNIKI POMOCNICZE (uploady)
CREATE TABLE document (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    doc_type VARCHAR(100) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    internship_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'Weryfikacja',
    reviewer_comment TEXT,
    FOREIGN KEY (internship_id) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE
);
