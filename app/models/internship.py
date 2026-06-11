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

    # KONTROLA FAZ (1=Inicjacja, 2=Realizacja, 3=Podsumowanie, 4=Zaliczenie, 5=Zamknięta)
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
    zal31_dyrektor = db.Column(db.Boolean, default=False)  # Skierowanie (Dyrektor)

    # --- FAZA 2: REALIZACJA ---
    zal32_zopz = db.Column(db.Boolean, default=False)          # Szkolenie BHP (Zakład)
    dziennik_zatwierdzony = db.Column(db.Boolean, default=False)  # 120 dni wpisane

    # --- FAZA 3: PODSUMOWANIE ---
    zal4_zopz = db.Column(db.Boolean, default=False)       # Efekty (Zakład)
    zal4_uopz = db.Column(db.Boolean, default=False)       # Efekty (Uczelnia)
    zal7_student = db.Column(db.Boolean, default=False)    # Sprawozdanie (Student)

    # --- FAZA 4: ZALICZENIE ---
    zal8_dyrektor = db.Column(db.Boolean, default=False)   # Protokół końcowy (Dyrektor)

    student_record = db.relationship('Student', backref=db.backref('formularze', lazy=True))
    firma = db.relationship('Firma', backref=db.backref('formularze', lazy=True))

    def check_and_advance_phase(self):
        if self.faza_procesu == 1:
            if all([self.zal1_zopz, self.zal1_dyrektor, self.zal2a_zopz,
                    self.zal2a_student, self.zal2a_uopz, self.zal31_dyrektor]):
                self.faza_procesu = 2
        elif self.faza_procesu == 2:
            if self.zal32_zopz and self.dziennik_zatwierdzony:
                self.faza_procesu = 3
        elif self.faza_procesu == 3:
            if all([self.zal7_student, self.zal4_zopz, self.zal4_uopz]):
                self.faza_procesu = 4
        elif self.faza_procesu == 4:
            if self.zal8_dyrektor:
                self.faza_procesu = 5
