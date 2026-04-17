import pytest
from app import calculate_total_price

def test_calculate_total_price_with_numeric_values():
    prices = [10.5, 20.0, 5.0]
    assert calculate_total_price(prices) == 35.5

def test_calculate_total_price_with_non_numeric_value():
    prices = [10.5, 20.0, "oops", 5.0]
    with pytest.raises(TypeError):
        calculate_total_price(prices)

def test_calculate_total_price_with_empty_list():
    prices = []
    assert calculate_total_price(prices) == 0