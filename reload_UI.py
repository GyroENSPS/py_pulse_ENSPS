import subprocess
import os

# === Paramètres à personnaliser ===
ui_file = 'GUI/UI_files/table_widget_test.ui'
py_file = 'GUI/UI_files/table_widget_test.py'

# === Commande pyuic5 ===
command = f"pyuic5 -x {ui_file} -o {py_file}"

# === Exécution ===
try:
    subprocess.run(command, check=True, shell=True)
    print(f"✅ Fichier .ui converti avec succès : {py_file}")
except subprocess.CalledProcessError as e:
    print("❌ Erreur lors de la conversion du fichier .ui")
    print(e)