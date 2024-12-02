import mysql.connector

# Database configuration
DB_HOST = "localhost"
DB_USER = "talla"
DB_PASSWORD = "talla1507"
DB_NAME = "DB2_edukateyownah"


def create_admins_table():
    try:
        # Connect to the database
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Create the 'admins' table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                admin_login VARCHAR(100) NOT NULL,
                admin_password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        print("Table 'admins' created or already exists.")

        # Insert data into the 'admins' table
        admins_data = [
            ("admin1", "hashed_password1"),
            ("admin2", "hashed_password2")
        ]
        cursor.executemany(
            "INSERT INTO admins (admin_login, admin_password) VALUES (%s, %s)",
            admins_data
        )
        print("Data inserted into 'admins' table.")

        # Commit changes
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")


if __name__ == "__main__":
    create_admins_table()
