from app import db

OCENY_PROTOKOL = ['2', '3', '3.5', '4', '4.5', '5']


def _round_grade(val: float) -> str:
    if val < 2.75:  return '2'
    if val < 3.25:  return '3'
    if val < 3.75:  return '3.5'
    if val < 4.25:  return '4'
    if val < 4.75:  return '4.5'
    return '5'


class ProtokolZaliczenia(db.Model):
    __tablename__ = 'protokoly_zaliczenia'

    id            = db.Column(db.Integer, primary_key=True)
    id_formularza = db.Column(db.Integer,
                               db.ForeignKey('formularze_praktyk.id_formularza'),
                               unique=True, nullable=False)
    data_zaliczenia = db.Column(db.Date, nullable=True)

    # Skład komisji (wolny tekst – nie są użytkownikami systemu)
    czlonek_1 = db.Column(db.String(200))  # Przewodniczący
    czlonek_2 = db.Column(db.String(200))  # UOPZ
    czlonek_3 = db.Column(db.String(200))
    czlonek_4 = db.Column(db.String(200))

    # Pytania / mini-zadania + oceny cząstkowe
    pytanie_1 = db.Column(db.Text)
    pytanie_2 = db.Column(db.Text)
    pytanie_3 = db.Column(db.Text)
    ocena_p1  = db.Column(db.String(5))
    ocena_p2  = db.Column(db.String(5))
    ocena_p3  = db.Column(db.String(5))

    # Oceny zewnętrzne
    ocena_s = db.Column(db.String(5))  # za sprawozdanie (podaje Dyrektor/UOPZ na egzaminie)

    # Oceny wyliczone (przechowywane po obliczeniu)
    ocena_e = db.Column(db.String(6))  # E = avg(p1,p2,p3)
    ocena_k = db.Column(db.String(6))  # K = 0.4E + 0.1S + 0.2U + 0.3Z
    ocena_finalna = db.Column(db.String(5))  # K zaokrąglone do skali
