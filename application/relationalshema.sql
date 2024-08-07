CREATE TABLE librarian (
    ssn VARCHAR(11) NOT NULL,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,
    salary INT,
	PRIMARY KEY (ssn)
);

CREATE TABLE client (
    email VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL,
    fees INT NOT NULL DEFAULT 0,
	PRIMARY KEY (email)
);

CREATE TABLE address (
	client_email VARCHAR(50) NOT NULL,
	client_address VARCHAR(100) UNIQUE NOT NULL,
	PRIMARY KEY (client_email, client_address),
    FOREIGN KEY (client_email) REFERENCES client(email)
);

CREATE TABLE credit_card (
	client_email VARCHAR(50) NOT NULL,
	card_number VARCHAR(16) UNIQUE NOT NULL,
	expiry_date DATE NOT NULL,
	payment_address VARCHAR(100) NOT NULL,
	charges INT NOT NULL DEFAULT 0,
	PRIMARY KEY (client_email, card_number, payment_address),
	FOREIGN KEY (payment_address) REFERENCES address(client_address),
	FOREIGN KEY (client_email) REFERENCES client(email)
);

CREATE TABLE document (
    document_id INT UNIQUE NOT NULL,
    copies INT NOT NULL,
    edoc BOOLEAN DEFAULT FALSE NOT NULL,
    document_type VARCHAR(20) NOT NULL CHECK (document_type IN ('book', 'magazine', 'journal')),
	PRIMARY KEY (document_id)
);

CREATE TABLE book (
	id INT NOT NULL,
	isbn VARCHAR(13) UNIQUE NOT NULL,
	title VARCHAR(50) NOT NULL,
	authors VARCHAR(50) NOT NULL,
	publisher VARCHAR(50) NOT NULL,
	edition VARCHAR(5) NOT NULL,
	year VARCHAR(4) NOT NULL,
	pages INT NOT NULL,
	PRIMARY KEY (id, isbn),
	FOREIGN KEY (id) REFERENCES document(document_id)
);

CREATE TABLE magazine (
	id INT NOT NULL,
	isbn VARCHAR(13) UNIQUE NOT NULL,
	title VARCHAR(50) NOT NULL,
	publisher VARCHAR(50) NOT NULL,
	year VARCHAR(4) NOT NULL,
	month VARCHAR(2) NOT NULL,
	PRIMARY KEY (id, isbn),
	FOREIGN KEY (id) REFERENCES document(document_id)
);

CREATE TABLE journal_article (
	id INT NOT NULL,
	name VARCHAR(50) UNIQUE NOT NULL,
	title VARCHAR(50) NOT NULL,
	authors VARCHAR(50) NOT NULL,
	publisher VARCHAR(50) NOT NULL,
	year VARCHAR(4) NOT NULL,
	issue VARCHAR(10) NOT NULL,
	num_issue INT NOT NULL,
	PRIMARY KEY (id, name),
	FOREIGN KEY (id) REFERENCES document(document_id)
);
	
CREATE TABLE loan (
    loan_id INT UNIQUE NOT NULL,
	document_id INT NOT NULL,
	client_email VARCHAR(50) NOT NULL,
    date_lent DATE NOT NULL,
    due_date DATE NOT NULL,
	PRIMARY KEY (loan_id, client_email),
	FOREIGN KEY (client_email) REFERENCES client(email),
    FOREIGN KEY (document_id) REFERENCES document(document_id)
);

CREATE INDEX addr_email ON address(client_email);
CREATE INDEX cc_email ON credit_card(client_email);
CREATE INDEX doc_id ON document(document_id);
