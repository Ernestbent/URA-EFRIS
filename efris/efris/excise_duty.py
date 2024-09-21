import base64
import json
import gzip
import requests
from datetime import datetime, timedelta, timezone
import frappe
from frappe.utils.data import now

# Define the East Africa Time (EAT) timezone, which is UTC+3
eat_timezone = timezone(timedelta(hours=3))

# Gzip decompression utility
def decompress_gzip(data):
    try:
        decompressed_data = gzip.decompress(data)
        return decompressed_data.decode('utf-8')
    except Exception as e:
        log_error("decompress_gzip", f"Error Decompressing Gzip data: {e}")
        return None

# Log integration request to ERPNext
def log_integration_request(status, url, headers, data, response, error=""):
    valid_statuses = ["", "Queued", "Authorized", "Completed", "Cancelled", "Failed"]
    if status not in valid_statuses:
        status = "Failed"  # Default to "Failed" if status is invalid

    try:
        integration_request = frappe.get_doc({
            "doctype": "Integration Request",
            "integration_type": "Remote",
            "is_remote_request": True,
            "integration_request_service": "Excise Duty Query",
            "method": "POST",
            "status": status,
            "url": url,
            "request_headers": json.dumps(headers, indent=4),
            "data": json.dumps(data, indent=4),
            "output": json.dumps(response, indent=4),
            "error": error,
            "execution_time": now()
        })
        integration_request.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"Integration request logged with status: {status}")
    except Exception as e:
        print(f"Failed to log integration request: {e}")

# Error logging
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
def query_excise_duty_items():
    def get_current_datetime():
        now = datetime.now(eat_timezone)
        formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_datetime

    current_time = get_current_datetime()

    # Fetch company information
    company = frappe.defaults.get_user_default("company")
    if not company:
        frappe.throw("No default company set for the current session")

    # Get Efris settings
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

    # Prepare request data
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
            "interfaceCode": "T125",
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

    # Make the API request
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()

        # Process and decompress response
        compressed_data = response_json["data"]["content"]
        decoded_data = base64.b64decode(compressed_data)
        decompressed_data = decompress_gzip(decoded_data)

        if decompressed_data:
            json_data = json.loads(decompressed_data)
            print("Decompressed JSON:", json.dumps(json_data, indent=4))

            # Create Excise Duty Items
            create_excise_duty_items(json_data)

        log_integration_request('Completed', url, headers, data, response_json)

        return {
            "status": "success",
            "message": response_json
        }

    except requests.exceptions.RequestException as e:
        log_integration_request('Failed', url, headers, data, {}, str(e))
        log_error("query_excise_duty_items", f"API request failed: {e}", str(e))
        return {
            "status": "failed",
            "message": str(e)
        }

def create_excise_duty_items(json_data):
    try:
        excise_duty_list = json_data.get("exciseDutyList", [])

        if not excise_duty_list:
            print("No excise duty data found.")
            return

        for excise_duty in excise_duty_list:
            print(f"Processing Excise Duty: {excise_duty}")

            # Create a new document for each excise duty item
            excise_duty_doc = frappe.new_doc("Excise Duty_Code Items")

            # Access and set the fields from the excise_duty dictionary
            excise_duty_doc.date_format = excise_duty.get("dateFormat", "")
            excise_duty_doc.effective_date = excise_duty.get("effectiveDate", "")
            excise_duty_doc.excise_duty_code = excise_duty.get("exciseDutyCode", "")

            # Access and set the specific fields from the excise_duty dictionary
            excise_duty_doc.good_service = excise_duty.get("goodService", "")
            excise_duty_doc.isleafnode = excise_duty.get("isLeafNode", "")
            excise_duty_doc.item_id = excise_duty.get("id", "")
            excise_duty_doc.item_page_size = excise_duty.get("pageSize", "")
            excise_duty_doc.parent_code = excise_duty.get("parentCode", "")
            excise_duty_doc.ratetext = excise_duty.get("rateText", "")
            # excise_duty_doc.time_format = excise_duty.get("timeFormat", "")

                        # Process the exciseDutyDetailsList
            excise_duty_details_list = excise_duty.get("exciseDutyDetailsList", [])

            if isinstance(excise_duty_details_list, list):
                for detail in excise_duty_details_list:
                    # First dictionary processing
                    if detail.get("currency") is None:  # Check if it's from the first dict
                        excise_duty_doc.object_dateformat = detail.get("dateFormat", "")
                        excise_duty_doc.excise_duty_id = detail.get("exciseDutyId", "")
                        excise_duty_doc.id = detail.get("id", "")
                        excise_duty_doc.now_time = detail.get("nowTime", "")
                        excise_duty_doc.page_index = detail.get("pageIndex", "")
                        excise_duty_doc.page_no = detail.get("pageNo", "")
                        excise_duty_doc.page_size = detail.get("pageSize", "")
                        excise_duty_doc.rate = detail.get("rate", "")
                        excise_duty_doc.time_format = detail.get("timeFormat", "")
                        excise_duty_doc.type = detail.get("type", "")

                    # Second dictionary processing
                    else:  # If currency exists, it's from the second dict
                        excise_duty_doc.currency = detail.get("currency", "")
                        excise_duty_doc.c_dateformat = detail.get("dateFormat", "")
                        excise_duty_doc.c_excisedutyid = detail.get("exciseDutyId", "")
                        excise_duty_doc.c_id = detail.get("id", "")
                        excise_duty_doc.c_timeformat = detail.get("timeFormat", "")
                        excise_duty_doc.c_type = detail.get("type", "")
                        excise_duty_doc.c_nowtime = detail.get("nowTime", "")
                        excise_duty_doc.c_pageindex = detail.get("pageIndex", "")
                        excise_duty_doc.c_pageno = detail.get("pageNo", "")
                        excise_duty_doc.c_pagesize = detail.get("pageSize", "")
                        excise_duty_doc.c_rate = detail.get("rate", "")
                        excise_duty_doc.c_unit = detail.get("unit", "")

            

            else:
                print(f"exciseDutyDetailsList is not a list for Excise Duty: {excise_duty}")

            # Insert the document into the database
            excise_duty_doc.insert(ignore_permissions=True)
            print(f"Excise Duty Item for ID {excise_duty.get('exciseDutyId', '')} inserted.")

        frappe.db.commit()
        print("Excise Duty Items created successfully.")

    except Exception as e:
        log_error("create_excise_duty_items", f"Error creating Excise Duty items: {e}")
        print(f"An error occurred: {e}")
