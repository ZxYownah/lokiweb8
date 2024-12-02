import mysql.connector

def verify_import(db_name, db_user, db_pass):
    """
    Verify the content of a database by listing its tables.

    Args:
    db_name (str): Name of the database to verify.
    db_user (str): MySQL username.
    db_pass (str): MySQL password.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user=db_user,
            password=db_pass,
            database=db_name
        )
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print(f"Tables in database '{db_name}':")
        for table in tables:
            print(table[0])
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if connection.is_connected():
            connection.close()

# Utilisation
verify_import(
    db_name="DB2_edukateyownah",
    db_user="talla",
    db_pass="talla1507"
)
