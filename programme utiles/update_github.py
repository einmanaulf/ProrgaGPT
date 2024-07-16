import os
import subprocess


def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Command failed: {command}\nError: {stderr.decode('utf-8')}")
    return stdout.decode('utf-8')


def update_github_project(repo_path):
    os.chdir(repo_path)

    print("Adding changes...")
    run_command('git add .')

    print("Committing changes...")
    commit_message = "Mise à jour automatique du projet"
    run_command(f'git commit -m "{commit_message}"')

    print("Pulling latest changes from remote...")
    run_command('git pull origin main --rebase')

    print("Pushing changes to remote...")
    run_command('git push origin main')

    print("Project updated successfully!")


if __name__ == "__main__":
    # Define the path to your repository
    repo_path = "C:/Users/Utilisateur/PycharmProjects/ProrgaGPT"

    try:
        update_github_project(repo_path)
    except Exception as e:
        print(f"An error occurred: {e}")
