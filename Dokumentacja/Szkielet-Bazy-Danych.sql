CREATE TABLE studenci (
    id_studenta INTEGER PRIMARY KEY AUTOINCREMENT,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    nr_albumu VARCHAR(20) NOT NULL UNIQUE,
    kierunek VARCHAR(100) NOT NULL,
    specjalnosc VARCHAR(100)
);

CREATE TABLE firmy (
    id_firmy INTEGER PRIMARY KEY AUTOINCREMENT,
    nazwa VARCHAR(255) NOT NULL,
    adres VARCHAR(255)
);

CREATE TABLE opiekunowie (
    id_opiekuna INTEGER PRIMARY KEY AUTOINCREMENT,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    typ_opiekuna VARCHAR(30) NOT NULL CHECK (typ_opiekuna IN ('uczelniany', 'zakladowy'))
);

CREATE TABLE formularze_praktyk (
    id_formularza INTEGER PRIMARY KEY AUTOINCREMENT,
    id_studenta INTEGER NOT NULL,
    id_firmy INTEGER NOT NULL,
    data_od DATE NOT NULL,
    data_do DATE NOT NULL,
    liczba_dni_roboczych INTEGER NOT NULL CHECK (liczba_dni_roboczych = 120),
    status VARCHAR(30) NOT NULL DEFAULT 'roboczy' CHECK (status IN ('roboczy', 'zatwierdzony', 'odrzucony')),
    FOREIGN KEY (id_studenta) REFERENCES studenci(id_studenta),
    FOREIGN KEY (id_firmy) REFERENCES firmy(id_firmy),
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
    id_efektu INTEGER PRIMARY KEY AUTOINCREMENT,
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
    id_harmonogramu INTEGER PRIMARY KEY AUTOINCREMENT,
    id_formularza INTEGER NOT NULL,
    lp INTEGER NOT NULL,
    dzial_komorka VARCHAR(255) NOT NULL,
    planowana_liczba_dni INTEGER NOT NULL CHECK (planowana_liczba_dni > 0),
    FOREIGN KEY (id_formularza) REFERENCES formularze_praktyk(id_formularza) ON DELETE CASCADE,
    UNIQUE (id_formularza, lp)
);