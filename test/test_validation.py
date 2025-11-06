import pytest
from app import validate_produkt_payload



def test_validate_valid_product():
    data = {"nazwa":"Produkt X","cena":10.5,"ilosc":5,"data_dodania":None}
    errs = validate_produkt_payload(data)
    assert errs == []

def test_validate_invalid_price_and_name():
    data = {"nazwa":"ab","cena":0,"ilosc":-1}
    errs = validate_produkt_payload(data)
    fields = {e['field'] for e in errs}
    assert 'nazwa' in fields
    assert 'cena' in fields
    assert 'ilosc' in fields

def test_validate_future_date():
    from datetime import date, timedelta
    future = (date.today() + timedelta(days=1)).isoformat()
    errs = validate_produkt_payload({"data_dodania": future}, partial=False)
    assert any(e['field']=='data_dodania' for e in errs)
