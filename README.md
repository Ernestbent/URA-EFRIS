# 🇺🇬 URA EFRIS Integration for ERPNext

This is a custom Frappe app that integrates ERPNext with the **Uganda Revenue Authority (URA) Electronic Fiscal Receipting and Invoicing System (EFRIS)**. It allows businesses in Uganda to automatically submit sales transactions, credit notes, and product information to URA, as required by the EFRIS compliance regulations.

---

## 🎯 Purpose

Uganda Revenue Authority (URA) mandates businesses to use EFRIS for real-time invoicing and tax reporting. Manually submitting each invoice is time-consuming, error-prone, and inefficient. This app solves that by:

- Seamlessly connecting your ERPNext system with URA's EFRIS API
- Automatically submitting **Sales Invoices**, **Credit Notes**, and **Product Registrations**
- Keeping a full audit log of all integration requests and responses
- Reducing manual effort and ensuring tax compliance

---

## 🔁 Integration Logic: ERPNext ↔ URA EFRIS

Here’s how the integration works:

1. **Sales Invoice Submission**
   - When a Sales Invoice is submitted in ERPNext, the app prepares a JSON payload as per URA's EFRIS format.
   - The payload includes TIN, invoice details, tax breakdown, and item metadata.
   - The system sends this to URA’s `/invoice/upload` endpoint.
   - The URA response (success or error) is saved in an **Integration Request** log.

2. **Credit Note (Return) Handling**
   - If a submitted invoice is canceled (return), a request is sent to `/invoice/return`.
   - URA acknowledges the credit note and adjusts tax records accordingly.

3. **Product (Goods/Services) Registration**
   - Items created in ERPNext can be pushed to EFRIS via a button or automatic trigger.
   - Details such as name, unit, price, and category are sent to URA’s `/goods/register` or `/goods/update` endpoints.



---

## 📦 Installation

### Prerequisites

Before installation, ensure you have:

- A working Frappe/ERPNext setup (v13 or later)
- A created site (e.g., `site1.local`)
- Bench CLI access
- Your URA EFRIS credentials

---

### Step 1: Clone the App

Clone the custom app into your bench directory by running the following command:

```bash
cd ~/frappe-bench
bench get-app efris https://github.com/Ernestbent/URA-EFRIS.git









