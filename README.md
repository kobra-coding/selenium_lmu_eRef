# selenium_lmu_eRef

Bei der folgenden Anwendung handelt es sich um einen Webscraper, der Thieme-Bücher aus der Online-Bibliothek der LMU herunterladen kann. Das Programm lädt die einzelnen PDF-Dateien herunter und fügt sie zum Schluss zu einer einzelnen Datei zusammen.

## Benutzung

Lade dir die aktuelle Version herunter.

Du benötigst deine LMU-Kennung und das dazugehörige Passwort.

Du benötigst die URL zum Buch, das du herunterladen möchtest. Z.B. "https://eref-thieme-de.emedien.ub.uni-muenchen.de/ebooks/cs_12606593#/ebook_cs_12606593_SL74462153"

pyinstaller --noconfirm --onedir --windowed --icon "C:/Users/kbram/dev/selenium_lmu_eRef/fav.ico" --add-data "C:/Users/kbram/dev/selenium_lmu_eRef/driver;driver/" --add-data "C:/Users/kbram/dev/selenium_lmu_eRef/fav.ico;." "C:/Users/kbram/dev/selenium_lmu_eRef/app.py"
