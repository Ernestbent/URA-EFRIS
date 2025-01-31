import json
import base64
import requests
from datetime import datetime, timedelta, timezone
import frappe

# Define the East Africa Time (EAT) timezone
eat_timezone = timezone(timedelta(hours=3))

@frappe.whitelist()
def make_api_call():
    # Fetch the first customer or any condition you want
    customer = frappe.get_all("Customer", fields=["tax_id"], limit=1)  # Fetch tax_id for the first customer
    
    if not customer:
        frappe.throw("No customer found with tax_id.")
    
    tax_id = customer[0].get("tax_id")  # Get the tax_id from the first customer
    
    if not tax_id:
        frappe.throw("No tax_id found for the customer.")

    # Fetch the current session company
    company = frappe.defaults.get_user_default("company")
    if not company:
        frappe.throw("No default company set for the current session")

    # Fetch the Efris Settings document for the current company
    efris_settings_list = frappe.get_all("Efris Settings", filters={"custom_company": company}, limit=1)
    if not efris_settings_list:
        frappe.throw(f"No Efris Settings found for the company {company}")

    efris_settings_doc_name = efris_settings_list[0].name
    efris_settings_doc = frappe.get_doc("Efris Settings", efris_settings_doc_name)
    
    device_number = efris_settings_doc.custom_device_number
    tin = efris_settings_doc.custom_tax_payers_tin
    server_url = efris_settings_doc.custom_server_url

    # Get the current time in EAT
    current_time = datetime.now(eat_timezone).strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare the data for the API request
    data_to_post = {
        "ninBrn": "",  # If you have the BRN (Business Registration Number), you can pass it here.
        "tin": tax_id   # Use the tax_id from the customer document
    }
    
    json_string = json.dumps(data_to_post)
    encoded_data = base64.b64encode(json_string.encode("utf-8")).decode("utf-8")
    
    data = {
        "data": {
            "content": encoded_data,
            "signature": "",
            "dataDescription": {
                "codeType": "0",
                "encryptionCode": "1",
                "zipCode": "0",
            },
        },
        "globalInfo": {
            "appId": "AP04",
            "version": "1.1.20191201",
            "dataExchangeId": "1",
            "interfaceCode": "T119",
            "requestCode": "TP",
            "requestTime": current_time,
            "responseCode": "TA",
            "userName": "admin",
            "deviceMAC": "B47720524158",
            "deviceNo": device_number,
            "tin": tin,
            "brn": "",
            "taxpayerID": "1",
            "longitude": "32.61665",
            "latitude": "0.36601",
            "agentType": "0",
            "extendfield": {
                "responseDateFormat": "dd/MM/yyyy",
                "responseTimeFormat": "dd/MM/yyyy HH:mm:ss",
                "referenceNo": "24PL01000221",
                "operatorName": "administrator",
            },
        },
        "returnStateInfo": {
            "returnCode": "",
            "returnMessage": ""
        },
    }

    headers = {'Content-Type': "application/json"}

    try:
        # Make the POST request to the API
        response = requests.post(server_url, json=data, headers=headers)
        response_data = response.json()  # Directly parse JSON response

        # Handle success or failure based on response
        if response.status_code == 200:
            
            # Process the successful response
            return {"status": "success", "data": response_data}
        else:
            return {"status": "failed", "message": response_data.get("returnStateInfo", {}).get("returnMessage", "Unknown error")}

    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        return {"status": "failed", "message": str(e)}
