import sys
import os
import pytest

# Add the parent directory to the Python path to allow importing the script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from import_pos_menu import guess_columns

def test_guess_columns_english():
    headers = ["Product Name", "Price", "Category", "SKU"]
    expected = {"name": 0, "price": 1, "category": 2, "sku": 3}
    assert guess_columns(headers) == expected

def test_guess_columns_chinese():
    headers = ["品名", "售價", "類別", "主商品編號"]
    expected = {"name": 0, "price": 1, "category": 2, "sku": 3}
    assert guess_columns(headers) == expected

def test_guess_columns_mixed():
    headers = ["Name", "售價", "cat", "條碼"]
    expected = {"name": 0, "price": 1, "category": 2, "sku": 3}
    assert guess_columns(headers) == expected

def test_guess_columns_with_combo():
    headers = ["名稱", "價格", "分類", "套用加購選單"]
    expected = {"name": 0, "price": 1, "category": 2, "combo_id": 3}
    assert guess_columns(headers) == expected

def test_guess_columns_missing_some():
    headers = ["Product Name", "Price"]
    expected = {"name": 0, "price": 1}
    assert guess_columns(headers) == expected

def test_guess_columns_empty():
    headers = []
    expected = {}
    assert guess_columns(headers) == expected
