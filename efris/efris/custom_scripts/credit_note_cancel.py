import frappe
import requests
import json
import base64
from datetime import datetime, timezone, timedelta

# Define the East Africa Time (EAT) timezone, which is UTC+3
eat_timezone = timezone(timedelta(hours=3))

def get_current_datetime_combined():
    now = datetime.now(eat_timezone)  # Get current time in EAT timezone
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    return date_str + " " + time_str

def log_integration_request(status, url, headers, data, response, error=""):
    valid_statuses = ["", "Queued", "Authorized", "Completed", "Cancelled", "Failed"]
    status = status if status in valid_statuses else "Failed"
    
    integration_request = frappe.get_doc({
        "doctype": "Integration Request",
        "integration_type": "Remote",
        "method": "POST",
        "integration_request_service": "Cancellation Of Credit Note",
        "is_remote_request": True,
        "status": status,
        "url": url,
        "request_headers": json.dumps(headers, indent=4),
        "data": json.dumps(data, indent=4),
        "output": json.dumps(response, indent=4),
        "error": error,
        "execution_time": datetime.now(eat_timezone).strftime("%Y-%m-%d %H:%M:%S")
    })
    integration_request.insert(ignore_permissions=True)
    frappe.db.commit()

def on_cancel(doc, event):
    if not doc.is_return:  # Replace with the actual field to check if it's a return
        
        return

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

    # Sample cancellation_data dictionary
    cancellation_data = {
        "oriInvoiceId": doc.custom_invoice_number,  # Replace with actual invoice ID
        "invoiceNo": doc.custom_fdn,     # Replace with actual invoice number
        "reason": "",  # Provide the reason if applicable
        "reasonCode": "102",
        "invoiceApplyCategoryCode": "104",
        "attachmentList": [
            {
                "fileName": "",  # Provide the file name if applicable
                "fileType": "",  # Provide the file type if applicable
                "fileContent": ""  # Base64 encoded file content if applicable
            }
        ]
    }

    # Encode the cancellation_data to JSON and then to Base64
    cancellation_data_json = json.dumps(cancellation_data, indent=4)
    encoded_json_cancellation = base64.b64encode(cancellation_data_json.encode()).decode()
    
    current_time = datetime.now(eat_timezone).strftime("%Y-%m-%d %H:%M:%S")
    # Prepare the API request data
    data_to_post = {
        "data": {
            "content": encoded_json_cancellation,  # Base64 encoded JSON string
            "signature": "",
            "dataDescription": {
                "codeType": "0",
                "encryptCode": "1",
                "zipCode": "0",
            },
        },
        "globalInfo": {
            "appId": "AP04",
            "version": "1.1.20191201",
            "dataExchangeId": "9230489223014123",
            "interfaceCode": "T114",  # Assuming T114 for cancellation
            "requestCode": "TP",
            "requestTime": current_time,  # Use the combined datetime string
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
            "extendField": {
                "responseDateFormat": "dd/MM/yyyy",
                "responseTimeFormat": "dd/MM/yyyy HH:mm:ss",
                "referenceNo": "24PL01000221",
                "operatorName": "administrator",
            },
        },
        "returnStateInfo": {"returnCode": "", "returnMessage": ""},
    }

    # Convert data_to_post to JSON string if needed
    data_to_post_json = json.dumps(data_to_post, indent=4)

    # Print the JSON request data (for debugging purposes)
    print("API Request Data:")
    print(data_to_post_json)

    # Prepare the API request
    api_url = server_url
    headers = {"Content-Type": "application/json"}

    try:
        # Make the POST request
        response = requests.post(api_url, json=data_to_post, headers=headers)
        response.raise_for_status()

        # Parse the JSON response content
        response_data = response.json()
        json_response = json.dumps(response_data, indent=4)
        
        return_message = response_data["returnStateInfo"]["returnMessage"]

        # Handle the response status code
        if response.status_code == 200 and return_message == "SUCCESS":
            frappe.msgprint("Credit Note Cancelled successfully.")

            # Print the response status code and content
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Content: {response.text}")

            # Extract and decode the 'content' string
            encoded_content = response_data["data"]["content"]
            decoded_content = base64.b64decode(encoded_content).decode("utf-8")

            print("Decoded Content:")
            print(decoded_content)

            # Log the successful integration request
            log_integration_request('Completed', api_url, headers, data_to_post, response_data)

        else:
            # Log the failed integration request
            log_integration_request('Failed', api_url, headers, data_to_post, response_data, return_message)
            frappe.throw(title="Oops! API Error", msg=return_message)
            doc.docstatus = 0


    except requests.exceptions.RequestException as e:
        # Log the failed integration request
        log_integration_request('Failed', api_url, headers, data_to_post, {}, str(e))
        frappe.throw(f"Request failed: {e}")
        doc.docstatus = 0
        doc.save()

    # except json.JSONDecodeError as e:
    #     # Handle JSON decoding errors
    #     log_integration_request('Failed', api_url, headers, data_to_post, {}, f"JSON decode error: {e}")
    #     frappe.throw(f"JSON decode error: {e}")
    #     doc.docstatus = 0
    #     doc.save()
    # except base64.binascii.Error as e:
    #     # Handle base64 decoding errors
    #     log_integration_request('Failed', api_url, headers, data_to_post, {}, f"Base64 decode error: {e}")
    #     frappe.throw(f"Base64 decode error: {e}")
    #     # Set the document status to 'Draft'
    #     doc.docstatus = 0  # 0 represents 'Draft' status
    #     doc.save()
