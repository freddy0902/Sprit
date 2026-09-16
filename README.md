# Spritpreise – Esso Dietzenbach & 12. Mann Bielefeld

Statische Seite auf GitHub Pages, die alle ~30 Minuten per GitHub Actions
den aktuellen Super-E5-Preis über die offizielle [Tankerkönig-API](https://creativecommons.tankerkoenig.de/)
(MTS-K-Daten des Bundeskartellamts) abruft und als JSON ablegt. Die Seite selbst
lädt nur diese JSON-Datei – kein API-Key im Browser, kein Live-Call vom iPhone aus nötig.

## Einmaliges Setup

1. **Kostenlosen API-Key holen**
   Auf https://creativecommons.tankerkoenig.de/#register registrieren (Name + E-Mail).
   Der Key kommt per Mail. Falls die Registrierung "wegen Wartungsarbeiten" gerade
   nicht möglich ist: einfach später nochmal versuchen.

2. **Repo erstellen**
   Neues **öffentliches** GitHub-Repository anlegen (für kostenloses GitHub Pages nötig)
   und alle Dateien aus diesem Ordner hochladen (Drag & Drop über "Add file → Upload files"
   reicht, kein Git-Kenntnisse nötig – oder per `git push`, falls gewünscht).

3. **API-Key als Secret hinterlegen**
   Repo → **Settings → Secrets and variables → Actions → New repository secret**
   Name: `TANKERKOENIG_API_KEY`
   Wert: dein Key von Schritt 1

4. **GitHub Pages aktivieren**
   Repo → **Settings → Pages** → Source: **Deploy from branch** → Branch **main**, Ordner **/ (root)** → Save.
   Die Seite ist danach unter `https://DEIN-USERNAME.github.io/DEIN-REPO/` erreichbar.

5. **Workflow einmal manuell anstoßen**
   Repo → **Actions** → "Spritpreise aktualisieren" → **Run workflow**.
   Danach sollte `data/prices.json` echte Preise enthalten (im Actions-Log sichtbar).
   Ab jetzt läuft der Workflow automatisch alle 30 Minuten.

6. **Auf dem iPhone zum Home-Bildschirm hinzufügen**
   Die Pages-URL in **Safari** öffnen → Teilen-Symbol → **"Zum Home-Bildschirm"**.
   Danach öffnet ein Tap auf das Icon direkt die zuletzt gespeicherten Preise – ganz
   ohne Login, auch offline nutzbar (zeigt dann den letzten bekannten Stand).

## Anpassen

- **Anderes Intervall:** Cron-Ausdruck in `.github/workflows/update-prices.yml` ändern.
  Tankerkönig bittet automatisierte Systeme, nicht öfter als alle 5 Minuten abzufragen –
  30 Minuten ist ein guter Kompromiss zwischen Aktualität und Höflichkeit gegenüber dem
  kostenlosen Dienst.
- **Andere/weitere Tankstellen:** `STATIONS`-Liste in `scripts/fetch_prices.py` erweitern
  (Adresse + ungefähre Koordinaten zum Suchen reichen, die genaue UUID wird automatisch
  ermittelt) und passende `<div class="sign">`-Blöcke in `index.html` ergänzen.
- **Diesel/E10 mit anzeigen:** `prices.php` liefert `diesel` und `e10` bereits mit,
  `fetch_prices.py` müsste sie nur zusätzlich in `result` übernehmen.

## Lizenz der Preisdaten

Die Preisdaten stehen unter [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.de)
und stammen von der [Tankerkönig API](https://www.tankerkoenig.de) – das ist bereits
im Footer der Seite verlinkt (Namensnennung ist laut Tankerkönig-Nutzungsbedingungen Pflicht).
