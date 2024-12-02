import os
import subprocess


def rename_database(old_db_name, new_db_name, db_user, db_pass):
    try:
        # Step 1: Export the old database
        dump_file = f"{old_db_name}.sql"
        export_command = f"mysqldump -u {db_user} -p{db_pass} {old_db_name} > {dump_file}"
        subprocess.run(export_command, shell=True, check=True)
        print(f"Backup created: {dump_file}")

        # Step 2: Create the new database
        create_db_command = f"mysql -u {db_user} -p{db_pass} -e 'CREATE DATABASE {new_db_name}'"
        subprocess.run(create_db_command, shell=True, check=True)
        print(f"New database created: {new_db_name}")

        # Step 3: Import data into the new database
        import_command = f"mysql -u {db_user} -p{db_pass} {new_db_name} < {dump_file}"
        subprocess.run(import_command, shell=True, check=True)
        print(f"Data imported into: {new_db_name}")

        # Step 4: Drop the old database
        drop_db_command = f"mysql -u {db_user} -p{db_pass} -e 'DROP DATABASE {old_db_name}'"
        subprocess.run(drop_db_command, shell=True, check=True)
        print(f"Old database deleted: {old_db_name}")

        # Clean up the dump file
        os.remove(dump_file)
        print("Temporary dump file removed.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


# Usage
rename_database("DB1_prime_edukateyownah", "DB1_test", "talla", "talla1507")
