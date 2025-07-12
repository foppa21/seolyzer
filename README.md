# SEOlyzer - SEO Command Line Tool

Ein leistungsstarkes CLI-Tool zur SEO-Analyse von Webseiten, das verschiedene SEO-Metriken und -Indikatoren überprüft.

## Voraussetzungen

- Python 3.11 oder 3.12 (empfohlen, Python 3.13 wird nicht für lxml empfohlen)
- Git (optional, für das Klonen des Repos)

## Installation

1. Repository klonen (oder ZIP entpacken):
   ```bash
   git clone https://github.com/yourusername/seolyzer.git
   cd seolyzer
   ```

2. Virtuelle Umgebung erstellen (empfohlen):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Unter Windows: venv\Scripts\activate
   ```

3. Abhängigkeiten installieren:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

## Nutzung

### Einzelne URL analysieren

```bash
python3 seolyzer.py https://www.example.com --output report.csv
```

### Mehrere URLs analysieren

1. Lege eine Datei `urls.txt` an, jede Zeile eine URL (mit http/https):
   ```
   https://www.example.com
   https://www.example.org
   ...
   ```
2. Dann:
   ```bash
   python3 seolyzer.py urls.txt --output report.csv
   ```

## Ausgabe

- Die Ergebnisse werden als CSV-Datei gespeichert.
- Jede Zeile entspricht einer analysierten URL.
- Die wichtigsten SEO-Metriken werden als Spalten ausgegeben (siehe Beispiel unten).

## Beispiel für CSV-Spalten

- URL
- Title Tag inhalt
- Description Tag inhalt
- H1 Header anzahl
- Inhalt H1 Header
- H2 Header anzahl
- Inhalt H2 Header
- Anzahl Bilder
- Ladezeit
- Größe
- Viewport-Tag
- Canonical
- hreflang
- Noindex

## Hinweise

- Für große URL-Listen kann die Analyse einige Zeit dauern.
- Das Tool benötigt Internetzugang für die Analyse der Seiten.
- Die Datei `urls.txt` muss im selben Verzeichnis wie das Script liegen oder mit absolutem Pfad angegeben werden.

## Lizenz

MIT License

## Beitragen

Beiträge sind willkommen! Bitte lesen Sie unsere Contributing Guidelines für Details.
