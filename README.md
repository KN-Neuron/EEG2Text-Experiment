# Experiment

BrainAccess SDK needs to be installed manually and is not included in Poetry dependencies.

For runtime config, modify constants in _main.py_:

- `DO_USE_DEBUG_MODE` - if True, makes the experiment quicker and uses windowed Pygame
- `DO_USE_MOCK_HEADSET` - if True, doesn't connect to actual BrainAccess headset
- `BRAINACCESS_CAP_NAME` - the name of the BrainAccess cap, can be checked in BrainAccess Board

For advanced config, modify constants in _src/constants.py_.

1. Go to /experiment
2. Create venv
3. After creating and activating venv do:

```
pip install poetry
poetry lock
poetry install
poetry run python main.py
```


Here is the content of the uploaded file converted into a structured Markdown format.

Here is the content of the file converted into a structured Markdown checklist.

### **Protokół badania - Checklista**

#### **1. Do wzięcia (Lista wyposażenia)**
* Laptop + ładowarka
* Sparowany BrainAccess MIDI przez Bluetooth
* Zainstalowany BrainAccess Board 1.1.3
* Czepek BrainAccess
* Zgody (wypełniony UUID i podpis osoby badającej)
* Dowód/legitymacja do odebrania sali
* Wydrukowana checklista
* Kartki + długopis
* Rękawiczki jednorazowe
* Nagrody materialne
* Woda + jedzenie + krzyżówki

---

#### **2. Przygotowanie do badania**

**Ustawienie stanowiska:**
* Ustawić stolik tak, aby widzieć, co dzieje się na ekranie.
* Podłączyć laptop do zasilania.
* Włączyć Bluetooth i sprawdzić, czy MIDI jest sparowane.
* Odpalić BrainAccess Board.

**Opisanie badanemu celu badania:**
* Wyjaśnić: „Badanie ma na celu analizę sposobu przetwarzania zdań i myślenia przy pomocy fal mózgowych”.
* Poinformować o trybach czytania/słuchania:
    * **Normal:** Przeczytanie zdania w miarę szybko, każde słowo ma być wyraźnie przeczytane.
    * **Sentiment:** Mniej skupienia na każdym słowie, bardziej na znaczeniu i wizualizacji sensu zdania.
    * **Słuchanie:** Badany śledzi tekst wzrokiem i słucha go jednocześnie, koncentrując się na każdym słowie w głowie.
* Bloki są mieszane, niekoniecznie w kolejności.
* Po losowych zdaniach pojawi się pytanie o treść.
* Jeśli badany odpowie poprawnie na wszystkie pytania, otrzyma cenne nagrody rzeczowe.

**Przygotowanie uczestnika i danych:**
* Uzupełnienie zgody przez badanego.
* Poproszenie o odłożenie, wyciszenie i/lub wyłączenie telefonów, smartwatchy, słuchawek, aparatów słuchowych i rozruszników serca.
* Wpisanie ID ze zgody do aplikacji.
* Upewnienie się, że w `src/config.py` zmienne `DEBUG` i `DEBUG WITHOUT HEADSET` są ustawione na **False**.
* **Wprowadzenie danych osobowych:**
    * Pełne imię.
    * Data urodzenia w formacie "10 września" (nie "wrzesień").
    * Płeć "m" lub "k" (z małej litery).

**Zakładanie sprzętu:**
1.  Poproszenie badanego o zdjęcie okularów.
2.  Założenie czepka badanemu.
3.  Poproszenie badanego o ponowne założenie okularów.

---

#### **3. Połączenie czepka z BrainAccess Board**
1.  Nacisnąć "Scan for Devices".
2.  Wybrać czepek z listy.
3.  Nacisnąć "Connect".
4.  Sprawdzić port po prawej stronie (np. "COM7") i wpisać go do zmiennej `PORT` w pliku `src/config.py`.
5.  Nacisnąć ikonkę z wykresem, aby otworzyć aplikację i przetestować siłę sygnału w sekcji **Signal** (kropki przy elektrodach).
6.  Nacisnąć ikonkę krzyżyka, aby rozłączyć się z czepkiem w BrainAccess Board (przed uruchomieniem właściwego skryptu).

---

#### **4. Procedura badania**

**Część 1: Część próbna**
* Pierwsze 9 prób nie jest liczonych do badania (trening).
* Badany czyta kilka zdań, aby określić średnią prędkość czytania.
* Obserwować wykresy w aplikacji – sprawdzić, czy czyta zbyt szybko lub wolno (skorygować prędkość i poprosić badanego o zmianę tempa, jeśli trzeba).
* Badany otrzyma feedback, jeśli odpowie źle.
* Po próbach treningowych następuje 10-sekundowa przerwa przed właściwym badaniem.
* Zapytać badanego, czy rozumie zasady.
* Jeśli jest gotowy, przechodzi dalej naciskając **prawy Shift**.
* (Opcjonalnie) Można ponownie wyświetlić instrukcje, jeśli badany chce sobie przypomnieć.

**Część 2: Bloki właściwe**
* Bloki obejmują tryby:
    1.  **Normal:** Wyraźne czytanie każdego słowa.
    2.  **Sentiment:** Skupienie na znaczeniu/wizualizacji.
    3.  **Słuchanie:** Śledzenie tekstu + słuchanie.
* Maksymalna i minimalna prędkość czytania jest ustalona wcześniej.

---

#### **5. Po zakończeniu bloków**
* Przekazanie nagrody rzeczowej (jeśli 100% poprawnych odpowiedzi).
* **Zdjęcie sprzętu:**
    1.  Poproszenie o zdjęcie okularów.
    2.  Zdjęcie czepka.
    3.  Poproszenie o założenie okularów.
* Sprawdzenie formalności: czy zgoda jest podpisana na obu stronach i czy badany zabrał wszystkie rzeczy (telefon, zegarek itp.).
* Pożegnanie badanego.
* Przemycie elektrod.
* **Archiwizacja danych:** Przerzucenie wygenerowanych plików (folder `eeg_data`, nazwa zgodna z UUID) na Google Drive:
    > koła > projekty > eeg2text > dane z badań

Would you like me to create a simple Python script to help validate the config file settings mentioned in the protocol?
