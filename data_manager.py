import json
import os

# Fájlnevek definiálása
DB_FILE = "inventory.json"
HISTORY_FILE = "history.json"

# --- TERMÉK ADATOK KEZELÉSE ---

def load_data():
    """Betölti a terméklistát a JSON fájlból. Ha nem létezik, üres listát ad vissza."""
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Hiba a termékadatok betöltésekor: {e}")
        return []

def save_data(data):
    """Elmenti a terméklistát a JSON fájlba, megőrizve az ékezetes karaktereket."""
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Hiba a termékadatok mentésekor: {e}")

# --- TRANZAKCIÓS ELŐZMÉNYEK KEZELÉSE ---

def load_history():
    """Betölti a tranzakciós naplót a history.json fájlból."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Hiba az előzmények betöltésekor: {e}")
        return []

def save_history(history_data):
    """Elmenti a tranzakciós naplót a history.json fájlba."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Hiba az előzmények mentésekor: {e}")