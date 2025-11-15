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

try:
    with open(py_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Remplacement de l’import
    content = content.replace(
        "import resources_rc",
        "from GUI.UI_files import resources_rc"
    )

    with open(py_file, "w", encoding="utf-8") as f:
        f.write(content)

    print("🔧 Import 'resources_rc' corrigé automatiquement.")

except Exception as e:
    print("❌ Erreur lors de la modification du fichier généré")
    print(e)

# === Paramètres à personnaliser ===
ui_file = 'GUI/UI_files/PS_config.ui'
py_file = 'GUI/UI_files/PS_config_Window_UI.py'

# === Commande pyuic5 ===
command = f"pyuic5 -x {ui_file} -o {py_file}"

# === Exécution ===
try:
    subprocess.run(command, check=True, shell=True)
    print(f"✅ Fichier .ui converti avec succès : {py_file}")
except subprocess.CalledProcessError as e:
    print("❌ Erreur lors de la conversion du fichier .ui")
    print(e)