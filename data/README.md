# Bank testing dataset

This folder contains a small, linked banking dataset for demos, lineage testing, and relational ingestion exercises.

## Files
- `bank_sample_schema.sql`: SQL DDL for the tables and foreign-key relationships.
- `generate_bank_test_data.py`: deterministic generator for the CSV fixtures in this folder.
- CSV tables:
  - `branches.csv`
  - `customers.csv`
  - `employees.csv`
  - `accounts.csv`
  - `cards.csv`
  - `loans.csv`
  - `transactions.csv`
  - `loan_payments.csv`
  - `fraud_alerts.csv`

## Relationship overview
- `branches.branch_id` links to customers, employees, accounts, loans, and transactions.
- `customers.customer_id` links to accounts, cards, loans, transactions, and fraud alerts.
- `employees.employee_id` links to accounts (`relationship_manager_id`), loans (`officer_employee_id`), and fraud alerts (`assigned_employee_id`).
- `accounts.account_id` links to cards, loans, transactions, loan payments, and fraud alerts.
- `transactions.transaction_id` links directly to fraud alerts.

## Regenerating the CSV files
```bash
python data/generate_bank_test_data.py
```

All values are synthetic and formatted to feel realistic for testing, but they do not represent real customers.
