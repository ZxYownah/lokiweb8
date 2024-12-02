import mysql.connector
from mysql.connector import Error


def delete_database(database_name, host="localhost", user="talla", password="talla1507"):
    """
    Supprime une base de données spécifique dans MySQL.

    Args:
        database_name (str): Nom de la base de données à supprimer.
        host (str): Adresse du serveur MySQL (par défaut "localhost").
        user (str): Nom d'utilisateur MySQL (par défaut "root").
        password (str): Mot de passe MySQL.

    Returns:
        str: Résultat de l'opération.
    """
    try:
        # Connexion au serveur MySQL
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )

        if connection.is_connected():
            cursor = connection.cursor()
            # Commande pour supprimer la base de données
            cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")
            print(f"La base de données '{database_name}' a été supprimée avec succès.")
            return f"Database '{database_name}' deleted successfully."

    except Error as e:
        print(f"Erreur lors de la suppression de la base de données : {e}")
        return str(e)

    finally:
        # Fermer la connexion
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connexion au serveur MySQL fermée.")


# Utilisation
if __name__ == "__main__":
    result = delete_database("DB1_test", host="localhost", user="talla", password="talla1507")
    print(result)
