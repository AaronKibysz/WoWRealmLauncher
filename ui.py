import os
import customtkinter as ctk
from PIL import Image, ImageTk
import subprocess

from config import guardar_config
from realmlist import cambiar_realmlist
from realms import agregar_realm, quitar_realm, editar_realm, actualizar_combo
from addons import obtener_addons, abrir_addons_folder

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def splash_screen():
    splash = ctk.CTk()
    splash.overrideredirect(True)
    splash.geometry("420x320+500+300")
    splash.configure(fg_color="#0B0C10")

    # Icono de la ventana
    if os.path.exists("assets/logo.ico"):
        splash.iconbitmap("assets/logo.ico")

    if os.path.exists("assets/logo.png"):
        img = Image.open("assets/logo.png").resize((200, 200))
        logo = ImageTk.PhotoImage(img)
        splash.logo_ref = logo
        ctk.CTkLabel(splash, image=logo, text="").pack(pady=10)

    ctk.CTkLabel(
        splash,
        text="WoW Launcher by Zpumae",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#FFD700"
    ).pack()

    splash.after(2000, splash.destroy)
    splash.mainloop()

def ventana_principal(config):
    root = ctk.CTk()
    root.title("⚔️ WoW Launcher by Zpumae")
    root.geometry("820x600+400+100")

    # Icono de la ventana
    if os.path.exists("assets/logo.ico"):
        root.iconbitmap("assets/logo.ico")

    # Logo dentro de la ventana
    if config.get("logo_enabled", True) and os.path.exists("assets/logo.png"):
        img = Image.open("assets/logo.png").resize((100, 100))
        logo = ImageTk.PhotoImage(img)
        root.logo_ref = logo
        ctk.CTkLabel(root, image=logo, text="").pack(pady=5)

    # Main frame dividido en dos columnas
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(pady=10, padx=10, fill="both", expand=True)

    left_frame = ctk.CTkFrame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=5)

    right_frame = ctk.CTkFrame(main_frame)
    right_frame.pack(side="right", fill="both", expand=True, padx=5)

    # --- Realms (izquierda) ---
    ctk.CTkLabel(left_frame, text="⚔️ Realms",
                 font=ctk.CTkFont(size=16, weight="bold"),
                 text_color="#FFD700").pack(pady=5)

    combo_values = [f"{r['name']} ({r['address']})" for r in config["realms"]]
    combo = ctk.CTkComboBox(left_frame, values=combo_values, width=240)
    combo.pack(pady=5)

    ctk.CTkButton(left_frame, text="➕ Agregar",
                  command=lambda: agregar_realm(config, combo, status_bar)).pack(pady=3)
    ctk.CTkButton(left_frame, text="✏️ Editar",
                  command=lambda: editar_realm(config, combo, status_bar)).pack(pady=3)
    ctk.CTkButton(left_frame, text="🗑 Quitar",
                  command=lambda: quitar_realm(config, combo, status_bar)).pack(pady=3)

    ctk.CTkButton(left_frame, text="🚀 Launch WoW",
                  fg_color="#C19A6B", hover_color="#D97706",
                  command=lambda: lanzar_wow(config, combo.get(), status_bar)).pack(pady=10)

    # --- AddOns (derecha) ---
    ctk.CTkLabel(right_frame, text="📦 AddOns instalados",
                 font=ctk.CTkFont(size=16, weight="bold"),
                 text_color="#FFD700").pack(pady=5)

    addons_list = ctk.CTkTextbox(right_frame, width=300, height=200)
    addons_list.pack(pady=5)
    addons = obtener_addons(config.get("wow_path") or "")
    for a in addons:
        addons_list.insert("end", a + "\n")

    ctk.CTkButton(right_frame, text="📂 Abrir carpeta",
                  command=lambda: abrir_addons_folder(config.get("wow_path") or "")).pack(pady=3)
    ctk.CTkButton(right_frame, text="🔄 Actualizar lista",
                  command=lambda: refrescar_addons(addons_list, config)).pack(pady=3)

    # --- Configuración rápida y status ---
    ctk.CTkButton(root, text="⚙ Configuración",
                  command=lambda: ventana_configuracion(config)).pack(pady=5)

    global status_bar
    status_bar = ctk.CTkLabel(root, text="Listo", anchor="w")
    status_bar.pack(side="bottom", fill="x")

    root.mainloop()

def ventana_configuracion(config):
    root = ctk.CTk()
    root.title("Configurar ruta de WoW")
    root.geometry("520x240+520+320")

    # Icono de la ventana
    if os.path.exists("assets/logo.ico"):
        root.iconbitmap("assets/logo.ico")

    ctk.CTkLabel(root, text="Selecciona la carpeta donde está instalado WoW:",
                 font=ctk.CTkFont(size=14),
                 text_color="#FFD700").pack(pady=10)

    entry = ctk.CTkEntry(root, width=400)
    entry.pack(pady=5)

    def seleccionar_ruta():
        import tkinter.filedialog as fd
        ruta = fd.askdirectory(title="Selecciona la carpeta de World of Warcraft")
        if ruta:
            entry.delete(0, "end")
            entry.insert(0, ruta)

    def confirmar_ruta():
        ruta = entry.get()
        if not ruta or not os.path.exists(ruta):
            status_bar.configure(text="La ruta ingresada no existe", text_color="red")
            return
        config["wow_path"] = ruta
        guardar_config(config)
        status_bar.configure(text="Ruta de WoW guardada", text_color="#FFD700")
        root.destroy()
        ventana_principal(config)

    ctk.CTkButton(root, text="Buscar carpeta", command=seleccionar_ruta).pack(pady=5)
    ctk.CTkButton(root, text="Confirmar", command=confirmar_ruta).pack(pady=10)

    root.mainloop()

def refrescar_addons(addons_list, config):
    addons_list.delete("1.0", "end")
    addons = obtener_addons(config.get("wow_path") or "")
    for a in addons:
        addons_list.insert("end", a + "\n")
    status_bar.configure(text=f"AddOns detectados: {len(addons)}", text_color="#FFD700")

def lanzar_wow(config, realm_value, status_bar):
    realm_name = realm_value.split(" (")[0] if realm_value else ""
    realm = next((r for r in config["realms"] if r["name"] == realm_name), None)
    if not realm:
        status_bar.configure(text="Debes seleccionar un realm", text_color="red")
        return

    ok = cambiar_realmlist(config["wow_path"], realm["address"])
    if not ok:
        status_bar.configure(text="Error al cambiar el realm", text_color="red")
        return

    config["last_realm"] = realm["name"]
    guardar_config(config)

    posibles_exes = ["Wow.exe", "WowClassic.exe", "WowRetail.exe"]
    wow_exe = next((os.path.join(config["wow_path"], exe)
                    for exe in posibles_exes
                    if os.path.exists(os.path.join(config["wow_path"], exe))), None)

    if wow_exe:
        try:
            subprocess.Popen([wow_exe])
            status_bar.configure(text=f"Lanzando WoW en {realm['name']}", text_color="green")
        except Exception as e:
            status_bar.configure(text=f"Error al lanzar WoW: {e}", text_color="red")
    else:
        status_bar.configure(text="No se encontró ejecutable de WoW", text_color="red")
