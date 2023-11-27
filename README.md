# Datev-AI-Datenautomatisierung

## Überblick

Datev-AI-Datenautomatisierung ist ein automatisiertes System zur Verarbeitung und Umbenennung von DATEV-Dokumentbildern unter Verwendung künstlicher Intelligenz. Das System liest JPG-Dateien, extrahiert relevante Informationen mit der OpenAI GPT-4 Vision API und benennt die Dateien anhand dieser Informationen um.

## Funktionsweise

- Liest JPG-Dateien aus einem vorgegebenen Verzeichnis.
- Konvertiert diese in Base64-Format und sendet sie an die OpenAI GPT-4 Vision API.
- Die API extrahiert Informationen wie Datum, Rechnungstyp und Firmennamen.
- Dateien werden entsprechend diesen Informationen umbenannt.

## Installation

Installieren Sie die erforderlichen Pakete mit:

```bash
pip install -r requirements.txt
```

## Konfiguration

- Stellen Sie sicher, dass Sie Ihren OpenAI API-Schlüssel im Skript angeben.
- Konfigurieren Sie den Pfad zu den JPG-Dateien.

## Nutzung

Führen Sie das Skript aus, um den Automatisierungsprozess zu starten. Überprüfen Sie die umbenannten Dateien im Zielverzeichnis.

## Lizenz

Dieses Projekt ist unter der MIT Lizenz lizenziert.