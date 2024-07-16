import os
import subprocess

def run_command(command):
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Erreur lors de l'exécution de '{command}': {result.stderr}")
    else:
        print(f"Succès: {result.stdout}")

# Supprimer l'ancienne base de données et le dossier de migrations
if os.path.exists('../instance/prorga.db'):
    os.remove('../instance/prorga.db')
    print("Base de données supprimée")
else:
    print("Aucune base de données à supprimer")

if os.path.exists('../migrations'):
    subprocess.run('rmdir /S /Q migrations', shell=True)
    print("Dossier de migrations supprimé")
else:
    print("Aucun dossier de migrations à supprimer")

# Initialiser et appliquer les nouvelles migrations
run_command('python manage.py db init')
run_command('python manage.py db migrate -m "Initial migration"')
run_command('python manage.py db upgrade')
