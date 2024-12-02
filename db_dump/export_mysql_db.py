import os
import subprocess

# Fonction d'exportation
def export_database(export_path, db_name, db_user, db_pass):
    try:
        command = [
            "mysqldump",
            "-u", db_user,
            f"-p{db_pass}",
            db_name
        ]
        with open(export_path, "w") as output_file:
            subprocess.run(command, stdout=output_file, check=True)
        print(f"Export successful: {export_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during export: {e}")

# Spécifiez ici le nom du fichier
export_filename = "exportDB212020947.sql"

# Obtenez le chemin du script en cours d'exécution
script_dir = os.path.dirname(os.path.abspath(__file__))

# Définissez export_path pour qu'il soit dans le même répertoire que le script
export_path = os.path.join(script_dir, export_filename)

# Appel de la fonction d'exportation
export_database(
    export_path=export_path,
    db_name="DB2_edukateyownah",
    db_user="talla",
    db_pass="talla1507"
)
