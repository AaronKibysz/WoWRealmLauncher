import os
import subprocess
from tkinter import messagebox

def obtener_addons(wow_path):
    addons_dir = os.path.join(wow_path, "Interface", "AddOns")
    if not os.path.exists(addons_dir):
        messagebox.showerror("Error", f"No se encontró la carpeta AddOns en:\n{addons_dir}")
        return []
    return [d for d in os.listdir(addons_dir) if os.path.isdir(os.path.join(addons_dir, d))]

def abrir_addons_folder(wow_path):
    addons_dir = os.path.join(wow_path, "Interface", "AddOns")
    if os.path.exists(addons_dir):
        try:
            subprocess.Popen(f'explorer "{addons_dir}"')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta AddOns:\n{e}")
    else:
        messagebox.showerror("Error", f"No se encontró la carpeta AddOns en:\n{addons_dir}")
