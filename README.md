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
- Your URA EFRIS credentials 

### Step 1: Clone the App
```bash
cd ~/frappe-bench
bench get-app https://github.com/Ernestbent/URA-EFRIS.git
```

### Step 2: Install the App
```bash
bench --site site1.local install-app efris
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
- Contact the maintainer at [benedict@phenomadvisory.com](mailto:benedict@phenom.com)

## 🔧 EFRIS Settings

The **EFRIS Settings** Doctype is used to configure and manage the connection between your ERPNext instance and the URA EFRIS system. These settings include environment toggles, credentials, server endpoints, and company-specific configuration needed for proper communication with the URA platform.

### 📝 Configuration Fields
![EFRIS Settings](assets/EFRIS%20Settings.png)



| Field Label             | Fieldname               | Description                                                                 |
|-------------------------|-------------------------|-----------------------------------------------------------------------------|
| **Details**             |                         | General information and instructions.                                       |
| **Submission Frequency**|                         | How often data should be submitted to EFRIS.                                |
| **Environment**         |                         | Specify whether the integration is in sandbox or production mode.           |
| **Sandbox**             | `custom_sandbox`        | Marks the environment as either sandbox (test) or production.               |
| **Is Active**           | `custom_is_active`      | Enables or disables the integration.                                        |

### 🌐 Settings Definition

| Field Label             | Fieldname               | Description                                                                 |
|-------------------------|-------------------------|-----------------------------------------------------------------------------|
| **Server URL**          | `custom_server_url`     | EFRIS Offline Enabler URL. Leave blank unless instructed otherwise.         |
| **Device Number**       | `custom_device_number`  | EFRIS Offline Enabler Device Number (e.g., TCSxxxxxxx).                     |

### 🏢 Company Settings

| Field Label             | Fieldname               | Description                                                                 |
|-------------------------|-------------------------|-----------------------------------------------------------------------------|
| **Legal Name**          | `custom_legal_name`     | Registered legal name of the company.                                       |
| **Company**             | `custom_company`        | Link to the company in ERPNext (e.g., MY COMPANY).          |
| **Branch ID**           | `custom_branch_id`      | Branch ID issued by URA.                                                    |
| **Line Phone**          | `custom_line_phone`     | Company landline number.                                                    |
| **Email Address**       | `custom_email_address`  | Email linked with the company’s URA account.                                |
| **Tax Payer's TIN**     | `custom_tax_payers_tin` | Company’s URA Taxpayer Identification Number (TIN).                         |
| **Business Name**       | `custom_business_name`  | Registered business name as per URA records.                                |
| **BRN**                 | `custom_brn`            | Business Registration Number.                                               |
| **Mobile Phone**        | `custom_mobile_phone`   | Primary contact mobile number.                                              |
| **Address**             | `custom_address`        | Registered physical address of the company.                                 |
| **Place of Business**   |                         | Location of the business as declared to URA.                                |

---

🛠️ **Note**: Ensure all fields are filled accurately to avoid API authentication failures or submission errors. In sandbox mode, dummy values can be used for testing, while production requires valid URA-issued credentials.
## 🧾 Item Registration

This section is used to configure items (goods or services) for EFRIS submission. Key fields include:
![Item Configuration](assets/Item%20Configuration.png)

- **Company**: Link the item to a specific company.
- **Add Product (Goods/Services)**: Reference an existing product registered in EFRIS.
- **Excise Tax**: Checkbox for whether the item is subject to excise tax.
- **Goods Category ID**: EFRIS code for the item.
- **Item Name & Code**: Name and code of the commodity.
- **Item Group**: Classification/grouping of the item.
- **Unit of Measure (UOM)** & **UOM Code (EFRIS)**: Defines quantity unit and its corresponding EFRIS code.
- **EFRIS Item**: Checkbox to indicate if the item should be synced with EFRIS.
- **Register/Modify Item**: Set to `101` to register, `102` to modify.
- **Stock, Variants, Pricing Fields**: Includes stock tracking, valuation, and pricing configuration.

## 🧾 Purchasing Stock in Purchase Invoice

To stock in items in ERPNext via a **Purchase Invoice**, you need to specify the type of purchase based on whether it’s a **Local Purchase**, **Import**, or **Manufacturing/Assembling**. The distinction is crucial for proper stock management.

### Key Fields:
![Purchase Invoice Configuration](assets/Stock%20In.png)

- **Company**: Link the invoice to the specific company.
- **Supplier**: Select the vendor from whom you are purchasing the goods.
- **Item Details**: Ensure to enter the correct items being purchased, along with their quantities and unit prices.
- **Stock UOM**: The unit of measure for the item being purchased.
- **Purchase Type**:
    - **Local Purchase**: Goods purchased locally.
    - **Import**: Goods purchased from international suppliers.
    - **Manufacturing/Assembling**: Items related to manufacturing or assembly processes.
 
## 🛠️ Stock Adjustment

Stock adjustments are made when there is a need to issue materials or make changes to the stock levels. In ERPNext, this can be done through a **Stock Entry** with the adjustment reason specified.

![Stock Adjustment](assets/Stock%20Adjustments.png)

### Key Steps:

1. **Create a Stock Entry**: This is done under the **Stock Entry** document where you can adjust stock quantities for various items.
2. **Select the Material Issue Type**: Choose the **Material Issue** option to issue the stock out of the warehouse.
3. **Enter the Adjusted Quantity**: Specify the quantity that needs to be adjusted (either positive or negative).
4. **Stock Adjustment Reason**: Choose the reason for the stock adjustment from the list of predefined reasons.

### Stock Adjustment Reasons:

- **Expired Goods**: Adjust stock when goods reach their expiry date and are no longer usable.
- **Damaged Goods**: Use this reason when goods are damaged during handling, storage, or shipping.
- **Personal Issues**: Sometimes, stock adjustments are made due to personal reasons like misplacement, theft, or personal usage.
- **Raw Materials**: Adjustments related to raw materials that might not be usable for production.

### Important Notes:

- Ensure that the **Stock Adjustment Reason** is selected properly for accurate inventory management.
- You can also track adjustments made to stock for auditing purposes by referencing the reason behind each adjustment.
- **Material Issue** is linked to stock levels, so any changes here will directly affect your inventory.

## 🧑‍🤝‍🧑 Customer Creation

The customer creation process in ERPNext involves retrieving customer information, especially for clients who have a **Taxpayer Identification Number (TIN)**. This is done by first checking the **URA (Uganda Revenue Authority)** database to verify and retrieve the relevant details before creating the customer record in the system.

![Customer Creation](assets/Customer%20Creation.png)

### Key Steps:

1. **Retrieve Taxpayer Information from URA**:
   - Before creating a new customer, the system checks the **URA** database for the provided **TIN number**. If the customer has an existing TIN registered with URA, their details (like legal name, company, and tax status) are retrieved automatically.

2. **Enter TIN Number**:
   - When creating the customer, enter the **TIN number** to retrieve data from the URA database. If the TIN is valid, the relevant customer information will be pulled from URA.

3. **Pre-populate Customer Fields**:
   - Once the TIN is validated, the customer form will be pre-populated with data retrieved from the URA database. This includes fields like:
     - **Legal Name**
     - **Company**
     - **Email Address**
     - **Phone Number**
     - **Taxpayer's TIN**
     - **Business Name**
     - **Company Address**
     - **Other required details**
   
4. **Save Customer Record**:
   - After verifying and filling in any necessary missing fields, save the customer record in ERPNext.

### Important Notes:

- **TIN Verification**: Ensure that the TIN is valid before creating a customer. This prevents the creation of invalid customer records.
- **Data Accuracy**: Make sure the data retrieved from URA is up-to-date and accurate. If there are discrepancies, manual updates might be required.
- **Customer Group**: Group customers based on certain criteria (e.g., **B2B**, **Government**, **B2C**, etc.) for easy management.


Made with ❤️ by Ernest Ben
