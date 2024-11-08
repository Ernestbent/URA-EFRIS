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
    
    # Log the request data to help with debugging
    print(f"Logging integration request: {status}, {url}, {headers}, {data}, {response}, {error}")
    
    try:
        # Create the Integration Request doc
        integration_request = frappe.get_doc({
            "doctype": "Integration Request",
            "integration_type": "Remote",
            "method": "POST",
            "integration_request_service": "Customer TIN Validation",
            "is_remote_request": True,
            "status": status,
            "url": url,
            "request_headers": json.dumps(headers),
            "data": json.dumps(data),
            "output": json.dumps(response),
            "error": error,
            "execution_time": datetime.now(eat_timezone).strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Insert and commit the request to the database
        integration_request.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Log success
        print("Integration request logged successfully.")
    except Exception as e:
        # Log the error if insertion fails
        print(f"Error logging integration request: {str(e)}")
        frappe.throw(f"Error logging integration request: {str(e)}")

def query_tax_payer_info(doc, event):
    

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
    
    data_to_post = {
        "ninBrn": doc.nin,
        "tin": doc.tin
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

        # Access the return message from the response
        return_message = response_data["returnStateInfo"].get("returnMessage", "Unknown error")
        
        # Check for success (status code 200) and handle the response
        if response.status_code == 200 and return_message == "SUCCESS":
            # Get the response payload
            response_payload = json.dumps(response_data)
            print(response_payload)

            # Access the encoded information in the response payload from Ura 
            content = response_data["data"].get("content", "")

            # Decode the Base64-encoded content
            if content:
                decoded_bytes = base64.b64decode(content)

                # Convert bytes to a string (usually UTF-8)
                decoded_string = decoded_bytes.decode('utf-8')

                # Step 2: Convert the decoded string to a dictionary
                decoded_data = json.loads(decoded_string)
                doc.information = decoded_string  # Store the decoded data
              
                
                
                
                # Print the decoded string
                print(decoded_string)
                frappe.msgprint("Success")
                log_integration_request('Completed', server_url, headers, data, response_data)
            else:
                # If content is missing, log and proceed
                log_integration_request('Failed', server_url, headers, data, response_data, "Missing content")
                frappe.msgprint("Content not found in response")
        else:
            # Log failure and throw an exception with the return message
            log_integration_request('Failed', server_url, headers, data, response_data, return_message)
            frappe.throw(f"Oops->{return_message}")
            doc.status = 0  # Set the document status to 'Draft'
            doc.save()
    except requests.exceptions.RequestException as e:
        # Handle request exceptions (e.g., network errors)
        log_integration_request('Failed', server_url, headers, data, {}, str(e))
        frappe.throw(f"An error occurred while making the API request: {str(e)}")
        doc.docstatus = 0  # Set the document status to 'Draft'
