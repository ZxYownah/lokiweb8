import os
import subprocess

def create_database(db_name, db_user, db_pass):
    """
    Crée une base de données si elle n'existe pas.
    """
    try:
        command = [
            "mysql",
            "-u", db_user,
            f"-p{db_pass}",
            "-e", f"CREATE DATABASE IF NOT EXISTS {db_name};"
        ]
        subprocess.run(command, check=True)
        print(f"Database '{db_name}' created successfully (or already exists).")
    except subprocess.CalledProcessError as e:
        print(f"Error creating database: {e}")

def import_database(import_path, db_name, db_user, db_pass):
    """
    Importe les données dans une base de données existante.
    """
    try:
        command = [
            "mysql",
            "-u", db_user,
            f"-p{db_pass}",
            db_name
        ]
        with open(import_path, "r") as input_file:
            subprocess.run(command, stdin=input_file, check=True)
        print(f"Import successful: {import_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during import: {e}")

""""""""""""""""""""""""""""""""""""""""""
# Spécifiez ici le nom du fichier à importer
import_filename = "exportDB212020947.sql"

# Obtenez le chemin du script en cours d'exécution
script_dir = os.path.dirname(os.path.abspath(__file__))

# Définissez import_path pour qu'il soit dans le même répertoire que le script
import_path = os.path.join(script_dir, import_filename)

""""""""""""""""""""""""""""""""""""""""""
# Nom de la nouvelle base de données
db_name = "DB2_edukateyownah"

# Appel des fonctions
create_database(
    db_name=db_name,
    db_user="talla",
    db_pass="talla1507"
)

import_database(
    import_path=import_path,
    db_name=db_name,
    db_user="talla",
    db_pass="talla1507"
)
