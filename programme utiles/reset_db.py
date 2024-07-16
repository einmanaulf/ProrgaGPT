import subprocess

def run_command(command):
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Erreur lors de l'exécution de '{command}': {result.stderr}")
    else:
        print(f"Succès: {result.stdout}")

# Supprimer l'ancienne base de données et le dossier de migrations
run_command('del instance\\prorga.db')
run_command('rmdir /S /Q migrations')

# Initialiser et appliquer les nouvelles migrations
run_command('python manage.py db init')
run_command('python manage.py db migrate -m "Initial migration"')
run_command('python manage.py db upgrade')


print( "reset_bd : RAS")