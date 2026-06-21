FROM python:3.12-slim

WORKDIR /app

# Czcionki z polskimi znakami (DejaVu). Kontener Linux nie ma Arial/Segoe z Windows,
# bez nich xhtml2pdf renderuje polskie litery jako puste kwadraty.
RUN apt-get update \
    && apt-get install -y --no-install-recommends fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run.py"]
