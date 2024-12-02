import os
import sys
import json
import time
import argparse
import threading
from queue import Queue
from http.server import HTTPServer, BaseHTTPRequestHandler
import mimetypes
from socketserver import ThreadingMixIn
from termcolor import colored
import mysql.connector
import uuid

VERSION = "v0.0.0"
BANNER = """ 

    __       ____     __ __    ____   _       __   ______   ____     _____
   / /      / __ \   / //_/   /  _/  | |     / /  / ____/  / __ )   / ___/
  / /      / / / /  / ,<      / /    | | /| / /  / __/    / __  |   \__ \ 
 / /___   / /_/ /  / /| |   _/ /     | |/ |/ /  / /___   / /_/ /   ___/ / 
/_____/   \____/  /_/ |_|  /___/     |__/|__/  /_____/  /_____/   /____/ 

"""


class CustomHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        code, headers, data = self.server.manager.on_GET(self.path, self.headers)
        if code != 200:
            self.server.manager.send_error(self, code, headers, data)
        else:
            self.server.manager.send_success_response(self, data, headers)

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) if 'Content-Length' in self.headers else 0
        post_data = self.rfile.read(content_length)
        code, headers, data = self.server.manager.on_POST(self.path, self.headers, post_data)
        if code != 200:
            self.server.manager.send_error(self, code, headers, data)
        else:
            self.server.manager.send_success_response(self, data, headers)


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class ServerManager:

    def __init__(self, config):
        self.config = config
        self.servers = []
        self.loggers = []
        self.sessions = {}  # Store active sessions
        self.doc_root = os.path.expanduser(config['servers'][0]['doc_root'])  # Expand ~ to home directory
        self.setup_loggers()

    def setup_loggers(self):
        for logger_name, logger_config in self.config['loggers'].items():
            if logger_config['active']:
                self.loggers.append(logger_name)

    def start_servers(self):
        for server_config in self.config['servers']:
            port = server_config['port']
            server_address = ('', port)
            server = ThreadingHTTPServer(server_address, CustomHTTPRequestHandler)
            server.manager = self
            print(colored(f"Starting server on port {port}", "green"))
            server.timeout = server_config.get('timeout', 10)
            self.servers.append(server)
            # Utilisation de `threading.Thread` pour démarrer le serveur
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.start()

    def send_error(self, handler, code, headers, message):
        try:
            handler.send_response(code)
            for header, value in headers:
                handler.send_header(header, value)
            handler.end_headers()

            # Ensure the message is written as bytes
            if isinstance(message, str):
                handler.wfile.write(message.encode('utf-8'))  # Encode if it's a string
            else:
                handler.wfile.write(message)  # Write directly if it's already bytes
        except BrokenPipeError:
            print("Client disconnected before receiving the full response.")

    def send_success_response(self, handler, data, headers):
        try:
            handler.send_response(200)
            for header, value in headers:
                handler.send_header(header, value)
            handler.end_headers()

            # Ensure the data is written as bytes
            if isinstance(data, str):
                handler.wfile.write(data.encode('utf-8'))  # Encode string to bytes
            else:
                handler.wfile.write(data)  # Write directly if already bytes
        except BrokenPipeError:
            print("Client disconnected before receiving the full response.")

    def on_request(self, handler):
        if not handler.path.startswith("/"):
            return 400, [("Connection", "close")], "Bad Request"
        return None, None

    def on_GET(self, path, headers):
        # Check if the path is the search endpoint
        if path.startswith("/search"):
            from urllib.parse import parse_qs, urlparse
            query_params = parse_qs(urlparse(path).query)
            keyword = query_params.get("keyword", [""])[0]  # Default to empty string if no keyword

            try:
                # Connexion à la base de données
                connection = mysql.connector.connect(
                    host="localhost",
                    user="talla",
                    password="talla1507",
                    database="DB2_edukateyownah"
                )
                cursor = connection.cursor(dictionary=True)

                # Vulnérabilité : Injection SQL directe
                # Le mot-clé est inséré directement dans la requête sans être paramétré correctement.
                query = f"""
                    SELECT title, description, image_url
                    FROM courses
                    WHERE title LIKE '%{keyword}%' OR description LIKE '%{keyword}%'
                """

                # Commentaire : Si `keyword` contient une entrée malveillante comme `' OR '1'='1`,
                # cela rend la clause WHERE toujours vraie et retourne toutes les lignes.
                cursor.execute(query)
                results = cursor.fetchall()
                connection.close()

                # Génération des cartes de cours (2 par ligne)
                course_html = ""
                for i, course in enumerate(results):
                    if i % 2 == 0:  # Démarrer une nouvelle ligne chaque deux cours
                        if i > 0:
                            course_html += "</div>"  # Fermer la ligne précédente
                        course_html += '<div class="row">'
                    course_html += f"""
                        <div class="col-md-6 mb-4">
                            <div class="card">
                                <img src="{course['image_url']}" class="card-img-top" alt="{course['title']}" style="height: 200px; object-fit: cover;">
                                <div class="card-body">
                                    <h5 class="card-title">{course['title']}</h5>
                                    <p class="card-text">{course['description']}</p>
                                </div>
                            </div>
                        </div>
                    """
                if results:
                    course_html += "</div>"  # Fermer la dernière ligne

                # Lire le fichier index.html
                full_path = os.path.join(self.doc_root, "index.html")
                if os.path.isfile(full_path):
                    with open(full_path, "r") as file:
                        index_html = file.read()

                    # Injecter les résultats de la recherche dans le placeholder
                    search_results_section = f"""
                    <div id="search-results" class="container py-5">
                        <h2 class="text-center mb-4">Search Results for: {keyword}</h2>
                        <div class="row" id="search-results-container">
                            {course_html if results else "<p>No courses found.</p>"}
                        </div>
                    </div>
                    """
                    modified_html = index_html.replace(
                        '<div id="search-results" class="container py-5" style="display: none;">',
                        search_results_section
                    )

                    return 200, [("Content-Type", "text/html")], modified_html.encode("utf-8")

            except mysql.connector.Error as err:
                return 500, [("Content-Type", "text/html")], f"<html><body><p>Error: {err}</p></body></html>".encode(
                    "utf-8"
                )

        # Session check logic
        if path == "/check_session":
            # Check if the session cookie is present
            cookie_header = headers.get("Cookie")

            if cookie_header:
                try:
                    # Parse cookies from the Cookie header
                    cookies = {}
                    for cookie in cookie_header.split("; "):
                        key, value = cookie.split("=", 1)  # Split only on the first "=" to extract key-value pairs
                        cookies[key] = value

                    # Retrieve the session token from the parsed cookies
                    session_token = cookies.get("session")

                    # Check if the session token exists in the server's session store
                    user = self.sessions.get(session_token)

                    if user:
                        # If a valid session exists, return a response with the user's email
                        return 200, [("Content-Type", "application/json")], json.dumps(
                            {"loggedIn": True, "email": user["email"]}
                        ).encode("utf-8")

                except ValueError as e:
                    # Handle cases where cookies are not properly formatted
                    print(f"Error parsing cookies: {e}")

                except Exception as e:
                    # General exception handling for unexpected errors
                    print(f"Unexpected error while checking session: {e}")

            # If no valid session or cookie is found, return a response indicating the user is not logged in
            return 200, [("Content-Type", "application/json")], json.dumps(
                {"loggedIn": False}
            ).encode("utf-8")

        # Administration page
        if path == "/admin":
            full_path = os.path.join(self.doc_root, "admin.html")
            if os.path.isfile(full_path):
                mime_type, _ = mimetypes.guess_type(full_path)
                with open(full_path, "rb") as file:
                    data = file.read()
                return 200, [("Content-Type", mime_type)], data
            else:
                return 404, [("Content-Type", "text/html")], b"<html><body>Admin Page Not Found</body></html>"

        # Map root path '/' to 'index.html' by default
        if path == "/":
            path = "/index.html"

        # Construct full file path
        full_path = os.path.join(self.doc_root, path.lstrip("/"))

        # Serve the file if it exists
        if os.path.isfile(full_path):
            mime_type, _ = mimetypes.guess_type(full_path)
            mime_type = mime_type or "application/octet-stream"  # Default MIME type if unknown
            with open(full_path, "rb") as file:
                data = file.read()
            return 200, [("Content-Type", mime_type)], data
        else:
            # File not found
            return 404, [("Content-Type", "text/html")], b"<html><body>Page Not Found</body></html>"

    """             INITIAL ON POST
        def on_POST(self, path, headers, post_data):
        return 200, [("Content-Type", "text/html")], "<html><body>POST data received</body></html>"
    """

    ###

    def on_POST(self, path, headers, post_data):
        # Handle registration requests
        if path == "/register":
            try:
                # Parse JSON data from the request body
                data = json.loads(post_data)
                username = data.get("username")
                email = data.get("email")
                password = data.get("password")
                role = data.get("role", "student")

                # Validate the role
                if role not in ["student", "instructor"]:
                    return 400, [("Content-Type", "application/json")], json.dumps(
                        {"message": "Invalid role"}
                    ).encode("utf-8")

                # Insert the user into the database
                connection = mysql.connector.connect(
                    host="localhost",
                    user="talla",
                    password="talla1507",
                    database="DB2_edukateyownah"
                )
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                    (username, email, password, role)
                )
                connection.commit()
                connection.close()

                # Success response
                return 201, [("Content-Type", "application/json")], json.dumps(
                    {"message": "User registered successfully"}
                ).encode("utf-8")
            except mysql.connector.Error as err:
                return 500, [("Content-Type", "application/json")], json.dumps(
                    {"message": f"Database error: {err}"}
                ).encode("utf-8")
            except Exception as e:
                return 400, [("Content-Type", "application/json")], json.dumps(
                    {"message": f"Error: {e}"}
                ).encode("utf-8")

        # Handle login requests
        elif path == "/login":
            try:
                # Parse JSON data from the request body
                data = json.loads(post_data)
                email = data.get("email")
                password = data.get("password")

                # Check credentials in the database
                connection = mysql.connector.connect(
                    host="localhost",
                    user="talla",
                    password="talla1507",
                    database="DB2_edukateyownah"
                )
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
                user = cursor.fetchone()
                connection.close()

                if user:
                    # Generate a session token
                    import uuid
                    session_token = str(uuid.uuid4())
                    self.sessions[session_token] = user

                    # Set session cookie in the response
                    headers = [
                        ("Content-Type", "application/json"),
                        ("Set-Cookie", f"session={session_token}; Path=/")
                    ]
                    return 200, headers, json.dumps({"message": "Login successful"}).encode("utf-8")
                else:
                    # Invalid credentials
                    return 401, [("Content-Type", "application/json")], json.dumps(
                        {"message": "Invalid credentials"}
                    ).encode("utf-8")
            except Exception as e:
                return 500, [("Content-Type", "application/json")], json.dumps(
                    {"message": str(e)}
                ).encode("utf-8")

        # Handle logout requests
        elif path == "/logout":
            try:
                # Parse session token from the cookie header
                cookie_header = headers.get("Cookie")
                if cookie_header:
                    cookies = {}
                    for cookie in cookie_header.split("; "):
                        key, value = cookie.split("=", 1)  # Split only on the first "="
                        cookies[key] = value
                    session_token = cookies.get("session")

                    if session_token and session_token in self.sessions:
                        # Remove the session
                        del self.sessions[session_token]

                # Return logout success response
                return 200, [("Content-Type", "application/json")], json.dumps(
                    {"message": "Logged out successfully"}
                ).encode("utf-8")
            except Exception as e:
                return 500, [("Content-Type", "application/json")], json.dumps(
                    {"message": str(e)}
                ).encode("utf-8")

        # Handle admin login on the admin page
        elif path == "/admin/login":
            try:
                from urllib.parse import parse_qs
                post_data = parse_qs(post_data.decode("utf-8"))
                admin_login = post_data.get("admin_login", [""])[0]
                admin_password = post_data.get("admin_password", [""])[0]

                # Connexion vulnérable : requête SQL non paramétrée
                connection = mysql.connector.connect(
                    host="localhost",
                    user="talla",
                    password="talla1507",
                    database="DB2_edukateyownah"
                )
                cursor = connection.cursor(dictionary=True)

                # Requête SQL vulnérable
                query = f"SELECT * FROM admins WHERE admin_login = '{admin_login}' AND admin_password = '{admin_password}'".split('--')[0]

                print("Executing query:", query)  # Debug pour voir la requête générée
                cursor.execute(query)
                admin = cursor.fetchone()  # Récupérer la première ligne (ou None si aucun résultat)

                # IMPORTANT : Assurez-vous de libérer tous les résultats restants
                cursor.fetchall()  # Consomme tous les résultats restants (même s'ils ne sont pas utilisés)

                if admin:
                    # Récupérer les tables de la base de données pour affichage
                    cursor.execute("SHOW TABLES")
                    tables = cursor.fetchall()

                    all_data = {}
                    for table in tables:
                        table_name = list(table.values())[0]
                        cursor.execute(f"SELECT * FROM {table_name}")
                        rows = cursor.fetchall()
                        all_data[table_name] = rows

                    connection.close()

                    # Construction de la réponse HTML
                    html_content = "<h3>Content of the database:</h3>"
                    for table_name, rows in all_data.items():
                        html_content += f"<h4>Table: {table_name}</h4>"
                        if rows:
                            html_content += "<table border='1' style='width: 100%; border-collapse: collapse;'>"
                            html_content += "<tr>"
                            for column in rows[0].keys():
                                html_content += f"<th style='padding: 8px; background-color: #f2f2f2;'>{column}</th>"
                            html_content += "</tr>"
                            for row in rows:
                                html_content += "<tr>"
                                for cell in row.values():
                                    html_content += f"<td style='padding: 8px; text-align: center;'>{cell}</td>"
                                html_content += "</tr>"
                            html_content += "</table><br>"
                        else:
                            html_content += "<p>No data in this table.</p>"

                    return 200, [("Content-Type", "text/html")], html_content.encode("utf-8")
                else:
                    connection.close()
                    return 401, [("Content-Type", "application/json")], json.dumps(
                        {"message": "Invalid credentials"}
                    ).encode("utf-8")
            except Exception as e:
                return 500, [("Content-Type", "application/json")], json.dumps(
                    {"message": str(e)}
                ).encode("utf-8")






        # Default case for unrecognized POST paths
        else:
            return 404, [("Content-Type", "application/json")], json.dumps(
                {"message": "Endpoint not found"}
            ).encode("utf-8")

    ###

    def on_complete(self, client, code, req_headers, res_headers, request, response):
        print(f"Request from {client} completed with code {code}.")


if __name__ == '__main__':
    print(colored(BANNER, 'yellow'))
    print(f"Welcome to LokiWebS {VERSION}\n")

    parser = argparse.ArgumentParser(description='Start a custom HTTP server.')
    parser.add_argument('--config', help='Path to configuration file', required=True)
    args = parser.parse_args()

    config_path = args.config
    if not os.path.exists(config_path):
        print(colored("Configuration file not found.", "red"))
        sys.exit(1)

    with open(config_path, "r") as file:
        config = json.load(file)

    manager = ServerManager(config)
    manager.start_servers()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
