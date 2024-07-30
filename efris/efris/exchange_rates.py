import base64
import json
import frappe
import requests
from datetime import datetime
from datetime import datetime, timedelta, timezone

# Define the East Africa Time (EAT) timezone, which is UTC+3
eat_timezone = timezone(timedelta(hours=3))

# Get the current time in EAT
current_time = datetime.now(eat_timezone).strftime("%Y-%m-%d %H:%M:%S")

print("Current time in Uganda (EAT):", current_time)


def log_integration_request(status, url, headers, data, response, error=""):
    valid_statuses = ["", "Queued", "Authorized", "Completed", "Cancelled", "Failed"]
    if status not in valid_statuses:
        status = "Failed"  # Default to "Failed" if status is invalid

    try:
        integration_request = frappe.get_doc({
            "doctype": "Integration Request",
            "integration_type": "Remote",
            "is_remote_request":True,
            "integration_request_service":"System Dictionary Update",
            "method": "POST",
            "status": status,
            "url": url,
            "request_headers": json.dumps(headers),
            "data": json.dumps(data),
            "output": json.dumps(response),
            "error": error,
            "execution_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        integration_request.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"Integration request logged with status: {status}")
    except Exception as e:
        print(f"Failed to log integration request: {e}")

def log_error(method, error_message, traceback=None):
    try:
        error_log = frappe.get_doc({
            "doctype": "Error Log",
            "method": method,
            "error": error_message,
            "traceback": traceback
        })
        error_log.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"Error logged: {error_message}")
    except Exception as e:
        print(f"Failed to log error: {e}")

@frappe.whitelist()
def get_exchange_rates():
    frappe.logger().info("get_exchange_rates method called")
    


    company = frappe.defaults.get_user_default("company")
    if not company:
        frappe.throw("No default company set for the current session")

    efris_settings_list = frappe.get_all("Efris Settings", filters={"custom_company": company}, limit=1)
    if not efris_settings_list:
        frappe.throw(f"No Efris Settings found for the company {company}")

    efris_settings_doc_name = efris_settings_list[0].name
    doc = frappe.get_doc("Efris Settings", efris_settings_doc_name)
    
    device_number = doc.custom_device_number
    tin = doc.custom_tax_payers_tin
    server_url = doc.custom_server_url
    url = server_url

    headers = {
        'Content-Type': 'application/json',
    }

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
            "interfaceCode": "T126",
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
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        response_json = response.json()
        log_integration_request('Completed', url, headers, data, response_json)

        if "data" in response_json and "content" in response_json["data"]:
            encoded_content = response_json["data"]["content"]
            decoded_content = base64.b64decode(encoded_content).decode("utf-8")
            print(decoded_content)

            try:
                content_dict = json.loads(decoded_content)
            except json.JSONDecodeError as je:
                log_error("get_exchange_rates", f"Error decoding JSON content: {je}", str(je))
                frappe.throw(f"Error decoding JSON content: {je}")
            
            print(content_dict)

            if isinstance(content_dict, list):
                for rate in content_dict:
                    insert_or_update_currency_exchange(doc, rate)
            elif isinstance(content_dict, dict):
                for rate in content_dict.get("currency", []):
                    insert_or_update_currency_exchange(doc, rate)
            else:
                frappe.throw("Unexpected content format in decoded JSON")
            
            doc.custom_exchange_rates = json.dumps(content_dict, indent=4)
            doc.save()
            
            return {"status": "success"}
        else:
            return {"status": "failure", "message": "No content found in the response"}
        
    except requests.exceptions.RequestException as e:
        log_integration_request('Failed', url, headers, data, {}, str(e))
        log_error("get_exchange_rates", f"API request failed: {e}", str(e))
        return {"status": "failure", "message": str(e)}
    
def insert_or_update_currency_exchange(doc, rate):
    from_currency = rate.get("currency", "")
    to_currency = "UGX"
    date = rate.get("nowTime", "")

    if from_currency != "UGX" or to_currency != "UGX":
        existing_doc = frappe.get_all("Currency Exchange", filters={"from_currency": from_currency, "to_currency": to_currency, "date": date}, limit=1)
        if existing_doc:
            exchange_rate_doc = frappe.get_doc("Currency Exchange", existing_doc[0].name)
            exchange_rate_doc.exchange_rate = rate.get("rate")
            exchange_rate_doc.save()
            print(f"Currency Exchange document updated for {from_currency}")
        else:
            exchange_rate_doc = frappe.new_doc("Currency Exchange")
            exchange_rate_doc.from_currency = from_currency
            exchange_rate_doc.date = date
            exchange_rate_doc.exchange_rate = rate.get("rate")
            exchange_rate_doc.to_currency = to_currency 
            exchange_rate_doc.insert()
            print(f"Currency Exchange document inserted for {from_currency}")
    else:
        print(f"Skipping Currency Exchange document insertion for {from_currency} and {to_currency} pair as both are UGX")
