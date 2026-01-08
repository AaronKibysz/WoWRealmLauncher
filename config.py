import os
import json

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "wow_path": None,
    "realms": [],
    "last_realm": None,
    "addons_path": None,
    "theme": "wow_dark",
    "font": "Morpheus",
    "logo_enabled": True,
    "config_version": 1
}

def cargar_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_CONFIG, **data}
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error cargando configuración: {e}")
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def guardar_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except OSError as e:
        print(f"Error guardando configuración: {e}")