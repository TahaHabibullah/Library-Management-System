import psycopg2
from client import Client
from librarian import Librarian, register_librarian
import re
 
# Email expression
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

# Database connection
conn = psycopg2.connect(
    dbname="project",
    user="postgres",
    password="testing",
    host="localhost",
)

def check_email(email):
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

def check_librarian_exists():
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM librarian")
        librarians = cursor.fetchall()
        if librarians:
            cursor.close()
            return True
        else:
            cursor.close()
            return False

def librarian_login(email, password):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM librarian WHERE email = %s AND password = %s", (email, password))
    librarian = cursor.fetchone()
    cursor.close()
    return librarian

# Function for client login
def client_login(email, password):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM client WHERE email = %s AND password = %s", (email, password))
    cData = cursor.fetchone()
    cursor.close()
    return cData

def welcome_message():
    print("========================================================================")
    print("Welcome to the Library! Press (CTRL + C) if you need to quit at anytime.")
    print("========================================================================")

def main():
    welcome_message()
    user_type = input("Are you a client or a librarian? (Enter 'c' or 'l'): ").lower()
    curClient = None
    curLibrarian = None

    while user_type not in ("c", "l"):
        print("Invalid input. Please enter either 'c' or 'l'.")
        user_type = input("Are you a client or a librarian? (Enter 'c' or 'l'): ").lower()

    if user_type == "c":
        # Code for client actions
        print()
        print("Welcome, client!")
        logged_in = False
        while logged_in == False:
            client_email = input("Please enter your email: ")
            if not check_email(client_email):
                validEmail = False
                print("ERROR: Only enter valid emails")
                while not validEmail:
                    client_email = input("Please enter your email: ")
                    if check_email(client_email):
                        validEmail = True
                    else:
                        print("ERROR: Only enter valid emails")

            client_password = input("Please enter your password: ")
            print()
            cData = client_login(client_email, client_password)
            if cData:
                curClient = Client(cData[0], cData[2], cData[1], cData[3], conn)
                print("Welcome, Client:", curClient.name)
                logged_in = True
                curClient.client_menu()
            else:
                print("Invalid login credentials for client. Please try again.")

    else:  # Assuming the other valid option is 'librarian'
        if not check_librarian_exists():
            print("There seem to be no librarians on file.")
            register_librarian(conn)
        # Code for librarian actions
        print()
        print("Welcome, librarian!")
        logged_in = False
        while logged_in == False:
            librarian_email = input("Please enter your email: ")
            if not check_email(librarian_email):
                validEmail = False
                print("ERROR: Only enter valid emails")
                while not validEmail:
                    librarian_email = input("Please enter your email: ")
                    if check_email(librarian_email):
                        validEmail = True
                    else:
                        print("ERROR: Only enter valid emails")

            librarian_password = input("Please enter your password: ")
            print()
            lData = librarian_login(librarian_email, librarian_password)
            if lData:
                curLibrarian = Librarian(lData[2], lData[3], lData[0], lData[1], lData[4], conn)
                print("Welcome, librarian:", curLibrarian.name)
                logged_in = True
                curLibrarian.librarian_menu()
            else:
                print("Invalid login credentials for librarian. Please try again.")

    # Close the database connection
    conn.close()

main()