# CRUD dla produktów (Flask + SQLite)
Ten projekt to prosta aplikacja CRUD stworzona w Pythonie z użyciem Flask i bazy danych SQLite.  
Umozliwia dodawanie, edytowanie, usuwanie i przegladanie produktow poprzez REST API i prosty interfejs webowy.
## Jak uruchomic projekt
1. Zainstaluj wymagaane biblioteki: pip install flask 
2. Uruchom serwer: python app.py 
3. W przegladarce otworz: http://127.0.0.1:5000

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

# URL 
https://fatta666.pythonanywhere.com/ 
Login: fatta666
haslo: 17072005

# Integracja API: Żarty o Chucku Norrisie
1. Opis Integracji
Ta integracja zastępuje planowaną integrację kursów walut na rzecz prostszego API, co pozwala na szybkie wdrożenie wszystkich aspektów zadania (Warstwa Klienta, Obsługa Błędów, Testy).

Zewnętrzne API: Chuck Norris Jokes API (https://api.chucknorris.io).

Warstwa Serwisowa: Logika API znajduje się w pliku joke_service.py.
Aby uzyskać losowy żart z Chuck Norris Jokes API, wywołaj:

GET /external/joke
Zapytanie (cURL)
curl -X GET http://localhost:5000/external/joke
Uproszczona Odpowiedź (HTTP 200 OK)
Baza danych zwraca uproszczony model danych (ID, tekst i URL źródłowy):
{
    "joke_id": "9h5e1z-x-s-a-g",
    "joke_text": "Chuck Norris potrafi pisać skrypty w HTML, które są Turing Complete.",
    "source_url": "[https://api.chucknorris.io/jokes/9h5e1z-x-s-a-g](https://api.chucknorris.io/jokes/9h5e1z-x-s-a-g)"
}
Obsługa BłędówBackend przechwytuje błędy zewnętrzne i zwraca spójne kody HTTP:ScenariuszKod HTTPKomunikatBrak odpowiedzi / Timeout503 Service Unavailable"Usługa żartów chwilowo niedostępna. Spróbuj później."Błąd po stronie API (np. 500)502 Bad Gateway"Błąd zewnętrznego API z żartami."
Testy Integracyjne
Wszystkie testy integracyjne dla tego endpointu zostały dodane do pliku test_integration.py i używają mocków, aby symulować odpowiedzi z API Chuck Norris.

Testy sprawdzają:

Poprawną ścieżkę (happy path).

Obsługę błędu serwera zewnętrznego (502).

Obsługę timeoutu/braku połączenia (503).
Aby uruchomić testy:pytest




