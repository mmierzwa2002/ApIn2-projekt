CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(150) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    password_hash VARCHAR(256),
    auth_provider VARCHAR(50) DEFAULT 'local',
    external_id VARCHAR(250),
    role VARCHAR(50) NOT NULL CHECK (role IN ('student', 'zopz', 'uopz', 'dyrektor', 'administrator', 'konto_do_zatwierdzenia')),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE studenci (
    id_studenta SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE, -- Powiązanie z kontem logowania
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
    user_id INTEGER UNIQUE, -- Powiązanie z kontem logowania
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    typ_opiekuna VARCHAR(30) NOT NULL CHECK (typ_opiekuna IN ('uczelniany', 'zakladowy')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE formularze_praktyk (
    id_formularza SERIAL PRIMARY KEY,
    id_studenta INTEGER NOT NULL,
    id_firmy INTEGER NOT NULL,
    data_od DATE NOT NULL,
    data_do DATE NOT NULL,
    liczba_dni_roboczych INTEGER NOT NULL CHECK (liczba_dni_roboczych = 120),
    
    -- Status ogólny z Laboratorium 07
    status VARCHAR(30) NOT NULL DEFAULT 'roboczy' CHECK (status IN ('roboczy', 'zatwierdzony', 'odrzucony')),
    
    -- KONTROLA FAZ (Silnik Workflow)
    faza_procesu INTEGER DEFAULT 1 CHECK (faza_procesu BETWEEN 1 AND 5),
    
    -- CYFROWE PODPISY (Zatwierdzenia Załączników)
    zal1_zopz BOOLEAN DEFAULT FALSE,
    zal1_dyrektor BOOLEAN DEFAULT FALSE,
    zal2a_zopz BOOLEAN DEFAULT FALSE,
    zal2a_student BOOLEAN DEFAULT FALSE,
    zal2a_uopz BOOLEAN DEFAULT FALSE,
    zal31_dyrektor BOOLEAN DEFAULT FALSE,
    dziennik_zatwierdzony BOOLEAN DEFAULT FALSE,
    zal4_zopz BOOLEAN DEFAULT FALSE,
    zal4_uopz BOOLEAN DEFAULT FALSE,
    zal7_student BOOLEAN DEFAULT FALSE,
    zal8_dyrektor BOOLEAN DEFAULT FALSE,

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


CREATE TABLE efekty_ksztalcenia (
    id_efektu SERIAL PRIMARY KEY,
    kod VARCHAR(2) NOT NULL UNIQUE,
    opis TEXT NOT NULL
);

CREATE TABLE efekty_formularza (
    id_formularza INTEGER NOT NULL,
    id_efektu INTEGER NOT NULL,
    opis_prac TEXT NOT NULL,
    PRIMARY KEY (id_formularza, id_efektu),
    FOREIGN KEY (id_formularza) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE,
    FOREIGN KEY (id_efektu) REFERENCES efekty_ksztalcenia(id_efektu) ON DELETE CASCADE
);

CREATE TABLE harmonogram_praktyki (
    id_harmonogramu SERIAL PRIMARY KEY,
    id_formularza INTEGER NOT NULL,
    lp INTEGER NOT NULL,
    dzial_komorka VARCHAR(255) NOT NULL,
    planowana_liczba_dni INTEGER NOT NULL CHECK (planowana_liczba_dni > 0),
    FOREIGN KEY (id_formularza) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE,
    UNIQUE (id_formularza, lp)
);

-- 5. KARTY ZALICZEŃ I DZIENNIKI
CREATE TABLE karty_praktyki (
    id_karty SERIAL PRIMARY KEY,
    id_formularza INTEGER NOT NULL UNIQUE,
    data_szkolenia_bhp DATE,
    ocena_zakladowa INTEGER CHECK (ocena_zakladowa BETWEEN 2 AND 5),
    ocena_uczelniana INTEGER CHECK (ocena_uczelniana BETWEEN 2 AND 5),
    data_podpisu DATE,
    FOREIGN KEY (id_formularza) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE
);

CREATE TABLE potwierdzenia_efektow (
    id_potwierdzenia SERIAL PRIMARY KEY,
    id_formularza INTEGER NOT NULL,
    id_efektu INTEGER NOT NULL,
    czy_uzyskany SMALLINT CHECK (czy_uzyskany IN (0, 1)),
    FOREIGN KEY (id_formularza) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE,
    FOREIGN KEY (id_efektu) REFERENCES efekty_ksztalcenia(id_efektu) ON DELETE CASCADE,
    UNIQUE(id_formularza, id_efektu)
);

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
    id_efektu INTEGER,
    FOREIGN KEY (id_dziennika) REFERENCES dzienniki_praktyk(id_dziennika) ON DELETE CASCADE,
    FOREIGN KEY (id_efektu) REFERENCES efekty_ksztalcenia(id_efektu) ON DELETE SET NULL,
    UNIQUE(id_dziennika, nr_dnia)
);

CREATE TABLE sprawozdania (
    id_sprawozdania SERIAL PRIMARY KEY,
    id_formularza INTEGER NOT NULL UNIQUE,
    charakterystyka_miejsca TEXT NOT NULL,
    opis_i_analiza_prac TEXT NOT NULL,
    samoocena_kompetencji TEXT NOT NULL,
    FOREIGN KEY (id_formularza) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE
);