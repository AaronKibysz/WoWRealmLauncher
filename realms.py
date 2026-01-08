import customtkinter as ctk
from tkinter import messagebox
from config import guardar_config

def agregar_realm(config, combo, status_bar=None):
    nombre = ctk.CTkInputDialog(text="Nombre del realm:", title="Agregar Realm").get_input()
    direccion = ctk.CTkInputDialog(text="Dirección del servidor:", title="Agregar Realm").get_input()
    if not nombre or not direccion:
        return

    # Validaciones básicas
    nombre = nombre.strip()
    direccion = direccion.strip()
    if not nombre or not direccion:
        messagebox.showwarning("Aviso", "Debes ingresar nombre y dirección válidos.")
        return
    if any(r["name"] == nombre for r in config["realms"]):
        messagebox.showwarning("Aviso", "Ya existe un realm con ese nombre.")
        return

    config["realms"].append({"name": nombre, "address": direccion})
    guardar_config(config)
    actualizar_combo(config, combo)
    if status_bar:
        status_bar.configure(text=f"Realm agregado: {nombre}", text_color="#FFD700")

def quitar_realm(config, combo, status_bar=None):
    valor = combo.get()
    if not valor:
        messagebox.showwarning("Aviso", "Selecciona un realm para quitar.")
        return

    idx = next((i for i, r in enumerate(config["realms"])
                if f"{r['name']} ({r['address']})" == valor), -1)

    if idx == -1:
        messagebox.showwarning("Aviso", "No se encontró el realm seleccionado.")
        return

    nombre = config["realms"][idx]["name"]
    if messagebox.askyesno("Confirmar", f"¿Seguro que quieres eliminar {nombre}?"):
        config["realms"].pop(idx)
        guardar_config(config)
        actualizar_combo(config, combo)
        if status_bar:
            status_bar.configure(text=f"Realm eliminado: {nombre}", text_color="#FFD700")

def editar_realm(config, combo, status_bar=None):
    valor = combo.get()
    if not valor:
        messagebox.showwarning("Aviso", "Selecciona un realm para editar.")
        return

    idx = next((i for i, r in enumerate(config["realms"])
                if f"{r['name']} ({r['address']})" == valor), -1)

    if idx == -1:
        messagebox.showwarning("Aviso", "No se encontró el realm seleccionado.")
        return

    realm = config["realms"][idx]

    # Ventana emergente con CustomTkinter
    edit_win = ctk.CTkToplevel()
    edit_win.title("Editar Realm")
    edit_win.geometry("420x240+600+300")
    edit_win.grab_set()

    ctk.CTkLabel(edit_win, text="Nombre del Realm:").pack(pady=5)
    entry_nombre = ctk.CTkEntry(edit_win, width=320)
    entry_nombre.pack(pady=5)
    entry_nombre.insert(0, realm["name"])

    ctk.CTkLabel(edit_win, text="Dirección del Servidor:").pack(pady=5)
    entry_direccion = ctk.CTkEntry(edit_win, width=320)
    entry_direccion.pack(pady=5)
    entry_direccion.insert(0, realm["address"])

    def guardar():
        nuevo_nombre = entry_nombre.get().strip()
        nueva_direccion = entry_direccion.get().strip()
        if not nuevo_nombre or not nueva_direccion:
            messagebox.showwarning("Aviso", "Debes ingresar nombre y dirección válidos.")
            return
        config["realms"][idx] = {"name": nuevo_nombre, "address": nueva_direccion}
        guardar_config(config)
        actualizar_combo(config, combo)
        if status_bar:
            status_bar.configure(text=f"Realm actualizado: {nuevo_nombre}", text_color="#00D26A")
        edit_win.destroy()

    def cancelar():
        if status_bar:
            status_bar.configure(text="Edición cancelada", text_color="#FFD700")
        edit_win.destroy()

    frame_botones = ctk.CTkFrame(edit_win)
    frame_botones.pack(pady=15)

    ctk.CTkButton(frame_botones, text="Guardar", command=guardar, fg_color="#4CAF50", hover_color="#43A047").pack(side="left", padx=10)
    ctk.CTkButton(frame_botones, text="Cancelar", command=cancelar, fg_color="#F44336", hover_color="#E53935").pack(side="right", padx=10)

def actualizar_combo(config, combo):
    opciones = [f"{r['name']} ({r['address']})" for r in config["realms"]]
    combo.configure(values=opciones)
    if opciones:
        last = config.get("last_realm")
        for r in config["realms"]:
            if r["name"] == last:
                combo.set(f"{r['name']} ({r['address']})")
                return
        combo.set(opciones[0])
