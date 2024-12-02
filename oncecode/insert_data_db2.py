import mysql.connector


def insert_data(table, columns, values):
    """
    Insert multiple rows into a specified table.

    Parameters:
    table (str): Table name
    columns (list): Column names
    values (list of tuples): Data to insert (one tuple per row)
    """
    connection = mysql.connector.connect(
        host="localhost",
        user="talla",
        password="talla1507",
        database="DB3_edukateyownah"
    )
    cursor = connection.cursor()
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    cursor.executemany(query, values)  # Use executemany to handle multiple rows
    connection.commit()
    connection.close()

if __name__ == "__main__":

    # USERS SAMPLE
    """
    table_u = "users"
    columns_u = ["username", "email", "password", "role"]
    values_u = [
        ("johndoe", "johndoe@example.com", "hashedpassword123", "student"),
        ("janedoe", "janedoe@example.com", "securepassword456", "instructor")
    ]
    """

    # COURSES SAMPLE
    """
    table_c = "courses"
    columns_c = ["title", "description", "image_url", "instructor_id"]
    values_c = [
        ("Web Design", "Learn the fundamentals of web design.", "img/courses-2.jpg", 3),
        ("Marketing", "Explore marketing strategies and tools.", "img/courses-3.jpg", 3),
        ("Research", "Master the art of conducting thorough research.", "img/courses-4.jpg", 3),
        ("SEO", "Understand and apply SEO best practices.", "img/courses-5.jpg", 3),
    ]
    """
    # From frontend to do later
    # ("Web Development", "Learn to build websites.", "img/courses-1.jpg", 1),
    # ("Data Science", "Data analysis and visualization.", "img/courses-2.jpg", 2),

    # INSTRUCTORS SAMPLE
    """
    table_i = "instructors"
    columns_i = ["name", "bio", "image_url"]
    values_i = [
        ("Jane Smith", "An experienced software developer and instructor", "https://example.com/images/jane.jpg"),
        ("John Doe", "Specialist in Python and Data Science", "https://example.com/images/john.jpg")
    ]
    """

    # ENROLLMENTS SAMPLE
    """
    table_e = "enrollments"
    columns_e = ["user_id", "course_id"]
    values_e = [
        (1, 1),  # User 1 (johndoe) enrolled in Course 1 (Python Programming)
        (1, 2)  # User 1 (johndoe) enrolled in Course 2 (Web Development)
    ]
    """

    # ADMINS SAMPLE
    table_a = "admins"
    columns_a = ["admin_login", "admin_password"]
    values_a = [
        ("admin1", "password123"),
        ("admin2", "password456"),
    ]

    # Uncomment the relevant section to insert data
    insert_data(table_a, columns_a, values_a)
    print("Data inserted successfully")
