import json
import base64
import requests
from datetime import datetime, timedelta, timezone
import frappe

# Define the East Africa Time (EAT) timezone
eat_timezone = timezone(timedelta(hours=3))

def log_integration_request(status, url, headers, data, response, error=""):
    """
    Log integration requests with their details to the Integration Request doctype.
    """
    valid_statuses = ["", "Queued", "Authorized", "Completed", "Cancelled", "Failed"]
    status = status if status in valid_statuses else "Failed"
    
    try:
        integration_request = frappe.get_doc({
            "doctype": "Integration Request",
            "integration_type": "Remote",
            "method": "POST",
            "integration_request_service": "Query Verification Code For Credit Note Number",
            "is_remote_request": True,
            "status": status,
            "url": url,
            "request_headers": json.dumps(headers),
            "data": json.dumps(data),
            "output": json.dumps(response),
            "error": error,
            "execution_time": datetime.now(eat_timezone).strftime("%Y-%m-%d %H:%M:%S")
        })
        
        integration_request.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.throw(f"Error logging integration request: {str(e)}")

@frappe.whitelist()
def query_verification_code_cn(custom_credit_note_number=None):
    
    company = frappe.defaults.get_user_default("company")
    if not company:
        frappe.throw("No default company set for the current session")

    efris_settings_list = frappe.get_all("Efris Settings", filters={"custom_company": company}, limit=1)
    if not efris_settings_list:
        frappe.throw(f"No Efris Settings found for the company {company}")

    efris_settings_doc_name = efris_settings_list[0].name
    efris_settings_doc = frappe.get_doc("Efris Settings", efris_settings_doc_name)

    device_number = efris_settings_doc.custom_device_number
    tin = efris_settings_doc.custom_tax_payers_tin
    server_url = efris_settings_doc.custom_server_url

    current_time = datetime.now(eat_timezone).strftime("%Y-%m-%d %H:%M:%S")

    data_to_post = {
        "invoiceNo": custom_credit_note_number,
    }
    
    json_string = json.dumps(data_to_post)
    encoded_data = base64.b64encode(json_string.encode("utf-8")).decode("utf-8")

    data = {
        "data": {
            "content": encoded_data,
            "signature": "",
            "dataDescription": {"codeType": "0", "encryptionCode": "1", "zipCode": "0"},
        },
        "globalInfo": {
            "appId": "AP04",
            "version": "1.1.20191201",
            "dataExchangeId": "1",
            "interfaceCode": "T108",
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
        "returnStateInfo": {"returnCode": "", "returnMessage": ""},
    }

    headers = {'Content-Type': "application/json"}

    try:
        response = requests.post(server_url, json=data, headers=headers)
        response_data = response.json()
        return_message = response_data["returnStateInfo"].get("returnMessage", "Unknown error")
        
        if response.status_code == 200 and return_message == "SUCCESS":
            content = response_data["data"].get("content", "")
            if content:
                decoded_bytes = base64.b64decode(content)
                decoded_string = decoded_bytes.decode('utf-8')
                decoded_data = json.loads(decoded_string)
                
                # Print values for debugging
                print(f"Decoded Data: {decoded_data}")  # Print the entire decoded data
                try:
                    verification_code = decoded_data["records"][0].get("antifakeCode", "N/A")
                    print(f"Verification Code: {verification_code}")
                except KeyError as e:
                    print(f"KeyError: Missing expected field in response - {str(e)}")

                log_integration_request('Completed', server_url, headers, data, response_data)
                return {
                    "status": "success",
                    "verification_code": verification_code
                }
            else:
                log_integration_request('Failed', server_url, headers, data, response_data, "Missing content")
                return {"status": "failed", "message": "Missing content in API response"}
        else:
            log_integration_request('Failed', server_url, headers, data, response_data, return_message)
            return {"status": "failed", "message": f"API call failed: {return_message}"}
    
    except requests.exceptions.RequestException as e:
        log_integration_request('Failed', server_url, headers, data, {}, str(e))
        return {"status": "failed", "message": str(e)}
