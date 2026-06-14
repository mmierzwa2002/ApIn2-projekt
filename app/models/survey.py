from app import db

PYTANIA_ZAL5 = [
    (1,  'Poznałam/poznałem zasady funkcjonowania instytucji, w której odbywałam/odbywałem praktyki zawodowe.'),
    (2,  'Poznałam/poznałem strukturę oraz regulamin organizacyjny instytucji, w której odbywałam/odbywałem praktyki zawodowe.'),
    (3,  'Praktyki zawodowe umożliwiły mi pełną realizację ramowego programu praktyk zawodowych przewidzianego w ramach mojego kierunku studiów.'),
    (4,  'Podczas praktyk zawodowych zwracano uwagę na przestrzeganie zasad etyki i tajemnicy zawodowej.'),
    (5,  'Podczas praktyk miałam/miałem możliwość praktycznego zastosowania wiedzy teoretycznej zdobytej na zajęciach.'),
    (6,  'Praktyki zawodowe przyczyniły się do pogłębienia mojej wiedzy i umiejętności zdobytych w trakcie studiów.'),
    (7,  'Mogłem liczyć na wsparcie merytoryczne Opiekuna zakładowego praktyk.'),
    (8,  'Mogłem liczyć na wsparcie merytoryczne Opiekuna uczelnianego praktyk.'),
    (9,  'Opiekun zakładowy odpowiedzialny za praktyki zawodowe w miejscu ich odbywania potrafił prawidłowo zorganizować ich przebieg.'),
    (10, 'Podczas praktyk zawodowych miałam/miałem możliwość pozyskiwania materiałów niezbędnych do przygotowania mojej pracy dyplomowej.'),
    (11, 'Praktyki zawodowe rozwinęły moje umiejętności skutecznego komunikowania się w sytuacjach zawodowych i pracy w zespole.'),
    (12, 'Praktyki zawodowe nauczyły mnie samodzielności i odpowiedzialności podczas wykonywania pracy.'),
    (13, 'Liczba godzin realizowana w ramach praktyk zawodowych jest wystarczająca.'),
    (14, 'Czy po zakończeniu praktyki zawodowej chciałaby/chciałby Pani/Pan współpracować z instytucją, w której Pani/Pan zrealizowała/zrealizował praktykę?'),
]

ODPOWIEDZI = ['zd_tak', 'rk_tak', 'trudno', 'rk_nie', 'zd_nie']
ODPOWIEDZI_LABELS = {
    'zd_tak': 'zdecydowanie tak',
    'rk_tak': 'raczej tak',
    'trudno': 'trudno powiedzieć',
    'rk_nie': 'raczej nie',
    'zd_nie': 'zdecydowanie nie',
}


class Ankieta(db.Model):
    __tablename__ = 'ankiety'
    id = db.Column(db.Integer, primary_key=True)
    id_formularza = db.Column(db.Integer, db.ForeignKey('formularze_praktyk.id_formularza'),
                              unique=True, nullable=False)
    q1  = db.Column(db.String(10))
    q2  = db.Column(db.String(10))
    q3  = db.Column(db.String(10))
    q4  = db.Column(db.String(10))
    q5  = db.Column(db.String(10))
    q6  = db.Column(db.String(10))
    q7  = db.Column(db.String(10))
    q8  = db.Column(db.String(10))
    q9  = db.Column(db.String(10))
    q10 = db.Column(db.String(10))
    q11 = db.Column(db.String(10))
    q12 = db.Column(db.String(10))
    q13 = db.Column(db.String(10))
    q14 = db.Column(db.String(10))
    uwagi = db.Column(db.Text)
    rok_akademicki = db.Column(db.String(20))
    forma_studiow  = db.Column(db.String(20))
    semestr        = db.Column(db.String(10))
    liczba_godzin  = db.Column(db.Integer)
