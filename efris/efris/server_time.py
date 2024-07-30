import base64
import json
import frappe
from frappe.utils.data import now
import requests
from datetime import datetime, timedelta, timezone

# Define the East Africa Time (EAT) timezone, which is UTC+3
eat_timezone = timezone(timedelta(hours=3))

# Get the current time in EAT
current_time = datetime.now(eat_timezone).strftime("%Y-%m-%d %H:%M:%S")

print("Current time in Uganda (EAT):", current_time)
@frappe.whitelist()
def get_server_time():
    def get_current_datetime():
        now = datetime.now()
        formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_datetime

    current_datetime = get_current_datetime()

    # Fetch the current session company
    company = frappe.defaults.get_user_default("company")
    if not company:
        frappe.throw("No default company set for the current session")

    # Fetch the Efris Settings document for the current company
    efris_settings_list = frappe.get_all("Efris Settings", filters={"custom_company": company}, limit=1)
    if not efris_settings_list:
        frappe.throw(f"No Efris Settings found for the company {company}")

    # Get the document name (fetch the correct one based on the company)
    efris_settings_doc_name = efris_settings_list[0].name
    efris_settings_doc = frappe.get_doc("Efris Settings", efris_settings_doc_name)
    
    device_number = efris_settings_doc.custom_device_number
    tin = efris_settings_doc.custom_tax_payers_tin
    server_url = efris_settings_doc.custom_server_url
    url = server_url  # Replace with your actual API endpoint
    headers = {
        'Content-Type': 'application/json',
    }

    # Define the fixed data to be sent
    data = {
        "data": {
            "content": "",
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
            "interfaceCode": "T101",
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

    try:
        # Make the POST request with data
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Get the JSON data from the response
        response_json = response.json()
        
        # Print the response in the terminal
        print("Response JSON:", response_json)

        # Base64 decode the string
        encoded_string = response_json.get("data", {}).get("content", "")
        decoded_bytes = base64.b64decode(encoded_string)
        # Decode the bytes to a UTF-8 string
        decoded_string = decoded_bytes.decode('utf-8')
        # Parse the JSON string
        decoded_json = json.loads(decoded_string)

        # Log the successful integration request
        log_integration_request('Completed', url, headers, data, response_json, "")

        return {
            "status": "success",
            "message": decoded_json
        }
    except requests.exceptions.RequestException as e:
        # Log the failed integration request
        log_integration_request('Failed', url, headers, data, {}, str(e))
        frappe.throw(f"API request failed: {e}")
    except (base64.binascii.Error, json.JSONDecodeError) as e:
        # Handle decoding errors
        log_integration_request('Failed', url, headers, data, {}, str(e))
        frappe.throw(f"Error decoding response: {e}")

    return {
        "status": "failed",
        "message": "Something went wrong"
    }

def log_integration_request(status, url, headers, data, response, error=""):
    valid_statuses = ["", "Queued", "Authorized", "Completed", "Cancelled", "Failed"]
    if status not in valid_statuses:
        status = "Failed"  # Default to "Failed" if status is invalid

    try:
        integration_request = frappe.get_doc({
            "doctype": "Integration Request",
            "integration_type": "Remote",
            "is_remote_request":True,
            "integration_request_service":"System Dictionary ",
            "method": "POST",
            "status": status,
            "url": url,
            "request_headers": json.dumps(headers),
            "data": json.dumps(data),
            "output": json.dumps(response),
            "error": error,  # Set error field based on provided error message
            "execution_time": now()
        })
        integration_request.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"Integration request logged with status: {status}")
    except Exception as e:
        # Log any exceptions that occur during logging
        print(f"Failed to log integration request: {e}")
