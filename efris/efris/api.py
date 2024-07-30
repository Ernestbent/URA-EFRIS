import frappe
from frappe.utils.data import now
import requests
from datetime import datetime, timedelta, timezone
import json
import gzip
import base64

# Define the East Africa Time (EAT) timezone, which is UTC+3
eat_timezone = timezone(timedelta(hours=3))

def decompress_gzip(data):
    try:
        decompressed_data = gzip.decompress(data)
        return decompressed_data.decode('utf-8')
    except Exception as e:
        print("Error Decompressing Gzip data:", e)
        return None

@frappe.whitelist()
def send_fixed_data_to_external_system():
    def get_current_datetime():
        now = datetime.now(eat_timezone)
        formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_datetime

    # Get the current time in EAT dynamically
    current_time = get_current_datetime()

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
    doc = frappe.get_doc("Efris Settings", efris_settings_doc_name)
    
    device_number = doc.custom_device_number
    tin = doc.custom_tax_payers_tin
    server_url = doc.custom_server_url
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
            "interfaceCode": "T115",
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
        compressed_data = response_json["data"]["content"]
        
        # Decode Base64 and decompress the data
        try:
            decoded_data = base64.b64decode(compressed_data)
            decompressed_data = decompress_gzip(decoded_data)
            if decompressed_data:
                print("Decompressed Data:", decompressed_data)
                json_data = json.loads(decompressed_data)
                print("Decompressed JSON:", json.dumps(json_data, indent=4))

                # Process UOM data
                for rate in json_data.get("rateUnit", []):
                    uom_name = rate.get("name", "")
                    uom_value = rate.get("value", "")

                    # Check if the UOM already exists
                    existing_uom = frappe.get_all("UOM", filters={"uom_name": uom_name}, limit=1)
                    
                    if existing_uom:
                        # Update existing UOM
                        uom_doc = frappe.get_doc("UOM", uom_name)
                        uom_doc.custom_value = uom_value
                        uom_doc.save()
                        print(f"Updated UOM: {uom_name}")
                    else:
                        # Insert new UOM
                        uom_doc = frappe.new_doc("UOM")
                        uom_doc.uom_name = uom_name
                        uom_doc.custom_value = uom_value
                        uom_doc.insert()
                        print(f"Inserted UOM: {uom_name}")

                # Log the successful integration request
                log_integration_request('Completed', url, headers, data, response_json, decompressed_data)

        except Exception as e:
            print("Error:", e)
            log_integration_request('Failed', url, headers, data, response_json, str(e))

        return {
            "status": "success",
            "message": response_json
        }
    except requests.exceptions.RequestException as e:
        frappe.throw(f"API request failed: {e}")

    return {
        "status": "failed",
        "message": "Something went wrong"
    }

def log_integration_request(status, url, headers, data, response, error=""):
    valid_statuses = ["", "Queued", "Authorized", "Completed", "Cancelled", "Failed"]
    if status not in valid_statuses:
        status = "Failed"  # Default to "Failed" if status is invalid

    integration_request = frappe.get_doc({
        "doctype": "Integration Request",
        "integration_type": "Remote",
        "is_remote_request": True,
        "integration_request_service": "Efris",
        "method": "POST",
        "status": status,
        "url": url,
        "request_headers": json.dumps(headers, indent=4),
        "data": json.dumps(data, indent=4),
        "output": json.dumps(response, indent=4),
        "execution_time": now()
    })
    integration_request.insert(ignore_permissions=True)  # This line inserts the integration request into ERPNext
    frappe.db.commit()
