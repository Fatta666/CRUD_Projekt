import requests
from requests.exceptions import Timeout, ConnectionError
from typing import Dict

class JokeIntegrationError(Exception):
    pass

class ServiceUnavailableError(JokeIntegrationError):
    """Błąd braku odpowiedzi / timeout (503)."""
    def __init__(self):
        super().__init__("Usługa żartów chwilowo niedostępna. Spróbuj później.")

class BadGatewayError(JokeIntegrationError):
    """Błąd po stronie zewnętrznego API (5xx) (502)."""
    def __init__(self, message="Błąd zewnętrznego API z żartami."):
        super().__init__(message)


class JokeClient:
    """Klient do integracji z Chuck Norris Jokes API."""
    
    API_URL = "https://api.chucknorris.io/jokes/random" 
    
    def get_random_joke(self) -> Dict:
        """
        Pobiera losowy żart o Chucku Norrisie i zwraca uproszczony JSON.
        """
        
        try:
            response = requests.get(self.API_URL, timeout=5)
            
        except (Timeout, ConnectionError):
            raise ServiceUnavailableError() 
            
        if response.status_code != 200:
            
            raise BadGatewayError(f"Zewnętrzny API żartów zwrócił status: {response.status_code}") 
            
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise BadGatewayError("Zewnętrzne API zwróciło nieprawidłową odpowiedź (nie-JSON).")

        simplified_joke = {
            "joke_id": data.get('id'),
            "joke_text": data.get('value'),
            "source_url": data.get('url')
        }
        
        return simplified_joke