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

# Zmiany wprowadzone (Wymaganie B)
- Dodano dwa nowe pola do encji produkty: producent i data_dodania.
- Zaktualizowano:
  - Model/Tabelę: kolumny producent i data_dodania
  - API REST: uwzględnia nowe pola przy GET, POST i PUT
  - Frontend: formularz dodawania/edycji i lista produktów z nowymi polami
