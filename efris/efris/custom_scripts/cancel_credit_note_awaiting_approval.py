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
            "integration_request_service": "Cancel Credit Note Awaiting Approval",
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
def cancel_credit_note_awaiting_ap(custom_id=None):
    if not custom_id:
        frappe.throw("Custom ID is required")

    company = frappe.defaults.get_user_default("company")
    if not company:
        frappe.throw("No default company set for the current session")

    efris_settings_list = frappe.get_all("Efris Settings", filters={"custom_company": company}, limit=1)
    if not efris_settings_list:
        frappe.throw(f"No Efris Settings found for the company {company}")

    efris_settings_doc = frappe.get_doc("Efris Settings", efris_settings_list[0].name)
    server_url = efris_settings_doc.custom_server_url
    device_number = efris_settings_doc.custom_device_number
    tin = efris_settings_doc.custom_tax_payers_tin

    current_time = datetime.now(eat_timezone).strftime("%Y-%m-%d %H:%M:%S")

    # Find the Sales Invoice using the custom ID
    sales_invoice = frappe.get_all("Sales Invoice", filters={"name": custom_id}, limit=1)
    if not sales_invoice:
        frappe.throw(f"No Sales Invoice found with ID {custom_id}")

    sales_invoice_doc = frappe.get_doc("Sales Invoice", custom_id)

    if sales_invoice_doc.docstatus != 1:
        frappe.throw("Only submitted Sales Invoices can be cancelled")

    # Prepare data for API request
    data_to_post = {"id": custom_id}
    encoded_data = base64.b64encode(json.dumps(data_to_post).encode("utf-8")).decode("utf-8")

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
            "interfaceCode": "T118",
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

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(server_url, json=data, headers=headers)
        response_data = response.json()
        return_message = response_data["returnStateInfo"].get("returnMessage", "Unknown error")

        if response.status_code == 200 and return_message == "SUCCESS":
            content = response_data["data"].get("content", "")
            if content:
                decoded_data = json.loads(base64.b64decode(content).decode("utf-8"))
                
                # Log API request
                log_integration_request("Completed", server_url, headers, data, response_data)

                # Cancel the Sales Invoice
                sales_invoice_doc.cancel()
                frappe.db.commit()

                return {"status": "success", "message": "Credit Note cancelled successfully"}
            else:
                log_integration_request("Failed", server_url, headers, data, response_data, "Missing content")
                return {"status": "failed", "message": "Missing content in API response"}
        else:
            log_integration_request("Failed", server_url, headers, data, response_data, return_message)
            return {"status": "failed", "message": f"API call failed: {return_message}"}

    except requests.exceptions.RequestException as e:
        log_integration_request("Failed", server_url, headers, data, {}, str(e))
        return {"status": "failed", "message": str(e)}
