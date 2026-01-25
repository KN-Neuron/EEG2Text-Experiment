# Experiment

BrainAccess SDK needs to be installed manually and is not included in Poetry dependencies.

For runtime config, modify constants in _main.py_:

- `DO_USE_DEBUG_MODE` - if True, makes the experiment quicker and uses windowed Pygame
- `DO_USE_MOCK_HEADSET` - if True, doesn't connect to actual BrainAccess headset
- `BRAINACCESS_CAP_NAME` - the name of the BrainAccess cap, can be checked in BrainAccess Board

For advanced config, modify constants in _src/constants.py_.

1. Create venv
2. After creating and activating venv do:

```
pip install -r requirements.txt
pip install BrainAccessSDK-linux/python_api #if you're on linux
# W terminalu przed uruchomieniem:
export LD_LIBRARY_PATH=/ścieżka/do/EEG2Text-Experiment/BrainAccessSDK-linux:$LD_LIBRARY_PATH
python3 main.py
```


Here is the content of the uploaded file converted into a structured Markdown format.

Here is the content of the file converted into a structured Markdown checklist.

### **Protokół badania - Checklista**

#### **0. Osoba badana**
* wypoczęta
* nie pod wpływem alkoholu i używek
* najlepiej jeśli nie piła kawy i napojów z wysoką zawartością kofeiny
* bez lakieru na włosach
* bez zbyt gęstych włosów (np afro)
* 

#### **1. Do wzięcia (Lista wyposażenia)**
* Laptop + ładowarka
* Sparowany BrainAccess MIDI przez Bluetooth
* Zainstalowany BrainAccess Board 2.5.0 https://drive.google.com/drive/u/1/folders/1XXSHa4FeGyfv57Ik3Kcwh1iO5W10GVt8
* Czepek BrainAccess 32 kanały
* Zgody (wypełniony UUID i podpis osoby badającej)
* Dowód/legitymacja do odebrania sali
* Wydrukowana checklista
* Kartki + długopis
* Rękawiczki jednorazowe
* Nagrody materialne
* Woda + jedzenie + krzyżówki
* Waciki (do wyczyszczenia elektrod przed badaniem)

---

#### **2. Przygotowanie do badania**

**Ustawienie stanowiska:**
* Ustawić stolik tak, aby widzieć, co dzieje się na ekranie.
* Podłączyć laptop do zasilania.
* Włączyć Bluetooth i sprawdzić, czy MIDI jest sparowane.
* Odpalić BrainAccess Board.
* Po upewnieniu się, że signal quality jest OK to rozłączamy się z boardem i włączamy aplikację.

**Opisanie badanemu celu badania:**
* Wyjaśnić: „Badanie ma na celu analizę sposobu przetwarzania zdań i myślenia przy pomocy fal mózgowych. Przewidujemy nagrodę od pewnego progu poprawnego wykonywania zadania." Nie musimy precyzować co to jest i jakie metryki mierzymy, ale musimy powiedzieć, że to sprawdzamy w czasie rzeczywistym.
* Poinformować o blokach czytania/słuchania:
    * **Normal:** Przeczytanie zdania naturalnym tempem słowo w słowo tak każde słowo było wyraźnie przeczytane.
    * **Sentiment:** Mniej skupienia na każdym słowie, bardziej na znaczeniu i zilustorowanie w myślach tego co przedstawia zdanie. Chcemy by w miarę możliwości ilustrował czytając zdanie. Mniej skupienia na słowach, a bardziej na to o czym czyta. nie chcemy by wizualizował obrazek, ale podczas czytania myślał nad sensem tego co czyta.
    * **Słuchanie + Czytanie:** Badany śledzi tekst wzrokiem i słucha go jednocześnie, koncentrując się na każdym słowie w głowie. To w zasadzie powtórka pierwszego bloku, ale z audio przeczytanych zdań. Tempo audio jest dostosowane do tego jak szybko czytaliśmy w normal readingu.
* Bloki są mieszane, niekoniecznie w kolejności.
* Po losowych zdaniach pojawi się pytanie o treść.
* Jeśli badany odpowie poprawnie na wszystkie pytania.

**Przygotowanie uczestnika i danych:**
* Uzupełnienie zgody przez badanego.
* Poproszenie o odłożenie, wyciszenie i/lub wyłączenie telefonów, smartwatchy, słuchawek, aparatów słuchowych.
* Wpisanie ID ze zgody do aplikacji.
* Upewnienie się, że w `src/config.py` zmienne `DEBUG` i `DEBUG WITHOUT HEADSET` są ustawione na **False**.
* **Wprowadzenie danych osobowych (wykonuje badacz):**
    * Pełne imię.
    * Płeć "m" lub "k" (z małej litery).
    * Wiek
    * Prawo i leworęczność (powinniśmy się skupić tylko na praworęcznych i w najepszym wypadku nie badać leworęcznych)

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
