# ui.py
import os
import subprocess
import tkinter.messagebox as mbox
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv

import customtkinter as ctk
from PIL import Image, ImageTk

from config import guardar_config
from realmlist import cambiar_realmlist
from realms import agregar_realm, quitar_realm, editar_realm, actualizar_combo
from addons import obtener_addons, abrir_addons_folder
from version import APP_VERSION
import updater

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Cargar variables desde .env para el envío de reportes
load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")  # ezequielkost2002@gmail.com (en .env)
SMTP_PASS = os.getenv("SMTP_PASS")

# URL pública de tu latest.json en GitHub Pages (cambia TUUSUARIO)
LATEST_JSON_URL = "https://TUUSUARIO.github.io/WoWRealmLauncher/latest.json"

# Barra de estado global (se inicializa en ventana_principal)
status_bar = None


def splash_screen():
    splash = ctk.CTk()
    splash.overrideredirect(True)
    splash.geometry("420x320+500+300")
    splash.configure(fg_color="#0B0C10")

    # Icono de la ventana
    if os.path.exists("assets/logo.ico"):
        try:
            splash.iconbitmap("assets/logo.ico")
        except Exception:
            pass

    # Logo del splash
    if os.path.exists("assets/logo.png"):
        try:
            img = Image.open("assets/logo.png").resize((200, 200))
            logo = ImageTk.PhotoImage(img)
            splash.logo_ref = logo  # evitar garbage collection
            ctk.CTkLabel(splash, image=logo, text="").pack(pady=10)
        except Exception:
            pass

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
        try:
            root.iconbitmap("assets/logo.ico")
        except Exception:
            pass

    # Logo dentro de la ventana
    if config.get("logo_enabled", True) and os.path.exists("assets/logo.png"):
        try:
            img = Image.open("assets/logo.png").resize((100, 100))
            logo = ImageTk.PhotoImage(img)
            root.logo_ref = logo  # evitar garbage collection
            ctk.CTkLabel(root, image=logo, text="").pack(pady=5)
        except Exception:
            pass

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

    combo_values = [f"{r['name']} ({r['address']})" for r in config.get("realms", [])]
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

    # --- Configuración y utilidades ---
    ctk.CTkButton(root, text="⚙ Configuración",
                  command=lambda: ventana_configuracion(config)).pack(pady=5)

    ctk.CTkButton(root, text="🔄 Buscar actualizaciones",
                  command=comprobar_actualizacion).pack(pady=5)

    ctk.CTkButton(root, text="🐞 Reportar problema",
                  command=lambda: ventana_reportar_problema(config)).pack(pady=5)

    # --- Barra de estado ---
    global status_bar
    status_bar = ctk.CTkLabel(root, text="Listo", anchor="w")
    status_bar.pack(side="bottom", fill="x")

    root.mainloop()


def comprobar_actualizacion():
    status_bar.configure(text="Buscando actualizaciones...", text_color="#FFD700")
    ok, temp_exe, msg = updater.prepare_update(LATEST_JSON_URL, APP_VERSION)
    if not ok:
        status_bar.configure(text=msg, text_color="red")
        return

    if not mbox.askyesno("Actualizar", f"{msg}\n¿Quieres instalar la nueva versión?"):
        status_bar.configure(text="Actualización cancelada", text_color="#FFD700")
        return

    try:
        updater.lanzar_actualizador_y_salir(temp_exe)
    except Exception as e:
        status_bar.configure(text=f"Error al actualizar: {e}", text_color="red")


def ventana_configuracion(config):
    root = ctk.CTk()
    root.title("Configurar ruta de WoW")
    root.geometry("520x240+520+320")

    # Icono de la ventana
    if os.path.exists("assets/logo.ico"):
        try:
            root.iconbitmap("assets/logo.ico")
        except Exception:
            pass

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


def lanzar_wow(config, realm_value, status):
    realm_name = realm_value.split(" (")[0] if realm_value else ""
    realm = next((r for r in config.get("realms", []) if r["name"] == realm_name), None)
    if not realm:
        status.configure(text="Debes seleccionar un realm", text_color="red")
        return

    ok = cambiar_realmlist(config.get("wow_path") or "", realm["address"])
    if not ok:
        status.configure(text="Error al cambiar el realm", text_color="red")
        return

    config["last_realm"] = realm["name"]
    guardar_config(config)

    posibles_exes = ["Wow.exe", "WowClassic.exe", "WowRetail.exe"]
    wow_exe = next(
        (os.path.join(config.get("wow_path") or "", exe)
         for exe in posibles_exes
         if os.path.exists(os.path.join(config.get("wow_path") or "", exe))),
        None
    )

    if wow_exe:
        try:
            subprocess.Popen([wow_exe])
            status.configure(text=f"Lanzando WoW en {realm['name']}", text_color="green")
        except Exception as e:
            status.configure(text=f"Error al lanzar WoW: {e}", text_color="red")
    else:
        status.configure(text="No se encontró ejecutable de WoW", text_color="red")


# ----------------------------
# Reportar problema por correo
# ----------------------------
def enviar_reporte(problema: str, explicacion: str, email_usuario: str = ""):
    if not SMTP_USER or not SMTP_PASS:
        raise RuntimeError("SMTP no configurado. Falta SMTP_USER/SMTP_PASS en .env.")

    msg = EmailMessage()
    msg["Subject"] = f"Reporte de problema: {problema}"
    msg["From"] = SMTP_USER
    msg["To"] = SMTP_USER  # tu correo, oculto en .env

    cuerpo = (
        f"Problema: {problema}\n"
        f"Explicación:\n{explicacion}\n\n"
        f"Email del usuario: {email_usuario if email_usuario else 'No proporcionado'}\n"
    )
    msg.set_content(cuerpo)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


def ventana_reportar_problema(config):
    root = ctk.CTk()
    root.title("Reportar problema")
    root.geometry("520x420+520+220")

    # Icono de la ventana
    if os.path.exists("assets/logo.ico"):
        try:
            root.iconbitmap("assets/logo.ico")
        except Exception:
            pass

    # Problema (obligatorio)
    ctk.CTkLabel(root, text="Problema (obligatorio):",
                 font=ctk.CTkFont(size=14), text_color="#FFD700").pack(pady=(10, 5))
    entry_problema = ctk.CTkEntry(root, width=420)
    entry_problema.pack(pady=5)

    # Explicación (obligatoria)
    ctk.CTkLabel(root, text="Explica el problema (obligatorio):",
                 font=ctk.CTkFont(size=14), text_color="#FFD700").pack(pady=(10, 5))
    entry_explicacion = ctk.CTkTextbox(root, width=420, height=160)
    entry_explicacion.pack(pady=5)

    # Email (opcional)
    ctk.CTkLabel(root, text="Email (opcional):",
                 font=ctk.CTkFont(size=14), text_color="#FFD700").pack(pady=(10, 5))
    entry_email = ctk.CTkEntry(root, width=420)
    entry_email.insert(0, "(opcional)")
    entry_email.pack(pady=5)

    def enviar():
        problema = entry_problema.get().strip()
        explicacion = entry_explicacion.get("1.0", "end").strip()
        email_usuario = entry_email.get().strip()
        if email_usuario == "(opcional)":
            email_usuario = ""

        if not problema or not explicacion:
            mbox.showerror("Error", "Debes completar los campos obligatorios.")
            return

        try:
            enviar_reporte(problema, explicacion, email_usuario)
            mbox.showinfo("Reporte enviado", "¡Gracias por tu reporte!")
            root.destroy()
        except Exception as e:
            mbox.showerror("Error", f"No se pudo enviar el reporte: {e}")

    ctk.CTkButton(root, text="Enviar reporte", command=enviar).pack(pady=12)
    root.mainloop()
