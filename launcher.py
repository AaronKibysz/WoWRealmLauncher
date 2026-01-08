from config import cargar_config
from ui import ventana_principal, ventana_configuracion, splash_screen

def main():
    config = cargar_config()
    splash_screen()  # Pantalla inicial WoW
    if not config["wow_path"]:
        ventana_configuracion(config)
    else:
        ventana_principal(config)

if __name__ == "__main__":
    main()