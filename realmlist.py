import os
from tkinter import messagebox

def cambiar_realmlist(wow_path, servidor):
    # Posibles ubicaciones del realmlist.wtf
    posibles_rutas = []

    # Carpeta Data con idiomas
    idiomas = ["esMX", "esES", "enUS", "deDE", "frFR", "ruRU", "zhCN", "zhTW", "koKR"]
    for idioma in idiomas:
        posibles_rutas.append(os.path.join(wow_path, "Data", idioma, "realmlist.wtf"))

    # Carpeta Data sin idioma
    posibles_rutas.append(os.path.join(wow_path, "Data", "realmlist.wtf"))

    # Carpeta raíz (algunos clientes lo ponen aquí)
    posibles_rutas.append(os.path.join(wow_path, "realmlist.wtf"))

    realmlist_path = None
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            realmlist_path = ruta
            break

    if not realmlist_path:
        messagebox.showerror("Error", "No se encontró realmlist.wtf en ninguna carpeta.")
        return False

    try:
        with open(realmlist_path, "w", encoding="utf-8") as f:
            f.write(f"set realmlist {servidor}\n")
        messagebox.showinfo("Éxito", f"Realm cambiado a {servidor}\nArchivo: {realmlist_path}")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo modificar el archivo:\n{e}")
        return False