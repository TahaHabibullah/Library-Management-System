from datetime import date, timedelta
import math

class Client:
    def __init__(self, email, password, name, overdue_fees, conn):
        self.email = email
        self.password = password
        self.name = name
        self.overdue_fees = overdue_fees
        self.conn = conn

    def borrow_document(self, email, document_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT copies, edoc FROM document WHERE document_id = %s", (document_id,))
        fetch = cursor.fetchone()
        copies = fetch[0]
        edoc = fetch[1]
        if copies > 0 or edoc:
            lent = date.today()
            due = lent + timedelta(weeks=4)
            cursor.execute("SELECT MAX(loan_id) FROM loan;")
            loan_id = cursor.fetchone()[0]
            if loan_id is None:
                loan_id = 0
            else:
                loan_id+=1
            cursor.execute("INSERT INTO loan (loan_id, document_id, client_email, date_lent, due_date) VALUES (%s, %s, %s, %s, %s)",
                        (loan_id, document_id, email, lent, due))
            print()
            print("Document successfully borrowed!")
            if not edoc:
                cursor.execute("UPDATE document SET copies = copies - 1 WHERE document_id = %s", (document_id))
        else:
            print()
            print("No more copies to lend")

        self.conn.commit()
        cursor.close()

    def return_loan(self, email, loan_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT document_id, due_date FROM loan where loan_id = %s AND client_email = %s", (loan_id, email))
        temp = cursor.fetchone()
        if not temp:
            print("ERROR: Loan ID does not exist.")
        else:
            document_id = temp[0]
            due = temp[1]
            today = date.today()
            cursor.execute("DELETE FROM loan WHERE loan_id = %s AND client_email = %s", (loan_id, email))
            cursor.execute("UPDATE document SET copies = copies + 1 WHERE document_id = %s", (document_id,))
            if today > due:
                diff = today - due
                print(diff.days)
                fee = 5 * math.floor(diff.days / 7)
                cursor.execute("UPDATE client SET fees = fees + %s WHERE email = %s", (fee, email))
            print("Successfully returned loan!")
            self.conn.commit()
            cursor.close()

    def print_loans(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT loan_id, document_id, date_lent, due_date FROM loan WHERE client_email = %s", (self.email,))
        loans = cursor.fetchall()
        print()
        print("Current Loans:")
        for loan in loans:
            print("Loan ID: " + str(loan[0]) + " Document ID: " + str(loan[1]) + " Date Lent: " + str(loan[2]) + " Due Date: " + str(loan[3]))

    def pay_fees(self, email, card_number):
        cursor = self.conn.cursor()
        cursor.execute("SELECT fees FROM client WHERE email = %s", (email,))
        fees = cursor.fetchone()[0]
        if fees > 0:
            cursor.execute("UPDATE credit_card SET charges =+ %s WHERE card_number = %s AND client_email = %s", (fees, card_number, email))
            cursor.execute("UPDATE client SET fees = 0 WHERE email = %s", (email,))
        else:
            print("All fees are already paid off")

        self.conn.commit()
        cursor.close()

    def add_payment_method(self, email, cards):
        cursor = self.conn.cursor()
        cursor.execute("SELECT client_address FROM address WHERE client_email = %s", (email,))
        addresses = cursor.fetchone()
        addresses = list(addresses)
        for card in cards:
            card_number, expiry_date, payment_address = card
            if payment_address not in addresses:
                print("ERROR: Payment address must be one of client's current addresses.")
                cursor.close()
                return False
            cursor.execute("INSERT INTO credit_card (client_email, card_number, expiry_date, payment_address) VALUES (%s, %s, %s, %s)",
                        (email, card_number, expiry_date, payment_address))
        self.conn.commit()
        cursor.close()
        return True

    def delete_payment_method(self, email, card_number):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM credit_card WHERE client_email = %s AND card_number = %s", (email, card_number))
        self.conn.commit()
        cursor.close()

    def add_payment_helper(self):
        print("Enter the new cards, use the format cardnumber:yyyy-mm-dd:payment_address")
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
        
        if self.add_payment_method(self.email, cards):
            print("Payment method added!")

    def delete_payment_helper(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM credit_card WHERE client_email = %s", (self.email,))
        num = cursor.fetchone()[0]
        if num == 1:
            print("ERROR: Client must have at least one payment method on file. Please add a new payment method before removing another.")
            cursor.close()
            return
        validNum = False
        while not validNum:
            cardNum = input("Please enter your card number: ")
            if cardNum.isnumeric():
                if len(cardNum) == 16:
                    validNum = True
                else:
                    print("ERROR: Card number must be 16 digits.")
            else:
                print("ERROR: Card number must be numeric.")
        self.delete_payment_method(self.email, cardNum)
        print("Payment method deleted!")

    def borrow_document_helper(self):
        docIDValid = False
        while not docIDValid:
            docID = input("Enter the document ID: ")
            if docID.isnumeric():
                docIDValid = True
            else:
                print("ERROR: Only enter numeric values.")
        self.borrow_document(self.email, docID)

    def return_loan_helper(self):
        validID = False
        while not validID:
            self.print_loans()
            loanID = input("Enter the loan ID: ")
            if loanID.isnumeric():
                self.return_loan(self.email, loanID)
                validID = True
            else:
                print("ERROR: Make sure to enter a numeric id.")

    def pay_fees_helper(self):
        validNum = False
        while not validNum:
            cardNum = input("Please enter your card number: ")
            if cardNum.isnumeric():
                if len(cardNum) == 16:
                    self.pay_fees(self.email, cardNum)
                    validNum = True
                else:
                    print("ERROR: Card number is 16 digits")
            else:
                print("ERROR: Only numeric values")

    def get_earliest_available(self, document_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT MIN(due_date) FROM loan WHERE loan.document_id = %s", (document_id,))
        earliest = cursor.fetchone()
        cursor.close()
        if earliest is None:
            return "-"
        else:
            return earliest[0]


    def print_book_results(self, books):
        book_columns = ["id", "copies", "edoc", "isbn", "title", "authors", "publisher", "edition", "year", "pages", "earliest available"]
        print()
        print("===================================================" + 
              "===================================================" + 
              "==========BOOKS====================================" + 
              "===================================================" + 
              "========================")
        for key in book_columns:
            print("{:<20}".format(key), end=" ")
        print()
        
        for book in books:
            id, copies, edoc, _, _, isbn, title, authors, publisher, edition, year, pages = book
            if len(title) > 20:
                title = title[:17] + "..."
            if len(authors) > 20:
                authors = authors[:17] + "..."
            if len(publisher) > 20:
                publisher = publisher[:17] + "..."
            print("{:<20}".format(id), end=" ")
            if edoc:
                print("{:<20}".format("-"), end=" ")
            else:
                print("{:<20}".format(copies), end=" ")
            print("{:<20}".format(edoc), end=" ")
            print("{:<20}".format(isbn), end=" ")
            print("{:<20}".format(title), end=" ")
            print("{:<20}".format(authors), end=" ")
            print("{:<20}".format(publisher), end=" ")
            print("{:<20}".format(edition), end=" ")
            print("{:<20}".format(year), end=" ")
            print("{:<20}".format(pages), end=" ")
            if copies == 0 and not edoc:
                earliest_avail = self.get_earliest_available(id)
                print(earliest_avail)
            else:
                print("-")
        print("===================================================" + 
              "===================================================" + 
              "===================================================" + 
              "===================================================" + 
              "========================")
        
    def print_magazine_results(self, magazines):
        magazine_columns = ["id", "copies", "edoc", "isbn", "title", "publisher", "year", "month", "earliest available"]
        print()
        print("                    " +
              "===================================================" + 
              "=======================================MAGAZINES===" + 
              "===================================================" +
              "=================================")
        print("                    ", end="")
        for key in magazine_columns:
            print("{:<20}".format(key), end=" ")
        print()
        
        for magazine in magazines:
            print("                    ", end="")
            id, copies, edoc, _, _, isbn, title, publisher, year, month = magazine
            if len(title) > 20:
                title = title[:17] + "..."
            if len(publisher) > 20:
                publisher = publisher[:17] + "..."
            print("{:<20}".format(id), end=" ")
            if edoc:
                print("{:<20}".format("-"), end=" ")
            else:
                print("{:<20}".format(copies), end=" ")
            print("{:<20}".format(edoc), end=" ")
            print("{:<20}".format(isbn), end=" ")
            print("{:<20}".format(title), end=" ")
            print("{:<20}".format(publisher), end=" ")
            print("{:<20}".format(year), end=" ")
            print("{:<20}".format(month), end=" ")
            if copies == 0 and not edoc:
                earliest_avail = self.get_earliest_available(id)
                print(earliest_avail)
            else:
                print("-")
        print("                    " +
              "===================================================" + 
              "===================================================" + 
              "===================================================" +
              "=================================")
        
    def print_journal_results(self, journals):
        journal_columns = ["id", "copies", "edoc", "name", "title", "authors", "publisher", "year", "issue", "num_issue", "earliest available"]
        print()
        print("===================================================" + 
              "===================================================" + 
              "========JOURNALS===================================" + 
              "===================================================" + 
              "========================")
        for key in journal_columns:
            print("{:<20}".format(key), end=" ")
        print()
        
        for journal in journals:
            id, copies, edoc, _, _, name, title, authors, publisher, year, issue, num_issue = journal
            if len(name) > 20:
                name = name[:17] + "..."
            if len(title) > 20:
                title = title[:17] + "..."
            if len(authors) > 20:
                authors = authors[:17] + "..."
            if len(publisher) > 20:
                publisher = publisher[:17] + "..."
            print("{:<20}".format(id), end=" ")
            if edoc:
                print("{:<20}".format("-"), end=" ")
            else:
                print("{:<20}".format(copies), end=" ")
            print("{:<20}".format(edoc), end=" ")
            print("{:<20}".format(name), end=" ")
            print("{:<20}".format(title), end=" ")
            print("{:<20}".format(authors), end=" ")
            print("{:<20}".format(publisher), end=" ")
            print("{:<20}".format(year), end=" ")
            print("{:<20}".format(issue), end=" ")
            print("{:<20}".format(num_issue), end=" ")
            if copies == 0 and not edoc:
                earliest_avail = self.get_earliest_available(id)
                print(earliest_avail)
            else:
                print("-")
        print("===================================================" + 
              "===================================================" + 
              "===================================================" + 
              "===================================================" + 
              "========================")

    def init_search(self):
        search_criteria = []

        while True:
            field = input("Enter the field to search (title, authors, publisher, year, etc.): ")
            operator = input("Enter the comparison operator (equals, contains, placeholders): ")
            value = input("Enter the value to search for: ")

            if field not in ["isbn", "name", "title", "author", "publisher", "edition", "year", "month", "issue", "num_issue", "pages"]:
                print("ERROR: Invalid search field. Please enter a valid search field (title, authors, publisher, year, etc.).")
                continue

            if operator not in ["equals", "contains", "placeholders"]:
                print("ERROR: Invalid comparison operator. Please enter 'equals', 'contains', or 'placeholders'.")
                continue

            search_criteria.append((field, operator, value))

            another_criteria = input("Do you want to add another search criterion? (y/n): ")
            if another_criteria.lower() != 'y':
                break
            while True:
                conditional = input("Enter the conditional (AND, OR) to link with the previous criterion: ").strip().upper()
                if conditional in ["AND", "OR"]:
                    search_criteria.append(conditional)
                    break
                else:
                    print("ERROR: Invalid conditional. Please enter 'AND' or 'OR'.")

        return search_criteria

    def search_documents(self, search_criteria):
        conditions = []
        params = []
        search_book = True
        search_magazine = True
        search_journal = True
        book_query = "SELECT * FROM document JOIN book on document.document_id = book.id"
        magazine_query = "SELECT * FROM document JOIN magazine on document.document_id = magazine.id"
        journal_query = "SELECT * FROM document JOIN journal_article on document.document_id = journal_article.id"

        # search_criteria is a list containing tuples of (field, operator, value) with conditions
        # in between. For example [(title, contains, "book"), OR, (title, contains, "cool")].
        # It will always end with a tuple, never a conditional
        for i in search_criteria:
            # Right here, we check if the current element is just a string, which means
            # it's a conditional (OR, AND). If so, we add it to the conditions list.
            # Ignoring everything below which is for the tuples
            if isinstance(i, str):
                conditions.append(i)
            else:
                # Here we check if the document types are compatible with the field chosen
                field, operator, value = i
                if field == "name":
                    search_book = False
                    search_magazine = False
                elif field == "isbn":
                    search_journal = False
                elif field == "authors":
                    search_magazine = False
                elif field == "pages":
                    search_journal = False
                    search_magazine = False
                elif field == "edition":
                    search_journal = False
                    search_magazine = False
                elif field == "month":
                    search_book = False
                    search_journal= False
                elif field == "issue":
                    search_book = False
                    search_magazine = False
                elif field == "num_issue":
                    search_book = False
                    search_magazine = False

                # Here we translate each operator into SQL and add it to the conditions list
                if operator == "equals":
                    conditions.append(field + " = %s")
                    params.append(value)
                elif operator == "contains":
                    conditions.append(field + " ILIKE %s")
                    params.append('%' + value + '%')
                elif operator == "placeholders":
                    conditions.append(field + " LIKE %s")
                    params.append(value)

        # Here we check if the conditions list is empty.
        # if not we join the conditions after a WHERE clause
        # Using the example before, for a book_query we get:
        # SELECT * FROM document JOIN book on document.document_id = book.id WHERE title ILIKE %'book'% OR title ILIKE %'cool'%
        # Notice that the conditions are always in the same order as from the search_criteria list
        if conditions:
            if search_book:
                book_query += " WHERE " + " ".join(conditions)
            if search_magazine:
                magazine_query += " WHERE " + " ".join(conditions)
            if search_journal:
                journal_query += " WHERE " + " ".join(conditions)

        cursor = self.conn.cursor()
        if not search_book and not search_magazine and not search_journal:
            print()
            print("Sorry, no search results found.")
            cursor.close()
            return
        
        books = None
        magazines = None
        journals = None
        if search_book:
            cursor.execute(book_query, tuple(params))
            books = cursor.fetchall()
            if books:
                self.print_book_results(books)
        if search_magazine:
            cursor.execute(magazine_query, tuple(params))
            magazines = cursor.fetchall()
            if magazines:
                self.print_magazine_results(magazines)
        if search_journal:
            cursor.execute(journal_query, tuple(params))
            journals = cursor.fetchall()
            if journals:
                self.print_journal_results(journals)

        if not books and not magazines and not journals:
            print()
            print("Sorry, no search results found.")
            cursor.close()
            return

        while True:
            print()
            print("[1] Make Another Search")
            print("[2] Borrow Document")
            print("[3] Change Sorting and Output Size")
            print("[4] Return To Menu")
            choice = input("Enter the number of what you'd like to do: ")

            if choice == '1':
                search_criteria = self.init_search()
                self.search_documents(search_criteria)
            elif choice == '2':
                self.borrow_document_helper()
            elif choice == '3':
                queries = [(search_book, book_query),
                           (search_magazine, magazine_query),
                           (search_journal, journal_query)]
                self.change_sort_and_lim(queries, params)
            elif choice == '4':
                print()
                self.client_menu()
            else:
                print("ERROR: Not a choice. Choose again.")

    def change_sort_and_lim(self, queries, params):
        cursor = self.conn.cursor()
        limit = "_"
        field = "_"
        validLim = False
        while not validLim:
            limit = input("Enter the desired output size (Enter an underscore '_' to keep unchanged): ")
            if limit.isnumeric():
                validLim = True
            else:
                print("ERROR: Please only enter numeric values.")

        valid = False
        while not valid:
            field = input("Enter the field above would you like to sort by (Enter an underscore '_' to keep current sorting): ")
            if field not in ["isbn", "name", "title", "author", "publisher", "edition", "year", "month", "issue", "num_issue", "pages", "_"]:
                print("ERROR: Invalid search field. Please enter a valid search field (title, authors, publisher, year, etc.).")
            else:
                valid = True

        count = 0
        if field != '_':
            while True:
                sort = input("Enter the sorting order (ASC, DESC): ").strip().upper()
                if sort in ["ASC", "DESC"]:
                    break
                else:
                    print("ERROR: Invalid sorting order. Please enter 'ASC' or 'DESC'.")
            for search, query in queries:
                pcopy = params[:]
                if search:
                    query += " ORDER BY " + field + " " + sort
                    if limit != '_':
                        query += " LIMIT %s"
                        pcopy.append(limit)
                    cursor.execute(query, pcopy)
                    output = cursor.fetchall()
                    if output:
                        if count == 0:
                            self.print_book_results(output)
                        elif count == 1:
                            self.print_magazine_results(output)
                        elif count == 2:
                            self.print_journal_results(output)
                count+=1
        elif limit != '_':
            pcopy = params[:]
            pcopy.append(limit)
            for search, query in queries:
                if search:
                    query += " LIMIT %s"
                    cursor.execute(query, pcopy)
                    output = cursor.fetchall()
                    if output:
                        if count == 0:
                            self.print_book_results(output)
                        elif count == 1:
                            self.print_magazine_results(output)
                        elif count == 2:
                            self.print_journal_results(output)
                count+=1
            
    def client_menu(self):
        valid = False
        while valid == False:
            print()
            print("[1] Search Documents")
            print("[2] Borrow Documents")
            print("[3] Return Documents")
            print("[4] Pay Overdue Fees")
            print("[5] Add Payment Method")
            print("[6] Remove Payment Method")
            print("[7] Print Loans")
            print("[8] Exit")
            choice = input("Enter the number of what you'd like to do: ")

            if choice == "1":
                search_criteria = self.init_search()
                self.search_documents(search_criteria)
                valid = True
                self.client_menu()
            elif choice == "2":
                self.borrow_document_helper()
                valid = True
                self.client_menu()
            elif choice == "3":
                self.return_loan_helper()
                valid = True
                self.client_menu()
            elif choice == "4":
                self.pay_fees_helper()
                valid = True
                self.client_menu()
            elif choice == "5":
                self.add_payment_helper()
                valid = True
                self.client_menu()
            elif choice == "6":
                self.delete_payment_helper()
                valid = True
                self.client_menu()
            elif choice == "7":
                self.print_loans()
                valid = True
                self.client_menu()
            elif choice == "8":
                print()
                print("Exiting...")
                exit()
            else:
                print("ERROR: Not a choice. Choose again.")