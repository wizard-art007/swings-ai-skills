# iPhone SMS Expense Parser

A lightweight, local-first Python experimental project for parsing and categorizing bank transaction SMS/notification texts (common on iOS workflows where direct SMS reading is restricted).

## How it Works
1. **Ingest**: Takes raw bank SMS strings (e.g., "Alert: Spent $45.50 at Starbucks on 10/24").
2. **Regex Parsing**: Extracts key details—amount, currency, merchant, transaction type (debit/credit), and date using robust regular expressions.
3. **Rule-Based Categorization**: Maps merchant names or keywords to predefined categories (Food, Transport, Utilities, Shopping, etc.).
4. **Aggregation**: Generates summary statistics and exports JSON reports.

## Running Tests
Run pytest completely offline:
