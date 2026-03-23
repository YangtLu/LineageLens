CREATE TABLE branches (
    branch_id INTEGER PRIMARY KEY,
    branch_code VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(80) NOT NULL,
    state CHAR(2) NOT NULL,
    opened_date DATE NOT NULL
);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    branch_id INTEGER NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(25) NOT NULL,
    risk_rating VARCHAR(10) NOT NULL,
    joined_date DATE NOT NULL,
    CONSTRAINT fk_customers_branch FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    branch_id INTEGER NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    title VARCHAR(80) NOT NULL,
    hire_date DATE NOT NULL,
    CONSTRAINT fk_employees_branch FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE accounts (
    account_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    relationship_manager_id INTEGER NOT NULL,
    account_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    opened_date DATE NOT NULL,
    currency_code CHAR(3) NOT NULL,
    current_balance DECIMAL(14,2) NOT NULL,
    CONSTRAINT fk_accounts_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_accounts_branch FOREIGN KEY (branch_id) REFERENCES branches(branch_id),
    CONSTRAINT fk_accounts_rm FOREIGN KEY (relationship_manager_id) REFERENCES employees(employee_id)
);

CREATE TABLE cards (
    card_id INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    card_type VARCHAR(20) NOT NULL,
    network VARCHAR(20) NOT NULL,
    issued_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    card_status VARCHAR(20) NOT NULL,
    CONSTRAINT fk_cards_account FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    CONSTRAINT fk_cards_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE loans (
    loan_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    officer_employee_id INTEGER NOT NULL,
    loan_type VARCHAR(30) NOT NULL,
    principal_amount DECIMAL(14,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    origination_date DATE NOT NULL,
    maturity_date DATE NOT NULL,
    loan_status VARCHAR(20) NOT NULL,
    CONSTRAINT fk_loans_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_loans_account FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    CONSTRAINT fk_loans_branch FOREIGN KEY (branch_id) REFERENCES branches(branch_id),
    CONSTRAINT fk_loans_officer FOREIGN KEY (officer_employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE transactions (
    transaction_id BIGINT PRIMARY KEY,
    account_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    transaction_timestamp TIMESTAMP NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    amount DECIMAL(14,2) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    counterparty_reference VARCHAR(100) NOT NULL,
    CONSTRAINT fk_transactions_account FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    CONSTRAINT fk_transactions_branch FOREIGN KEY (branch_id) REFERENCES branches(branch_id),
    CONSTRAINT fk_transactions_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE loan_payments (
    payment_id INTEGER PRIMARY KEY,
    loan_id INTEGER NOT NULL,
    debit_account_id INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    payment_amount DECIMAL(14,2) NOT NULL,
    principal_component DECIMAL(14,2) NOT NULL,
    interest_component DECIMAL(14,2) NOT NULL,
    payment_status VARCHAR(20) NOT NULL,
    CONSTRAINT fk_loan_payments_loan FOREIGN KEY (loan_id) REFERENCES loans(loan_id),
    CONSTRAINT fk_loan_payments_account FOREIGN KEY (debit_account_id) REFERENCES accounts(account_id)
);

CREATE TABLE fraud_alerts (
    alert_id INTEGER PRIMARY KEY,
    transaction_id BIGINT NOT NULL,
    account_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    assigned_employee_id INTEGER NOT NULL,
    alert_created_at TIMESTAMP NOT NULL,
    alert_type VARCHAR(40) NOT NULL,
    severity VARCHAR(10) NOT NULL,
    alert_status VARCHAR(20) NOT NULL,
    CONSTRAINT fk_fraud_alerts_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    CONSTRAINT fk_fraud_alerts_account FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    CONSTRAINT fk_fraud_alerts_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_fraud_alerts_employee FOREIGN KEY (assigned_employee_id) REFERENCES employees(employee_id)
);
