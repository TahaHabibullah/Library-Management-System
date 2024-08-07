import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

def register_librarian(conn):
    cursor = conn.cursor()
    print("Let's register a new librarian.")
    print()
    validSSN = False
    ssn = None
    while not validSSN:
        ssn = input("Enter your social security number (SSN): ")
        if ssn.isnumeric():
            if len(ssn) == 9:
                cursor.execute("SELECT ssn FROM librarian WHERE ssn = %s", (ssn,))
                ssnExists = cursor.fetchall()
                if not ssnExists:
                    validSSN = True
                else:
                    print("ERROR: Duplicate SSN")
            else:
                print("ERROR: Make sure you enter 9 digits")
        else:
            print("ERROR: Only enter numeric values")
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    if not check_email(email):
        validEmail = False
        print("ERROR: Only enter valid emails")
        while not validEmail:
            email = input("Please enter your email: ")
            if check_email(email):
                validEmail = True
            else:
                print("ERROR: Only enter valid emails")
    password = input("Enter your password: ")
    salary = None
    validSalary = False
    while not validSalary:
        salary = input("Enter your salary: ")
        if salary.isnumeric():
            validSalary = True
        else:
            print("ERROR: Only enter numeric values")
    cursor.execute("INSERT INTO librarian (ssn, name, email, password, salary) VALUES (%s, %s, %s, %s, %s)", 
                    (ssn, name, email, password, salary,))
    conn.commit()
    cursor.close()
    print("Successfully registered librarian!")

def check_email(email):
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

class Librarian:
    def __init__(self, email, password, ssn, name, salary, conn):
        self.email = email
        self.password = password
        self.ssn = ssn
        self.name = name
        self.salary = salary
        self.conn = conn

    def insert_document(self, document_type, edoc, attributes, copies=0):
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(document_id) FROM document;")
        document_id = cursor.fetchone()[0]
        if document_id is None:
            document_id = 0
        else:
            document_id+=1
        cursor.execute("INSERT INTO document (document_id, copies, edoc, document_type) VALUES (%s, %s, %s, %s)",
                    (document_id, copies, edoc, document_type))

        if document_type == "book":
            isbn, title, authors, publisher, edition, year, pages = attributes
            cursor.execute("INSERT INTO book (id, isbn, title, authors, publisher, edition, year, pages) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (document_id, isbn, title, authors, publisher, edition, year, pages))
        elif document_type == "magazine":
            isbn, title, publisher, year, month = attributes
            cursor.execute("INSERT INTO magazine (id, isbn, title, publisher, year, month) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (document_id, isbn, title, publisher, year, month))
        elif document_type == "journal":
            name, title, authors, publisher, year, issue, num_issue = attributes
            cursor.execute("INSERT INTO journal_article (id, name, title, authors, publisher, year, issue, num_issue) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (document_id, name, title, authors, publisher, year, issue, num_issue))

        self.conn.commit()
        cursor.close()

    def insert_new_document(self):
        docType = False
        while not docType:
            document_type = input("What type of document? (book, magazine, journal): ")
            if document_type == "book" or document_type == "magazine" or document_type == "journal":
                docType = True
            else:
                print("ERROR: Type in a valid type")
        document_type = document_type.lower()
        ynValid = False
        while not ynValid:
            edoc = input("Is this an electronic document? (y/n): ")
            if edoc == "y" or edoc == "n":
                ynValid = True
            else:
                print("ERROR: Only type 'y' or 'n'")
        edoc = edoc.lower()
        if edoc == 'y':
            edoc = True
        elif edoc == 'n':
            edoc = False
        if document_type == "book":
            if not edoc:
                copyValid = False
                while not copyValid:
                    copies = input("How many copies of this document are on hand: ")
                    if copies.isnumeric():
                        copyValid = True
                    else:
                        print("ERROR: Only type numeric values for copies")

            print("Enter book information in the following format: isbn:title:authors:publisher:edition:year:pages")
            line = input()
            temp = line.split(":")
            attributes = tuple(temp)
            if edoc:
                self.insert_document(document_type, edoc, attributes)
            else:
                self.insert_document(document_type, edoc, attributes, copies)

        elif document_type == "magazine":
            if not edoc:
                copyValid = False
                while not copyValid:
                    copies = input("How many copies of this document are on hand: ")
                    if copies.isnumeric():
                        copyValid = True
                    else:
                        print("ERROR: Only type numeric values for copies")

            print("Enter book information in the following format: isbn:title:publisher:year:month")
            line = input()
            temp = line.split(":")
            attributes = tuple(temp)
            if edoc:
                self.insert_document(document_type, edoc, attributes)
            else:
                self.insert_document(document_type, edoc, attributes, copies)

        elif document_type == "journal":
            if not edoc:
                copyValid = False
                while not copyValid:
                    copies = input("How many copies of this document are on hand: ")
                    if copies.isnumeric():
                        copyValid = True
                    else:
                        print("ERROR: Only type numeric values for copies")

            print("Enter book information in the following format: name:title:authors:publisher:year:issue:num_issue")
            line = input()
            temp = line.split(":")
            attributes = tuple(temp)
            if edoc:
                self.insert_document(document_type, edoc, attributes)
            else:
                self.insert_document(document_type, edoc, attributes, copies)

    def update_document(self, id, document_type, attributes):
        cursor = self.conn.cursor()
        values = []
        
        if document_type == "book":
            query = "UPDATE book SET"
            isbn, title, authors, publisher, edition, year, pages = attributes
            if isbn != '_':
                query += " isbn = %s,"
                values.append(isbn)
            if title != '_':
                query += " title = %s,"
                values.append(title)
            if authors != '_':
                query += " authors = %s,"
                values.append(authors)
            if publisher != '_':
                query += " publisher = %s,"
                values.append(publisher)
            if edition != '_':
                query += " edition = %s,"
                values.append(edition)
            if year != '_':
                query += " year = %s,"
                values.append(year)
            if pages != '_':
                query += " isbn = %s,"
                values.append(pages)
        elif document_type == "magazine":
            query = "UPDATE magazine SET"
            isbn, title, publisher, year, month = attributes
            if isbn != '_':
                query += " isbn = %s,"
                values.append(isbn)
            if title != '_':
                query += " title = %s,"
                values.append(title)
            if publisher != '_':
                query += " publisher = %s,"
                values.append(publisher)
            if year != '_':
                query += " year = %s,"
                values.append(year)
            if month != '_':
                query += " month = %s,"
                values.append(month)
        elif document_type == "journal":
            query = "UPDATE journal_article SET"
            name, title, authors, publisher, year, issue, num_issue = attributes
            if name != '_':
                query += " isbn = %s,"
                values.append(name)
            if title != '_':
                query += " title = %s,"
                values.append(title)
            if authors != '_':
                query += " authors = %s,"
                values.append(authors)
            if publisher != '_':
                query += " publisher = %s,"
                values.append(publisher)
            if year != '_':
                query += " year = %s,"
                values.append(year)
            if issue != '_':
                query += " issue = %s,"
                values.append(issue)
            if num_issue != '_':
                query += " num_issue = %s,"
                values.append(num_issue)

        query = query[:-1]
        query += " WHERE id = %s"
        values.append(id)
        cursor.execute(query, tuple(values))
        self.conn.commit()
        cursor.close()

    def update_existing_document(self):
        docValid = False
        while not docValid:
            document_id = input("Enter the id of the document you would like to update: ")
            if document_id.isnumeric():
                docValid = True
            else:
                print("ERROR: Only enter numeric values")
        cursor = self.conn.cursor()
        cursor.execute("SELECT document_type FROM document WHERE document_id = %s", (document_id,))
        temp = cursor.fetchone()
        if temp is None:
            print("Document does not exist")
        else:
            document_type = temp[0]
            if document_type == "book":
                print("Enter the updated book info in the following format: isbn:title:authors:publisher:edition:year:pages")
            if document_type == "magazine":
                print("Enter the updated magazine info in the following format: isbn:title:publisher:year:month")
            if document_type == "journal":
                print("Enter the updated journal info in the following format: name:title:authors:publisher:year:issue:num_issue")

            print("Any fields that do not need to be updated should be filled in with an underscore: _")
            line = input()
            temp = line.split(":")
            attributes = tuple(temp)
            self.update_document(document_id, document_type, attributes)

    def change_copies(self):
        validCopy = False
        while not validCopy:
            document_id = input("Enter the id of the document to change copies of: ")
            if document_id.isnumeric():
                validCopy = True
            else:
                print("ERROR: Only enter numeric values")
        cursor = self.conn.cursor()
        cursor.execute("SELECT edoc, document_type FROM document WHERE document_id = %s", (document_id,))
        details = cursor.fetchone()
        if details is None:
            print("Document does not exist")
        else:
            edoc = details[0]
            document_type = details[1]
            if not edoc:
                copies = input("Enter the updated number of copies: ")
                validCopies = False
                while not validCopies:
                    if copies.isnumeric():
                        if int(copies) >= 0:
                            cursor.execute("UPDATE document SET copies = %s WHERE document_id = %s", (copies, document_id))
                            self.conn.commit()
                            print("Copies updated.")
                            validCopies = True
                        else:
                            print("ERROR: Number of copies must be 0 or more.")
                            copies = input("Enter the updated number of copies: ")
                    else:
                        print("ERROR: Please enter only numbers above or equal to 0.")
                        copies = input("Enter the updated number of copies: ")
            else:
                print("You cannot change the number of copies of an edoc.")
        cursor.close()


    def register_client(self, name, email, password, addresses, credit_cards, fees=0):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO client (name, email, password, fees) VALUES (%s, %s, %s, %s)", 
                    (name, email, password, fees))

        for address in addresses:
            cursor.execute("INSERT INTO address (client_email, client_address) VALUES (%s, %s)",
                        (email, address))

        for card in credit_cards:
            card_number, expiry_date, payment_address = card
            cursor.execute("INSERT INTO credit_card (client_email, card_number, expiry_date, payment_address) VALUES (%s, %s, %s, %s)",
                        (email, card_number, expiry_date, payment_address))

        self.conn.commit()
        cursor.close()
        print("Client registered!")

    def get_client_info(self):
        print("Let's start registering your client!")
        name = input("Enter the client's name: ")
        email = input("Enter the client's email: ")
        if not check_email(email):
            validEmail = False
            print("ERROR: Only enter valid emails")
            while not validEmail:
                email = input("Please enter your email: ")
                if check_email(email):
                    validEmail = True
                else:
                    print("ERROR: Only enter valid emails")

        password = input("Enter the client's password: ")
        print("Enter the client's address, if there are multiple addresses, use the format firstaddress:secondaddress:...")
        validAddress = False
        addresses = None
        while not validAddress:
            line = input()
            if not line:
                print("ERROR: Enter 1 or more addresses")
            else:
                validAddress = True
        addresses = line.split(":")
        print("Enter the client's card, use the format cardnumber:yyyy-mm-dd:payment_address")
        print("If there are multiple credit cards, use the format card1#card2")
        validCard = False
        line = None
        cards = []
        while not validCard:
            line = input()
            cards = []
            validCard = False
            validPaymentAddr = True
            if not line:
                print("ERROR: Enter 1 or more cards")
            else:
                temp = line.split("#")
                for i in temp:
                    card = i.split(":")
                    if card[2] not in addresses:
                        print("ERROR: Payment address must be one of client's current addresses.")
                        validPaymentAddr = False
                        break
                    else:
                        cards.append(tuple(card))
                if not validPaymentAddr:
                    validCard = False
                else:
                    validCard = True
        
        return name, email, password, addresses, cards

    def update_client(self, email, name=None, addresses=None, credit_cards=None, fees=None):
        cursor = self.conn.cursor()
        if name is not None:
            cursor.execute("UPDATE client SET name = %s WHERE email = %s", (name, email))

        if fees is not None:
            cursor.execute("UPDATE client SET fees = %s WHERE email = %s", (fees, email))

        if addresses is not None:
            cursor.execute("DELETE FROM address WHERE client_email = %s", (email,))
            for address in addresses:
                cursor.execute("INSERT INTO address (client_email, client_address) VALUES (%s, %s)",
                            (email, address))
            
        if credit_cards is not None:
            cursor.execute("DELETE FROM credit_card WHERE client_email = %s", (email,))
            for card in credit_cards:
                card_number, expiry_date, payment_address = card
                cursor.execute("INSERT INTO credit_card (client_email, card_number, expiry_date, payment_address) VALUES (%s, %s, %s, %s)",
                            (email, card_number, expiry_date, payment_address))
        
        self.conn.commit()
        cursor.close()
        print("Client updated!")

    def get_updated_info(self):
        print("For any info that doesn't need to be updated, input an underscore '_'")
        name = input("Enter the client's updated name: ")
        if name == "_":
            name = None

        feeValid = False
        while not feeValid:
            fees = input("Enter the client's updated overdue fees: ")
            if fees == "_":
                fees = None
                feeValid = True
            elif fees.isnumeric():
                feeValid = True
            else:
                print("ERROR: Only enter numeric values")
        print("Enter the client's updated addresses, if there are multiple addresses, use the format firstaddress:secondaddress:...")
        line = input()
        if line != "_":
            addresses = line.split(":")
        else:
            addresses = None

        print("Enter the client's updated cards, use the format cardnumber:yyyy-mm-dd:payment_address")
        print("If there are multiple credit cards, use the format card1#card2")
        line = input()
        if line != "_":
            temp = line.split("#")
            cards = []
            for i in temp:
                card = i.split(":")
                cards.append(tuple(card))
        else:
            cards = None
        return name, addresses, cards, fees

    def delete_client(self, email):
        cursor = self.conn.cursor()
        cursor.execute("SELECT fees FROM client WHERE email = %s", (email,))
        fees = cursor.fetchone()[0]
        if fees > 0:
            print("ERROR: You may not delete a client that has outstanding overdue fees")
        else:
            cursor.execute("DELETE FROM credit_card WHERE client_email = %s", (email,))
            cursor.execute("DELETE FROM address WHERE client_email = %s", (email,))
            cursor.execute("DELETE FROM client WHERE email = %s", (email,))
            self.conn.commit()
            print("Client deleted!")
        cursor.close()

    def manage_documents(self):
        valid = False
        while valid == False:
            print()
            print("[1] Insert New Document")
            print("[2] Update Existing Document")
            print("[3] Change Copies")
            print("[4] Go Back")
            choice = input("Enter the number of what you'd like to do: ")
            print()
            if choice == "1":
                self.insert_new_document()
                self.manage_documents()
                valid = True
            elif choice == "2":
                self.update_existing_document()
                self.manage_documents()
                valid = True
            elif choice == "3":
                self.change_copies()
                self.manage_documents()
                valid = True
            elif choice == "4":
                valid = True
                self.librarian_menu()
            else:
                print("ERROR: Not a choice. Choose again.")     

    def manage_clients(self):
        valid = False
        while valid == False:
            print()
            print("[1] Register New Client")
            print("[2] Update Client Info")
            print("[3] Delete Client")
            print("[4] Go Back")
            choice = input("Enter the number of what you'd like to do: ")
            print()
            if choice == "1":
                name, email, password, addresses, cards = self.get_client_info()
                self.register_client(name, email, password, addresses, cards)
                self.manage_clients()
                valid = True
            elif choice == "2":
                email = input("Enter email of client to be updated: ")
                if not check_email(email):
                    validEmail = False
                    print("ERROR: Only enter valid emails")
                    while not validEmail:
                        email = input("Please enter your email: ")
                        if check_email(email):
                            validEmail = True
                        else:
                            print("ERROR: Only enter valid emails")
                name, addresses, cards, fees = self.get_updated_info()
                self.update_client(email, name, addresses, cards, fees)
                self.manage_clients()
                valid = True
            elif choice == "3":
                email = input("Enter email of client to be deleted: ")
                if not check_email(email):
                    validEmail = False
                    print("ERROR: Only enter valid emails")
                    while not validEmail:
                        email = input("Please enter your email: ")
                        if check_email(email):
                            validEmail = True
                        else:
                            print("ERROR: Only enter valid emails")
                self.delete_client(email)
                self.manage_clients()
                valid = True
            elif choice == "4":
                valid = True
                self.librarian_menu()
            else:
                print("ERROR: Not a choice. Choose again.") 

    def librarian_menu(self):
        valid = False
        while valid == False:
            print()
            print("[1] Manage Documents")
            print("[2] Manage Clients")
            print("[3] Register Librarian")
            print("[4] Exit")
            choice = input("Enter the number of what you'd like to do: ")
            print()
            if choice == "1":
                self.manage_documents()
                valid = True
            elif choice == "2":
                self.manage_clients()
                valid = True
            elif choice == "3":
                register_librarian(self.conn)
                self.librarian_menu()
                valid = True
            elif choice == "4":
                print()
                print("Exiting...")
                exit()
            else:
                print("ERROR: Not a choice. Choose again.")