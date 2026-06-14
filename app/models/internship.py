from app import db

class Internship(db.Model):
    __tablename__ = 'formularze_praktyk'

    id_formularza = db.Column(db.Integer, primary_key=True)
    id_studenta = db.Column(db.Integer, db.ForeignKey('studenci.id_studenta'), nullable=False)
    id_firmy = db.Column(db.Integer, db.ForeignKey('firmy.id_firmy'), nullable=False)
    data_od = db.Column(db.Date, nullable=False)
    data_do = db.Column(db.Date, nullable=False)
    liczba_dni_roboczych = db.Column(db.Integer)  # uzupełniane po zakończeniu Fazy 2
    status = db.Column(db.String(30), default='roboczy')

    # KONTROLA FAZ (1=Inicjacja, 2=Realizacja, 3=Podsumowanie, 4=Zaliczenie/Zakończone)
    faza_procesu = db.Column(db.Integer, default=1, nullable=False)

    # Metadane Porozumienia (Zał. 1)
    nr_porozumienia = db.Column(db.String(50), nullable=True)
    data_porozumienia = db.Column(db.Date, nullable=True)

    # --- FAZA 1: INICJACJA ---
    zal1_zopz = db.Column(db.Boolean, default=False)       # Porozumienie (Zakład)
    zal1_dyrektor = db.Column(db.Boolean, default=False)   # Porozumienie (Uczelnia)
    zal2a_zopz = db.Column(db.Boolean, default=False)      # Harmonogram (Zakład)
    zal2a_student = db.Column(db.Boolean, default=False)   # Harmonogram (Student)
    zal2a_uopz = db.Column(db.Boolean, default=False)      # Harmonogram (Uczelnia)
    # Zał. 3.1 = Karta praktyki STRONA 1 (przed praktyką): skierowanie + potwierdzenia zakładu
    zal31_dyrektor = db.Column(db.Boolean, default=False)         # Skierowanie (Dyrektor)
    zal32_zgloszenie_zopz = db.Column(db.Boolean, default=False)  # Potwierdzenie zgłoszenia studenta (Zakład) — strona 1
    zal32_bhp_zopz = db.Column(db.Boolean, default=False)         # Potwierdzenie szkolenia BHP (Zakład) — strona 1

    # --- FAZA 2: REALIZACJA ---
    dziennik_zatwierdzony = db.Column(db.Boolean, default=False)  # 120 dni wpisane

    # --- FAZA 3: PODSUMOWANIE ---
    # Zał. 3.2 = Karta praktyki STRONA 2 (po praktyce): zaświadczenie + oceny
    zal3_strona2_zopz = db.Column(db.Boolean, default=False)  # Zaświadczenie odbycia + ocena zakładowa (ZOPZ)
    zal3_strona2_uopz = db.Column(db.Boolean, default=False)  # Ocena uczelniana + ocena sprawozdania (UOPZ)
    zal4_zopz = db.Column(db.Boolean, default=False)           # Efekty (Zakład)
    zal4_opinia_uopz = db.Column(db.Text, nullable=True)       # Opinia UOPZ do Zał. 4
    zal4_uopz = db.Column(db.Boolean, default=False)           # Efekty (Uczelnia)
    zal5_student = db.Column(db.Boolean, default=False)        # Kwestionariusz ankiety (Student)
    zal7_student = db.Column(db.Boolean, default=False)        # Sprawozdanie złożone (Student)
    zal7_zopz = db.Column(db.Boolean, default=False)           # Sprawozdanie potwierdzone (Zakład)

    # --- FAZA 4: ZALICZENIE ---
    zal8_dyrektor = db.Column(db.Boolean, default=False)   # Protokół końcowy — Przewodniczący Komisji (Dyrektor)
    zal8_uopz     = db.Column(db.Boolean, default=False)   # Protokół — podpis uczelnianego opiekuna (UOPZ)
    usos_wpisany  = db.Column(db.Boolean, default=False)   # Wpis zaliczenia do USOS (UOPZ)

    student_record = db.relationship('Student', backref=db.backref('formularze', lazy=True))
    firma = db.relationship('Firma', backref=db.backref('formularze', lazy=True))

    def check_and_advance_phase(self):
        if self.faza_procesu == 1:
            if all([self.zal1_zopz, self.zal1_dyrektor, self.zal2a_zopz,
                    self.zal2a_student, self.zal2a_uopz, self.zal31_dyrektor,
                    self.zal32_zgloszenie_zopz, self.zal32_bhp_zopz]):
                self.faza_procesu = 2
        elif self.faza_procesu == 2:
            if self.dziennik_zatwierdzony:
                self.faza_procesu = 3
        elif self.faza_procesu == 3:
            if all([self.zal7_student, self.zal7_zopz,
                    self.zal3_strona2_zopz, self.zal3_strona2_uopz,
                    self.zal4_zopz, self.zal4_uopz,
                    self.zal5_student]):
                self.faza_procesu = 4
