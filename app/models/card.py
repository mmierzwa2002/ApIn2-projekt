from app import db

class KartaPraktyki(db.Model):
    __tablename__ = 'karty_praktyki'
    id_karty = db.Column(db.Integer, primary_key=True)
    id_formularza = db.Column(db.Integer, db.ForeignKey('formularze_praktyk.id_formularza'), unique=True, nullable=False)
    data_szkolenia_bhp = db.Column(db.Date)
    ocena_zakladowa = db.Column(db.Integer)    # (legacy, nieużywane)
    ocena_uczelniana = db.Column(db.Integer)   # (legacy, nieużywane)
    data_podpisu = db.Column(db.Date)

    # --- Zał. 3.2 = Karta praktyki STRONA 2 (po praktyce) ---
    uwagi_odbycie = db.Column(db.Text)              # Zaświadczenie odbycia — uwagi
    ocena_zopz_param = db.Column(db.String(4))      # Ocena ZOPZ parametryczna (2–5)
    ocena_zopz_opis = db.Column(db.Text)            # Ocena ZOPZ opisowa
    ocena_uopz_param = db.Column(db.String(4))      # Ocena UOPZ parametryczna (2–5)
    ocena_uopz_opis = db.Column(db.Text)            # Ocena UOPZ opisowa
    ocena_sprawozdania = db.Column(db.String(4))    # Ocena sprawozdania (UOPZ, 2–5)

    formularz = db.relationship('Internship', backref=db.backref('karta', uselist=False))
