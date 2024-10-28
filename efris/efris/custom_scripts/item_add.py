import frappe
import requests
import json
from datetime import datetime, timezone, timedelta
import base64

# Define the East Africa Time (EAT) timezone, which is UTC+3
eat_timezone = timezone(timedelta(hours=3))

def log_integration_request(status, url, headers, data, response, error=""):
    valid_statuses = ["", "Queued", "Authorized", "Completed", "Cancelled", "Failed"]
    status = status if status in valid_statuses else "Failed"
    
    integration_request = frappe.get_doc({
        "doctype": "Integration Request",
        "integration_type": "Remote",
        "method": "POST",
        "integration_request_service": "Goods Upload",
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

@frappe.whitelist()
def on_save(doc, event):
    if not doc.custom_efris_item:
        return
    
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

    operation_type = doc.custom_registermodify_item
    
    data = [
        {
            "operationType": operation_type,
            "goodsName": doc.item_name,
            "goodsCode": doc.item_code,
            "measureUnit": doc.custom_uom_code_efris,  # Example field, adjust as needed
            "unitPrice": doc.standard_rate,
            "currency": "101",  # Assuming default currency code
            "commodityCategoryId": doc.custom_goods_category_id,
            "haveExciseTax": doc.custom_has_excise_tax,  # Assuming default value
            "description": doc.description,
            "stockPrewarning": "10",  # Assuming default value
            "pieceMeasureUnit": "",
            "havePieceUnit": "102",  # Assuming default value
            "pieceUnitPrice": "",
            "exciseDutyCode": doc.custom_excise_duty_code,
            "haveOtherUnit": "",
            "goodsTypeCode": "101",  # Assuming default value
            "goodsOtherUnits": [],
        }
    ]

    json_string = json.dumps(data)
    encoded_json = base64.b64encode(json_string.encode("utf-8")).decode("utf-8")

    current_time = datetime.now(eat_timezone).strftime("%Y-%m-%d %H:%M:%S")
    data_to_post = {
        "data": {
            "content": encoded_json,
            "signature": "",
            "dataDescription": {
                "codeType": "0",
                "encryptCode": "1",
                "zipCode": "0"
            },
        },
        "globalInfo": {
            "appId": "AP04",
            "version": "1.1.20191201",
            "dataExchangeId": "9230489223014123",
            "interfaceCode": "T130",
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
            "extendField": {
                "responseDateFormat": "dd/MM/yyyy",
                "responseTimeFormat": "dd/MM/yyyy HH:mm:ss",
                "referenceNo": "24PL01000221",
                "operatorName": "administrator",
            },
        },
        "returnStateInfo": {
            "returnCode": "",
            "returnMessage": ""
        }
    }

    try:
        api_url = server_url
        headers = {"Content-Type": "application/json"}
        response = requests.post(api_url, json=data_to_post, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        return_message = response_data["returnStateInfo"]["returnMessage"]
        
        if response.status_code == 200 and return_message == "SUCCESS":
            if operation_type == "101":
                frappe.msgprint("Item successfully created in EFRIS.")
            elif operation_type == "102":
                frappe.msgprint("Item modified successfully in EFRIS.")
            else:
                frappe.msgprint("Operation successfully completed with EFRIS.")
            log_integration_request('Completed', api_url, headers, data_to_post, response_data)
        else:
            frappe.throw(
                title="Oops! API Error",
                msg=return_message
            )
            doc.status = 0  # Set the document status to 'Draft'
            log_integration_request('Failed', api_url, headers, data_to_post, response_data, return_message)
            
    except requests.exceptions.RequestException as e:
        frappe.msgprint(f"Error making API request: {e}")
        doc.status = 0  # Set the document status to 'Draft'
        log_integration_request('Failed', api_url, headers, data_to_post, {}, str(e))
