# CRUD dla produktów (Flask + SQLite)
Ten projekt to prosta aplikacja CRUD stworzona w Pythonie z użyciem Flask i bazy danych SQLite.  
Umozliwia dodawanie, edytowanie, usuwanie i przegladanie produktow poprzez REST API i prosty interfejs webowy.
## Jak uruchomic projekt
1. Zainstaluj wymagaane biblioteki: pip install flask 
2. Uruchom serwer: python app.py 
3. W przegladarce otworz: http://127.0.0.1:5000/ui

Po uruchomieniu zobaczysz prosta strone, ktora pozwala dodawac, edytowac i usuwac produkty.
## Endpointy API
Metoda GET | /produkty | Zwraca wszystkie produkty 
Metoda POST | /produkty | Dodaje nowy produkt 
Metoda PUT | /produkty/<id> | Aktualizuje produkt 
Metoda DELETE | /produkty/<id> | Usuwa produkt 
## Struktura tabeli 'produkty' 
KOLUMNA | TYP | OPIS
id      |Int  | Klucz glowny 
nazwa   |text | Nazwa Produktu 
cena    |real | Cena produktu
kategor |text | Kategoria produktu 
ilosc   |int  | Ilosc w magazynie 