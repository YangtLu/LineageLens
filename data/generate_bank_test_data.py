from __future__ import annotations

import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TABLES = {
    "branches.csv": [
        {"branch_id": 101, "branch_code": "NYC001", "name": "Manhattan Flagship", "city": "New York", "state": "NY", "opened_date": "2012-05-14"},
        {"branch_id": 102, "branch_code": "BOS001", "name": "Back Bay Branch", "city": "Boston", "state": "MA", "opened_date": "2015-08-03"},
        {"branch_id": 103, "branch_code": "CHI001", "name": "Loop Branch", "city": "Chicago", "state": "IL", "opened_date": "2018-02-19"},
    ],
    "customers.csv": [
        {"customer_id": 1001, "branch_id": 101, "first_name": "Alicia", "last_name": "Carter", "date_of_birth": "1987-04-12", "email": "alicia.carter@examplebank.test", "phone": "212-555-0101", "risk_rating": "LOW", "joined_date": "2021-01-15"},
        {"customer_id": 1002, "branch_id": 101, "first_name": "Marcus", "last_name": "Nguyen", "date_of_birth": "1979-09-23", "email": "marcus.nguyen@examplebank.test", "phone": "212-555-0102", "risk_rating": "MEDIUM", "joined_date": "2020-11-02"},
        {"customer_id": 1003, "branch_id": 102, "first_name": "Priya", "last_name": "Patel", "date_of_birth": "1991-03-02", "email": "priya.patel@examplebank.test", "phone": "617-555-0103", "risk_rating": "LOW", "joined_date": "2022-04-21"},
        {"customer_id": 1004, "branch_id": 103, "first_name": "Daniel", "last_name": "Reed", "date_of_birth": "1984-12-18", "email": "daniel.reed@examplebank.test", "phone": "312-555-0104", "risk_rating": "HIGH", "joined_date": "2019-06-30"},
        {"customer_id": 1005, "branch_id": 103, "first_name": "Sofia", "last_name": "Lopez", "date_of_birth": "1995-07-08", "email": "sofia.lopez@examplebank.test", "phone": "312-555-0105", "risk_rating": "LOW", "joined_date": "2023-02-17"},
        {"customer_id": 1006, "branch_id": 102, "first_name": "Ethan", "last_name": "Brooks", "date_of_birth": "1975-01-27", "email": "ethan.brooks@examplebank.test", "phone": "617-555-0106", "risk_rating": "MEDIUM", "joined_date": "2018-09-11"},
    ],
    "employees.csv": [
        {"employee_id": 501, "branch_id": 101, "first_name": "Nina", "last_name": "Shaw", "title": "Branch Manager", "hire_date": "2016-07-01"},
        {"employee_id": 502, "branch_id": 101, "first_name": "Owen", "last_name": "Miles", "title": "Relationship Manager", "hire_date": "2019-03-15"},
        {"employee_id": 503, "branch_id": 102, "first_name": "Grace", "last_name": "Kim", "title": "Loan Officer", "hire_date": "2020-10-09"},
        {"employee_id": 504, "branch_id": 103, "first_name": "Leo", "last_name": "Turner", "title": "Fraud Analyst", "hire_date": "2021-05-24"},
        {"employee_id": 505, "branch_id": 103, "first_name": "Maya", "last_name": "Singh", "title": "Relationship Manager", "hire_date": "2017-12-04"},
    ],
    "accounts.csv": [
        {"account_id": 20001, "customer_id": 1001, "branch_id": 101, "relationship_manager_id": 502, "account_type": "CHECKING", "status": "ACTIVE", "opened_date": "2021-01-16", "currency_code": "USD", "current_balance": "12540.33"},
        {"account_id": 20002, "customer_id": 1001, "branch_id": 101, "relationship_manager_id": 502, "account_type": "SAVINGS", "status": "ACTIVE", "opened_date": "2021-02-01", "currency_code": "USD", "current_balance": "44200.00"},
        {"account_id": 20003, "customer_id": 1002, "branch_id": 101, "relationship_manager_id": 501, "account_type": "CHECKING", "status": "ACTIVE", "opened_date": "2020-11-05", "currency_code": "USD", "current_balance": "8300.18"},
        {"account_id": 20004, "customer_id": 1003, "branch_id": 102, "relationship_manager_id": 503, "account_type": "MONEY_MARKET", "status": "ACTIVE", "opened_date": "2022-04-25", "currency_code": "USD", "current_balance": "156700.54"},
        {"account_id": 20005, "customer_id": 1004, "branch_id": 103, "relationship_manager_id": 505, "account_type": "CHECKING", "status": "REVIEW", "opened_date": "2019-07-02", "currency_code": "USD", "current_balance": "1180.27"},
        {"account_id": 20006, "customer_id": 1005, "branch_id": 103, "relationship_manager_id": 505, "account_type": "SAVINGS", "status": "ACTIVE", "opened_date": "2023-02-18", "currency_code": "USD", "current_balance": "9300.00"},
        {"account_id": 20007, "customer_id": 1006, "branch_id": 102, "relationship_manager_id": 503, "account_type": "CHECKING", "status": "ACTIVE", "opened_date": "2018-09-13", "currency_code": "USD", "current_balance": "26750.45"},
    ],
    "cards.csv": [
        {"card_id": 30001, "account_id": 20001, "customer_id": 1001, "card_type": "DEBIT", "network": "VISA", "issued_date": "2021-01-20", "expiry_date": "2027-01-31", "card_status": "ACTIVE"},
        {"card_id": 30002, "account_id": 20003, "customer_id": 1002, "card_type": "DEBIT", "network": "MASTERCARD", "issued_date": "2020-11-10", "expiry_date": "2026-11-30", "card_status": "ACTIVE"},
        {"card_id": 30003, "account_id": 20004, "customer_id": 1003, "card_type": "CREDIT", "network": "VISA", "issued_date": "2022-05-01", "expiry_date": "2028-05-31", "card_status": "ACTIVE"},
        {"card_id": 30004, "account_id": 20005, "customer_id": 1004, "card_type": "DEBIT", "network": "VISA", "issued_date": "2019-07-07", "expiry_date": "2025-07-31", "card_status": "BLOCKED"},
        {"card_id": 30005, "account_id": 20006, "customer_id": 1005, "card_type": "DEBIT", "network": "MASTERCARD", "issued_date": "2023-02-22", "expiry_date": "2029-02-28", "card_status": "ACTIVE"},
    ],
    "loans.csv": [
        {"loan_id": 40001, "customer_id": 1002, "account_id": 20003, "branch_id": 101, "officer_employee_id": 501, "loan_type": "AUTO", "principal_amount": "22000.00", "interest_rate": "4.25", "origination_date": "2021-06-14", "maturity_date": "2026-06-14", "loan_status": "CURRENT"},
        {"loan_id": 40002, "customer_id": 1004, "account_id": 20005, "branch_id": 103, "officer_employee_id": 505, "loan_type": "SMALL_BUSINESS", "principal_amount": "150000.00", "interest_rate": "6.75", "origination_date": "2020-01-09", "maturity_date": "2027-01-09", "loan_status": "DELINQUENT"},
        {"loan_id": 40003, "customer_id": 1006, "account_id": 20007, "branch_id": 102, "officer_employee_id": 503, "loan_type": "HOME_EQUITY", "principal_amount": "85000.00", "interest_rate": "5.10", "origination_date": "2019-10-30", "maturity_date": "2034-10-30", "loan_status": "CURRENT"},
    ],
    "transactions.csv": [
        {"transaction_id": 500001, "account_id": 20001, "branch_id": 101, "customer_id": 1001, "transaction_timestamp": "2024-01-15T09:14:00", "transaction_type": "PAYROLL_DEPOSIT", "channel": "ACH", "amount": "4800.00", "direction": "CREDIT", "counterparty_reference": "ACME_PAYROLL"},
        {"transaction_id": 500002, "account_id": 20001, "branch_id": 101, "customer_id": 1001, "transaction_timestamp": "2024-01-16T18:27:00", "transaction_type": "POS_PURCHASE", "channel": "CARD", "amount": "126.48", "direction": "DEBIT", "counterparty_reference": "GROCERY_1148"},
        {"transaction_id": 500003, "account_id": 20003, "branch_id": 101, "customer_id": 1002, "transaction_timestamp": "2024-01-17T10:02:00", "transaction_type": "WIRE_TRANSFER", "channel": "ONLINE", "amount": "2500.00", "direction": "DEBIT", "counterparty_reference": "HOME_RENOVATION"},
        {"transaction_id": 500004, "account_id": 20004, "branch_id": 102, "customer_id": 1003, "transaction_timestamp": "2024-01-18T08:40:00", "transaction_type": "INTEREST_CREDIT", "channel": "SYSTEM", "amount": "145.29", "direction": "CREDIT", "counterparty_reference": "MMKT_INT"},
        {"transaction_id": 500005, "account_id": 20005, "branch_id": 103, "customer_id": 1004, "transaction_timestamp": "2024-01-18T23:11:00", "transaction_type": "ATM_WITHDRAWAL", "channel": "ATM", "amount": "500.00", "direction": "DEBIT", "counterparty_reference": "ATM_CHI_044"},
        {"transaction_id": 500006, "account_id": 20005, "branch_id": 103, "customer_id": 1004, "transaction_timestamp": "2024-01-19T23:54:00", "transaction_type": "INTERNATIONAL_CARD_NOT_PRESENT", "channel": "CARD", "amount": "980.75", "direction": "DEBIT", "counterparty_reference": "ELECTRONICS_GLOBAL"},
        {"transaction_id": 500007, "account_id": 20006, "branch_id": 103, "customer_id": 1005, "transaction_timestamp": "2024-01-20T11:20:00", "transaction_type": "MOBILE_DEPOSIT", "channel": "MOBILE", "amount": "2200.00", "direction": "CREDIT", "counterparty_reference": "CHECK_7731"},
        {"transaction_id": 500008, "account_id": 20007, "branch_id": 102, "customer_id": 1006, "transaction_timestamp": "2024-01-20T16:45:00", "transaction_type": "LOAN_PAYMENT", "channel": "ONLINE", "amount": "950.00", "direction": "DEBIT", "counterparty_reference": "LN40003_JAN"},
    ],
    "loan_payments.csv": [
        {"payment_id": 60001, "loan_id": 40001, "debit_account_id": 20003, "payment_date": "2024-01-15", "payment_amount": "405.33", "principal_component": "327.42", "interest_component": "77.91", "payment_status": "POSTED"},
        {"payment_id": 60002, "loan_id": 40002, "debit_account_id": 20005, "payment_date": "2024-01-12", "payment_amount": "2100.00", "principal_component": "1250.00", "interest_component": "850.00", "payment_status": "LATE"},
        {"payment_id": 60003, "loan_id": 40003, "debit_account_id": 20007, "payment_date": "2024-01-20", "payment_amount": "950.00", "principal_component": "588.75", "interest_component": "361.25", "payment_status": "POSTED"},
    ],
    "fraud_alerts.csv": [
        {"alert_id": 70001, "transaction_id": 500006, "account_id": 20005, "customer_id": 1004, "assigned_employee_id": 504, "alert_created_at": "2024-01-20T00:05:00", "alert_type": "CARD_ANOMALY", "severity": "HIGH", "alert_status": "OPEN"},
        {"alert_id": 70002, "transaction_id": 500005, "account_id": 20005, "customer_id": 1004, "assigned_employee_id": 504, "alert_created_at": "2024-01-19T02:14:00", "alert_type": "ATM_PATTERN", "severity": "MEDIUM", "alert_status": "CLOSED"},
    ],
}


def write_csv(filename: str, rows: list[dict[str, object]]) -> None:
    path = BASE_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    for name, rows in TABLES.items():
        write_csv(name, rows)
    print(f"Generated {len(TABLES)} CSV files in {BASE_DIR}")
