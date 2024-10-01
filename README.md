
# Gesture-Pong
## Ziele
 - [ ] Pong als Spiel programmieren
 - [ ]  Einzelspieler- & Mehrspielermodus
 - [ ] Mithilfe von OpenPose Position von einer Hand einlesen
 - [ ] Mithilfe von OpenPose Position von mehrern Händen einlesen (Einer oder Zwei Personen)
 - [ ] Schnittstelle zwischen Gestik und Pong realisieren

## Vorgehensweise & Technologien
 ### Vorgehensweise
**Generelle Vorgehensweise** (Projektplanung und Setup):
    - Definiere die genauen Anforderungen und Ziele des Projekts.
    - Erstelle ein Repository auf GitHub.
    - Installiere alle notwendigen Tools und Bibliotheken (Python, Pygame, OpenPose).
 **Iterationsplan**
- Grundlegendes Pong-Spiel entwickeln
    - Implementieren des Grundgerüst des Spiels in Pygame.
    - Erstellen der Spiellogik für den Einzelspieler.
- Entwicklung vom OpenPose Modul
    - Installation und konfiguration von OpenPose.
    - Entwickeln eines Moduls, das die Position einer Hand erkennt und auf benutzbare Art wiedergibt.
    - Implementieren einer Kalibrierungsfunktion, um die Gestenerkennung an verschiedene Benutzer anzupassen.
 - Schnittstelle zwischen Gestik und Pong
    - Entwickeln einer Schnittstelle, die die Paddles mithilfe der Handgestik bewegt. 
    - Integration der beiden Module (Pong- und Gestikmodul) 
- Erweiterung auf mehrere Hände und Spieler
    - Modifizieren des Skripts, um die Positionen von mehreren Händen zu erkennen.
    - Anpassen der Spiellogik, um Eingaben von zwei Spielern zu verarbeiten.
- Präsentation
    - Vorbereiten einer Präsentation mit Live Demo der Schnittstelle.
### Technologien
 - Python als programmiersprache
 - Pygame als Gameengine
 - OpenPose als Gestikerkennung
