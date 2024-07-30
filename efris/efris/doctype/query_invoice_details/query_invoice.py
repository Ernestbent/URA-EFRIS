import json
import base64
from datetime import datetime, timedelta, timezone
import frappe
import requests

# Define the East Africa Time (EAT) timezone, which is UTC+3
eat_timezone = timezone(timedelta(hours=3))

def log_integration_request(status, url, headers, data, response, error=""):
    valid_statuses = ["", "Queued", "Authorized", "Completed", "Cancelled", "Failed"]
    status = status if status in valid_statuses else "Failed"
    
    # Format data and response as pretty-printed JSON
    formatted_data = json.dumps(data, indent=4)
    formatted_response = json.dumps(response, indent=4)

    integration_request = frappe.get_doc({
        "doctype": "Integration Request",
        "integration_type": "Remote",
        "method": "POST",
        "integration_request_service": "Query Invoice Details",
        "is_remote_request": True,
        "status": status,
        "url": url,
        "request_headers": json.dumps(headers, indent=4),
        "data": formatted_data,
        "output": formatted_response,
        "error": error,
        "execution_time": datetime.now(eat_timezone).strftime("%Y-%m-%d %H:%M:%S")
    })
    integration_request.insert(ignore_permissions=True)
    frappe.db.commit()

def query_invoice_information(doc, event):
    # Fetch the current session company
    company = frappe.defaults.get_user_default("company")
    if not company:
        frappe.throw("No default company set for the current session")

    # Fetch the Efris Settings document for the current company
    efris_settings_list = frappe.get_all("Efris Settings", filters={"custom_company": company}, limit=1)
    if not efris_settings_list:
        frappe.throw(f"No Efris Settings found for the company {company}")

    # Get the Efris Settings document
    efris_settings_doc_name = efris_settings_list[0].name
    efris_settings_doc = frappe.get_doc("Efris Settings", efris_settings_doc_name)
    
    # Extract settings
    device_number = efris_settings_doc.custom_device_number
    tin = efris_settings_doc.custom_tax_payers_tin
    server_url = efris_settings_doc.custom_server_url
    legal_name = efris_settings_doc.custom_legal_name
    business_name = efris_settings_doc.custom_business_name
    place_of_business = efris_settings_doc.custom_place_of_businesss
    email_id = efris_settings_doc.custom_email_address
    mobile_phone = efris_settings_doc.custom_mobile_phone
    line_phone = efris_settings_doc.custom_line_phone
    address = efris_settings_doc.custom_address
    
    # Prepare the data to post
    data_to_post = {
        "invoiceNo": doc.invoice_number,
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
            "interfaceCode": "T108",
            "requestCode": "TP",
            "requestTime": datetime.now(eat_timezone).strftime("%Y-%m-%d %H:%M:%S"),
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
        response = requests.post(server_url, json=data, headers=headers)
        response.raise_for_status()
        
        response_data = response.json()
        encoded_content = response_data["data"]["content"]
        decoded_content = base64.b64decode(encoded_content).decode("utf-8")
        # Format the JSON content with indent 4
        formatted_content = json.dumps(json.loads(decoded_content), indent=4)

        # Assign the formatted content to the doc's field
        doc.invoice_information = formatted_content
        # Log the successful integration request
        log_integration_request('Completed', server_url, headers, data, response_data)
        
        # Handle the response status code
        if response.status_code == 200:
            frappe.msgprint("Invoice Details Retrieved successfully")
        else:
            frappe.throw("Efris API Error")
    except requests.exceptions.RequestException as e:
        # Log the failed integration request
        log_integration_request('Failed', server_url, headers, data, {}, str(e))
        frappe.throw(f"API request failed: {e}")
