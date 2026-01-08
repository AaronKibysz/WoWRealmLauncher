# updater.py
import os, sys, json, hashlib, tempfile, urllib.request, subprocess

TIMEOUT = 10

def fetch_latest_json(latest_url: str) -> dict | None:
    try:
        with urllib.request.urlopen(latest_url, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None

def is_newer_version(current: str, remote: str) -> bool:
    def parse(v): return [int(x) for x in v.split(".")]
    try:
        return parse(remote) > parse(current)
    except Exception:
        return False

def download_file(url: str, dest_path: str) -> bool:
    try:
        urllib.request.urlretrieve(url, dest_path)
        return os.path.exists(dest_path) and os.path.getsize(dest_path) > 0
    except Exception:
        return False

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def prepare_update(latest_url: str, current_version: str) -> tuple[bool, str, str]:
    latest = fetch_latest_json(latest_url)
    if not latest:
        return False, "", "No se pudo obtener información de actualización."

    remote_version = latest.get("version")
    download_url = latest.get("url")
    expected_sha = latest.get("sha256")

    if not remote_version or not download_url:
        return False, "", "latest.json inválido."

    # Siempre descarga la última versión publicada
    temp_exe = os.path.join(tempfile.gettempdir(), f"WoWRealmLauncher-{remote_version}.exe")
    if not download_file(download_url, temp_exe):
        return False, "", "No se pudo descargar la versión publicada."

    # Validar checksum si está presente
    if expected_sha:
        actual_sha = sha256_file(temp_exe)
        if actual_sha.lower() != expected_sha.lower():
            try: os.remove(temp_exe)
            except Exception: pass
            return False, "", "Checksum inválido. Descarga corrupta o alterada."

    # Mensajes según comparación de versiones
    if not is_newer_version(current_version, remote_version):
        return True, temp_exe, f"Ya estás en la versión {current_version}, pero puedes reinstalarla."
    else:
        return True, temp_exe, f"Nueva versión {remote_version} disponible."

def lanzar_actualizador_y_salir(temp_exe_path: str):
    if not getattr(sys, "frozen", False):
        return

    launcher_exe = sys.executable
    bat_path = os.path.join(tempfile.gettempdir(), "wowlauncher_update.bat")
    new_exe = temp_exe_path
    old_exe = launcher_exe

    bat_content = f"""@echo off
timeout /t 1 >nul
taskkill /F /IM "{os.path.basename(old_exe)}" >nul 2>&1
timeout /t 1 >nul
copy /Y "{new_exe}" "{old_exe}"
timeout /t 1 >nul
start "" "{old_exe}"
del "{new_exe}"
del "%~f0"
"""

    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_content)

    subprocess.Popen(["cmd", "/c", bat_path], close_fds=True)
    os._exit(0)
