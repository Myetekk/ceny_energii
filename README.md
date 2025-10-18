[Open Documentation (PDF)](./dokumentacja.pdf)



# Program pobierający ceny energii rynku dnia następnego

## Wstęp

```
Program pobierający ceny energii rynku dnia następnego z dwóch źródeł: “entsoe
Transparency Platform” oraz “Towarowa Giełda Energii”.
Aplikacja operuje na danych dla aktualnego dnia, oraz dnia następnego, gdy jego
dane zostaną już udostępnione.
Pobrane dane są wyświetlane w oknie aplikacji, oraz wysyłane przy pomocy
protokołu ModbusTCP.
```

## Źródła danych

```
● entsoe Transparency Platform (ENTSOE) - API udostępniane przez Transparency
Platform
● Towarowa Giełda Energii (TGE) - dane zescrapowane z TGE - Rynek Dnia
Następnego
```

## Instalacja Python

```
Projekt napisany jest w języku Python. Aby móc go obsługiwać (przez pliki .py)
należy zainstalować Python, według następujących kroków:
● wejść na strone https://www.python.org/downloads/ oraz pobrać najonwszą wersję
(kliknąć żółty przycisk “Download Python [najnowsza wersja])
● uruchomić instalator - otworzyć pobrany plik .exe
● upewnić się, że pole "Add Python to PATH" jest zaznaczone (dół okna)
● kliknąć "Install Now" i postępować zgodnie z instrukcjami instalatora

Po zakończeniu instalacji zweryfikować czy Python został poprawnie zainstalowany:
● otworzyć wiersz poleceń
● wpisać “python --version” lub “python3 --version”
Jeśli zwrócona informacja nie jest błędem oznacza, że Pyhon został zainstalowany
pomyślnie.

Czasami dodatkowo trzeba zrestartować urządzenie
```

## Instalacja pip

```
Program korzysta z szeregu bibliotek, które należy zainstalować przy pomocy ‘pip’.
W większości przypadków pip jest instalowany razem z Python-em. Aby sprawdzić
czy pip jest zainstalowany na naszym urządzeniu należy otworzyć wiersz poleceń i
wpisać “pip --version”. Jeśli zwrócona wartość nie jest błędem oznacza, że pip został
już wcześniej zainstalowany. W przeciwnym wypadku należy:
● otworzyć wiersz poleceń
● wpisać “python -m ensurepip --upgrade”
● ponownie zweryfikować obecność pip na urządzeniu przez wpisanie “pip --version” w
wierszu poleceń
```

## Wykorzystane biblioteki

```
Program wykorzystuje następujące biblioteki:
● tk
● entsoe-py
● pyModbusTCP
● matplotlib
● datetime
● pandas
● tkcalendar
Aby je zainstalować należy dla każdej z nich w wierszu poleceń użyć komendy “pip
install [nazwa biblioteki]”
```

## Struktura plików

```
● “main.exe” - główny plik programu
● “outputs” - folder zawierający wszystkie pliki stworzone przez program. Jeśli nie
istnieje tworzy się obok pliku “main.exe”. Zawiera:
     ○ “settings.json”
     ○ “errors.txt”
     ○ “dataBase.db” - baza danych zawierająca wszystkie dane pobrane przez
          program. Dane są podzielone na tabele według dnia, z którego pochodzą
     ○ “data.json” - dane aktualne w formacie .json
     ○ “data.html” - dane aktualne w formacie .html
     ○ “data.csv” - dane aktualne w formacie .csv
     ○ “rrrr-mm-dd__rrrr-mm-dd” - folder zawierający dane hurtowe dla zadanego
          przedziału czasu (np. “2024-09-22__2024-09-28”). Składa się z:
          ■ “rrrr-mm-dd__rrrr-mm-dd.json” (np. “2024-09-22__2024-09-28.json”)
          ■ “rrrr-mm-dd__rrrr-mm-dd.csv” (np. “2024-09-22__2024-09-28.csv”)
```

## Instrukcja obsługi

```
Po uruchomieniu programu zobaczymy okno, którego zawartość możemy podzielić
na trzy części: dane w formie tabeli, dane w formie wykresu i ustawienia programu.
```
● część 1 - dane w formie tabeli
```
Przedstawia dane z części 1 w formie graficznej. Wyświetlanymi danymi można
zarządzać poprzez checkboxy znajdujące się w wierszu tytułowym w części 1.
```
● część 2  -  dane w formie wykresu
```
Przedstawia dane z części 1 w formie graficznej. Wyświetlanymi danymi można
zarządzać poprzez checkboxy znajdujące się w wierszu tytułowym w części 1.
```
● część 3 - ustawienia programu
```
Ta część może zostać podzielona na kolejne 3 części: ręczne zapisywanie danych,
dane hurtowe, ustawienia działania programu

**1. ręczne zapisywanie danych**
Pozwala zapisywać dane z danego momentu w formacie JSON, HTML, CSV,
oraz w bazie danych.
**2.  dane hurtowe**
Otwiera nowe okno dające możliwość przeglądania danych w formie
hurtowej. Opisane szerzej w części 4.
**3. ustawienia**
Program pozwala na modyfikację następujących wartości:
● częstotliwość aktualizowania danych.
● waluta, w której wyświetlane, zapisywane i wysyłane są dane.
● fixing, z którego pochodzą dane. Dotyczy TGE.
● źródło danych, z którego pochodzą dane (dotyczy danych wysyłanych
przez Modbus).
```
● część 4 - dane hurtowe
```
Okno, w którym wyświetlane są dane dla zadanego przedziału czasu. Tak jak w
części 3 można wybrać walutę i fixing TGE, oraz zapisać dane do plików JSON lub
CSV.
```

## Jak uzyskać dostęp do API Transparency Platform

```
Aby uzyskać dostęp do API udostępnianego przez Transparency Platform należy:
- założyć konto na stronie ENTSOE-E
- wysłać maila w języku angielskim o tytule “Restful API access” na adres
transparency@entsoe.eu z prośbą o przyznanie dostępu do API, oraz adresem email, na
który zostało założone konto
- po przyznaniu dostępu można przejść do ustawień konta, gdzie powinien być już
widoczny element “Web Api Security Token”, w którym można wygenerować token.
Dokument zawierający m.in. instrukcje uzyskania dostępu do API - dokument
Instrukcja korzystania z API - instrukcja
```

## Znaczenie danych w Modbus według indeksów

```
- dane dotyczące czasu: 0 - rok, 1 - miesiąc, 2 - dzień, 3 - godzina, 4 - minuta, 5 -
sekunda
- 6 - sygnał życia
- kurs euro: 7 - część całkowita, 8 - część dziesiętna
- dane z dnia dzisiejszego: 10 - dla godzin 00:00-01:00, 11 - dla godzin 01:00-02:00 …
33 - dla godzin 23:00-00:00, 34 - dataok (określenie czy przesyłane dane są
poprawne), 35 - wartość minimalna z dnia dzisiejszego, 36 - wartość maksymalna z
dnia dzisiejszego
- dane z dnia następnego: 40 - dla godzin 00:00-01:00, 41 - dla godzin 01:00-02:00 …
63 - dla godzin 23:00-00:00, 64 - dataok (określenie czy przesyłane dane są
poprawne), 65 - wartość minimalna z dnia następnego, 66 - wartość maksymalna z
dnia następnego
- ustawienia aplikacji: 121 - waluta danych (1-PLN / 2-EUR), 122 - fixing tge (1-fixing 1
/ 2-fixing 2), 123 - źródło danych (1-entsoe / 2-tge), 124 - częstotliwość pobierania
danych (w sekundach)
```

## Sposób zapisu danych w plikach

```
Wszystkie pliki zapisują się w folderze “outputs”, który tworzy się obok pliku “.exe”.
- JSON
- HTML
- CSV
- Baza danych
```

## Plik z ustawieniami

```
Ustawienia programu zapisują się w pliku “settings.json” w folderze “outputs”, gdzie
● “currency” - waluta, w której wyświetlane, zapisywane i wysyłane są dane.
● “fixing” - fixing, z którego pochodzą dane. Dotyczy TGE.
● “data_source” - źródło danych, z którego pochodzą dane (dotyczy danych
wysyłanych przez Modbus).
● “updateTime” - częstotliwość aktualizowania danych.
● “entsoeKey” - klucz dostępu do API Transparency Platform. Instrukcja jak go uzyskać
została opisana w punkcie “Jak uzyskać dostęp do API Transparency Platform”.
```

## Opis klas i funkcji według plików

```
**1. main.py**
Tworzy i zarządza głównym oknem aplikacji.
Zawiera jedną klasę “EnergyPrices”, która składa się z funkcji:
● “main” - tworzy okno, ładuje ustawienia, pobiera dane, przygotowuje do
transmisji danych przez modbus.
● “increaseInteger” - co sekundę zmienia jedną z liczb w modbusie w celu
wykrycia gdy program się zawiesi.
● “sendToModbus” - wysyła dane przy pomocy protokołu ModbusTCP.
● “checkSettingsChange” - stale monitoruje czy ktoś próbuje zmienić
ustawienia programu poprzez Modbus.
● “getDifference” - oblicza różnice między wartościami pobranymi z entsoe, a
tymi z tge.
● “changeCurrency” - zmienia walutę, w której podawane są dane.
● “changeFixing” - zmienia fixing, w którym podawane są dane (dotyczy tge).
● “reloadElements” - przeładowuje elementy interfejsu na te zapisane w
pamięci.
● “updateGraph” - przeładowuje dane prezentowane na wykresie.
● “updateTime_onChange” - aktualizuje regularność aktualizacji, jednocześnie
zerując czas od poprzedniej aktualizacji.
● “updateData” - pobiera nowe dane i wykonuje wszystkie konieczne
aktualizacje w interfejsie.
● “createInterface” - tworzy cały interfejs: tabelkę z danymi, jej granice i
podpisy, przyciski do exportu danych, przycisk otwierający okno z danymi w
formie hurtowej, elementy zarządzające czasem aktualizacji, walutą, fixingiem
i źródłem danych.

**2. windowTimeInterval.py**
Klasy:
● “EnergyPrices_timeInterval” - klasa tworząca i zarządzająca oknem z danymi
w formie hurtowej. Funkcje:
    ○ “loadHeader” - tworzy ‘nagłówek’ (po lewej stronie okna) zawierający
    zarządzanie przedziałem czasu, walutą, fixingiem, oraz przyciski
    pobierania danych.
    ○ “reloadElements” - przeładowuje elementy interfejsu na te zapisane w
    pamięci.
    ○ “getData” - pobiera dane dla wybranego przedziału czasu.
    ○ “loadOneDay” - obrazuje w interfejsie dane z jednego dnia.
    ○ “createInterface” - tworzy całe okno z danymi w formie hurtowej.
    ○ “changeCurrency” - zmienia walutę danych według kursu dla danego
    dnia
    ○ “changeFixing” - zmienia fixing dla danych z tge
    ○ “exportToCSV” - tworzy folder i plik .csv (lub nadpisuje istniejący), oraz
    zapisuje w nim dane dla wybranego przedziału czasu.
    ○ “exportToJSON” - tworzy folder i plik .json (lub nadpisuje istniejący),
    oraz zapisuje w nim dane dla wybranego przedziału czasu.
    ○ “closeWindow” - zamyka to okno.
    ○ “restartWindow” - restartuje to okno.
● “OneDayObject” - przechowuje dane z jednego dnia

**3. webParser_entsoe.py**
● “Entsoe” - przechowuje dane z entsoe.
● “getDataFromAPI_oneDay” - łączy się z API Transparency Platform i pobiera
dane dla danego dnia.
● “parseENTSOE” - obrabia pobrane dane i zapisuje w odpowiedni sposób.
● “resetData” - zeruje dane utrzymywane w pamięci.

**4. webParser_tge.py**
● “Tge” - przechowuje dane z tge.
● “parseTGE” - pobiera kod strony tge, usuwa niepotrzebne elementy i
pozostawia jedynie ten zawierający tabelę z danymi.
● “getInfo” - wyciąga z tabelki potrzebne dane i zapisuje w odpowiedni sposób.
● “resetData” - zeruje dane utrzymywane w pamięci.

**5. utils.py**
Zawiera różne funkcje pomocnicze wykorzystywane w wielu plikach.
Funkcje:
● “getEUR” - sprawdza kurs EURPLN dnia poprzedniego od dnia podanego
(kurs z dnia poprzedniego, ponieważ ceny energii dla dnia 10.06.2024 są
ogłaszane dzień wcześniej - 09.06.2024, więc aby dane były prawidłowe kurs
również musi pochodzić z dnia poprzedniego). Gdy dane pochodzą z soboty
lub niedzieli (lub innego dnia, w którym nie został opublikowany kurs
EURPLN) używany jest ostatni znany kurs. Wykorzystywane przy każdym
pobieraniu danych. Źródło danych money.pl.
● “errorWindow” - tworzy małe okienko z podaną informacją. Stosowane do
wyświetlania informacji o błędach popełnianych przez użytkownika (np.
podanie nieprawidłowego przedziału dat).
● “checkNumberOfErrors” - sprawdza ilość błędów, które wystąpiły podczas
aktualnego pobierania danych, a jeśli ta przekracza 20 restartuje aplikacje.
● “tryInternetConnection” - sprawdza czy ma dostęp do internetu (poprzez
pingowanie “https://www.google.com”), jeśli nie uzyska odpowiedzi w ciągu 5
sekund - zwraca odpowiednią informację, oraz zapisuje błąd w pliku z
błędami.
● “saveError” - zapisuje informacje o błędach w pliku tekstowym z błędami.
● “decreaseOneDay”, “increaseOneDay”, “decreaseOneMonth”,
“increaseOneMonth” - zmniejszają lub zwiększają datę o określony czas.

Klasy:
● “CheckboxStatus” - przechowuje informacje o tym, które checkboxy sterujące
wykresem są zaznaczone.
● “Settings” - przechowuje aktualne ustawienia programu.
● “Errors” - przechowuje informacje o ilości błędów

**6. settingsOperations.py**
Operuje na ustawieniach programu:
- “currency” - waluta, w której podawane są dane, możliwe wartości: ‘PLN’ /
‘EUR’.
- “fixing” - określa czy dane pobrane ze strony tge pochodzą z fixingu
pierwszego czy drugiego, możliwe wartości: ‘1’ / ‘2’.
- “data_source” - źródło danych, możliwe wartości: ‘tge’ / ‘entsoe’.
- “updateTime” - mówi jak często aplikacja pobiera nowe dane (ilość sekund).
Możliwe wartości zawierają się w przedziale od ‘5’ do ‘7200’
- “entsoeKey” - klucz dostępu potrzebny do pobrania danych z API
Transparency Platform (instrukcja uzyskania klucza została opisana w
punkcie “Jak uzyskać dostęp do API Transparency Platform”)
Funkcje:
● “saveSettings_JSON” - tworzy nowy (lub nadpisuje istniejący) plik z
ustawieniami aplikacji i zapisuje w nim aktualne wartości.
● “createDefaultSettings” - tworzy plik z ustawieniami aplikacji i zapisuje w nim
domyślne wartości. Stosowany gdy nie znaleziono pliku z ustawieniami lub
zawierał niepoprawne dane.
● “loadSettings” - wczytuje ustawienia aplikacji z pliku z ustawieniami.
Stosowany przy otwieraniu programu.
● “saveError” - zapisuje informacje o błędach w pliku tekstowym.

**7. createCSV.py**
● “createCSV” - tworzy nowy (lub nadpisuje istniejący) plik z aktualnymi danymi
w pliku .csv. Znaczenie danych: “time” - godzina, której dotyczą dane (np. ‘0’
oznacza przedział 00:00-01:00), “entsoe” - dane pochodzące z entsoe z dnia
dzisiejszego, “entsoe_next” - dane pochodzące z entsoe z dnia jutrzejszego,
“tge” - dane pochodzące z tge z dnia dzisiejszego, “tge_next” - dane
pochodzące z tge z dnia jutrzejszego.

**8. createHTML.py**
● “createHTML” - tworzy nowy (lub nadpisuje istniejący) plik z aktualnymi
danymi w pliku .html w formie prostej tabelki. Znaczenie danych: “time” -
godzina, której dotyczą dane (np. ‘0’ oznacza przedział 00:00-01:00), “entsoe”
- dane pochodzące z entsoe z dnia dzisiejszego, “entsoe_next” - dane
pochodzące z entsoe z dnia jutrzejszego, “tge” - dane pochodzące z tge z
dnia dzisiejszego, “tge_next” - dane pochodzące z tge z dnia jutrzejszego

**9. createJSON.py**
●  “createJSON” - tworzy nowy (lub nadpisuje istniejący) plik z aktualnymi
danymi w pliku .json. Znaczenie danych: “time” - godzina, której dotyczą dane
(np. ‘0’ oznacza przedział 00:00-01:00), “entsoe” - dane pochodzące z entsoe
z dnia dzisiejszego, “entsoe_next” - dane pochodzące z entsoe z dnia
jutrzejszego, “tge” - dane pochodzące z tge z dnia dzisiejszego, “tge_next” -
dane pochodzące z tge z dnia jutrzejszego.

**10.sendToSQLite.py**
Zapisuje odczytane dane w bazie danych w SQLite
● “sendToSQLite” - sprawdza czy w bazie danych istnieje tabela dla danego
dnia, jeśli nie, tworzy ją. Schemat nazewnictwa
“odczyt_[rok]_[miesiąc]_[dzień]”.
● “send” - wysyła aktualne dane do bazy danych w tabeli odpowiedniej dla
danego dnia. Znaczenie danych: “hours” - godzina, której dotyczą dane (np.
‘0’ oznacza przedział 00:00-01:00), “price_entsoe” - dane pochodzące z
entsoe z dnia dzisiejszego, “price_entsoe_next” - dane pochodzące z entsoe
z dnia jutrzejszego, “price_tge” - dane pochodzące z tge z dnia dzisiejszego,
“price_tge_next” - dane pochodzące z tge z dnia jutrzejszego, “date” - dzień,
z którego pochodzą dane, “upload_time” - dokładna data i godzina, w której
dane zostały pobrane.
```
