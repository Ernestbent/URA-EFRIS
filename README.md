# 🇺🇬 URA EFRIS Integration for ERPNext

This is a custom Frappe app that integrates ERPNext with the **Uganda Revenue Authority (URA) Electronic Fiscal Receipting and Invoicing System (EFRIS)**. It allows businesses in Uganda to automatically submit sales transactions, credit notes, and product information to URA, as required by the EFRIS compliance regulations.

## 🎯 Purpose

Uganda Revenue Authority (URA) mandates businesses to use EFRIS for real-time invoicing and tax reporting. Manually submitting each invoice is time-consuming, error-prone, and inefficient. This app solves that by:
- Seamlessly connecting your ERPNext system with URA's EFRIS API
- Automatically submitting **Sales Invoices**, **Credit Notes**, and **Product Registrations**
- Keeping a full audit log of all integration requests and responses
- Reducing manual effort and ensuring tax compliance

## 🔁 Integration Logic: ERPNext ↔ URA EFRIS

Here's how the integration works:

1. **Sales Invoice Submission**
   - When a Sales Invoice is submitted in ERPNext, the app prepares a JSON payload as per URA's EFRIS format.
   - The payload includes TIN, invoice details, tax breakdown, and item metadata.
   - The system sends this to URA's `/invoice/upload` endpoint.
   - The URA response (success or error) is saved in an **Integration Request** log.

2. **Credit Note (Return) Handling**
   - If a submitted invoice is canceled (return), a request is sent to `/invoice/return`.
   - URA acknowledges the credit note and adjusts tax records accordingly.

3. **Product (Goods/Services) Registration**
   - Items created in ERPNext can be pushed to EFRIS via a button or automatic trigger.
   - Details such as name, unit, price, and category are sent to URA's `/goods/register` or `/goods/update` endpoints.

4. **Security and Tokens**
   - EFRIS credentials (Client ID, Secret, TIN) are configured securely in the app.
   - The app manages session tokens automatically and includes them in all requests.

## 📦 Installation

### Prerequisites
Before installation, ensure you have:
- A working Frappe/ERPNext setup (v13 or later)
- A created site (e.g., `site1.local`)
- Bench CLI access
- Your URA EFRIS credentials (TIN, Client ID, Client Secret)

### Step 1: Clone the App
```bash
cd ~/frappe-bench
bench get-app efris_integration https://github.com/Ernestbent/URA-EFRIS.git
```

### Step 2: Install the App
```bash
bench --site site1.local install-app efris_integration
```

### Step 3: Configure EFRIS Credentials
1. Go to **URA EFRIS Settings** in ERPNext
2. Enter your TIN, Client ID, and Client Secret
3. Select the environment (Production or Testing)
4. Save the configuration

## 🛠️ Features

- **Automatic Invoice Submission**: Submit Sales Invoices to URA in real-time
- **Credit Note Integration**: Process returns and credit notes with URA
- **Product Registration**: Register or update products in the URA system
- **Comprehensive Logging**: Track all API requests and responses
- **Error Handling**: Detailed error messages for troubleshooting
- **Configurable Settings**: Control which transactions are sent to URA

## 📊 Reports and Monitoring

- **Integration Logs**: View status of all EFRIS submissions
- **Reconciliation Tool**: Compare ERPNext invoices with URA records
- **Pending Submissions**: Track invoices awaiting submission

## 🔄 Usage

### Sales Invoice Submission
- Create and submit a Sales Invoice in ERPNext
- The system automatically sends it to URA
- View submission status in the EFRIS tab of the Sales Invoice

### Item Registration
1. Go to any Item in ERPNext
2. Click "Register with URA" button
3. View registration status in the EFRIS section

### Manual Submission
For previously created invoices:
1. Go to "URA EFRIS Dashboard"
2. Select invoices to submit
3. Click "Submit to URA"

## 🔧 Troubleshooting

- **API Connection Issues**: Verify internet connection and EFRIS credentials
- **Validation Errors**: Check invoice format against URA requirements
- **Authentication Failures**: Ensure valid and unexpired credentials

## 📝 License

This application is licensed under the [MIT License](LICENSE).

## 👨‍💻 Support

For support, bug reports, or feature requests, please:
- Open an issue on [GitHub](https://github.com/Ernestbent/URA-EFRIS/issues)
- Contact the maintainer at [ernest@example.com](mailto:ernest@example.com)

---

Made with ❤️ by Ernest Bent
