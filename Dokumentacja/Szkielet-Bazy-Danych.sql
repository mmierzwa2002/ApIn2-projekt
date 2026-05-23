CREATE TABLE Role (
    id_roli INTEGER PRIMARY KEY AUTOINCREMENT,
    nazwa_roli VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Uzytkownicy (
    id_uzytkownika INTEGER PRIMARY KEY AUTOINCREMENT,
    id_roli INTEGER NOT NULL,
    imie VARCHAR(100) NOT NULL,
    nazwisko VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    numer_albumu VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_roli) REFERENCES Role(id_roli)
);

CREATE TABLE Dzienniki_Praktyk (
    id_dziennika INTEGER PRIMARY KEY AUTOINCREMENT,
    id_studenta INTEGER NOT NULL,
    id_opiekuna INTEGER,
    nazwa_zakladu VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'Draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_studenta) REFERENCES Uzytkownicy(id_uzytkownika),
    FOREIGN KEY (id_opiekuna) REFERENCES Uzytkownicy(id_uzytkownika)
);

CREATE TABLE Wpisy_Dziennika (
    id_wpisu INTEGER PRIMARY KEY AUTOINCREMENT,
    id_dziennika INTEGER NOT NULL,
    data_wpisu DATE NOT NULL,
    opis_prac TEXT NOT NULL,
    efekty_uczenia VARCHAR(100),
    uwagi_opiekuna TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_dziennika) REFERENCES Dzienniki_Praktyk(id_dziennika) ON DELETE CASCADE
);