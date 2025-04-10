import base64
from datetime import datetime, timezone, timedelta
import frappe
import requests
import json

# Specify the East Africa Time (EAT) timezone
eat_timezone = timezone(timedelta(hours=3))  # UTC+3


def on_stock(doc, event):
    # Check if checkbox is checked
    if not doc.custom_efris_pi:
        return

    date_str = doc.posting_date  # Assuming doc.posting_date holds the date string
    time_str = doc.posting_time  # Assuming doc.posting_time holds the time string

    # Concatenate the date and time strings to form one string
    datetime_combined = date_str + " " + time_str
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
    items_data = []
    goods_stock_in_items = []

    for item in doc.items:
        item_data = {
            "item_name": item.item_name,
            "item_code": item.item_code,
            "qty": item.qty,
            "rate": item.rate,
            "uom": item.uom,
            "amount": item.amount,
            "description": item.description,
            "item_tax_template": item.item_tax_template,
            "custom_uom_code": item.custom_uom_code,
        }
        items_data.append(item_data)
        stock_in_type_mapping = {
            "Import": "101",
            "Local Purchase": "102",
            "Manufacturing/Assembling": "103",
            "Opening Stock": "104",
        }

        # Fetch the selected type from the ERPNext field
        selected_type = doc.custom_stock_in_type  # Assuming 'custom_stock_in_type' is a field in the ERPNext document
        stock_in_type = stock_in_type_mapping.get(selected_type, "")

        goods_stock_in_item = {
            "commodityGoodsId": "",
            "goodsCode": item.item_code,
            "measureUnit": item.custom_uom_code,
            "quantity": item.qty,
            "unitPrice": item.rate,
            "remarks": "",
            "fuelTankId": "",
            "lossQuantity": "",
            "originalQuantity": "",
        }
        goods_stock_in_items.append(goods_stock_in_item)


    data = {
        "goodsStockIn": { 
            "operationType": "101",
            "supplierTin": doc.tax_id,
            "supplierName": doc.supplier_name,
            "adjustType": "",
            "remarks": "Increase Inventory",
            "stockInDate": doc.posting_date,
            "stockInType": stock_in_type,
            "productionBatchNo": "",
            "productionDate": "",
            "branchId": "",
            "invoiceNo": doc.bill_no,
            "isCheckBatchNo": "0",
            "rollBackIfError": "0",
            "goodsTypeCode": "101",
        },
        "goodsStockInItem": goods_stock_in_items,
    }

    json_string = json.dumps(data)
    encoded_json = base64.b64encode(json_string.encode("utf-8")).decode("utf-8")

    def log_integration_request(status, url, headers, data, response, error=""):
        valid_statuses = ["", "Queued", "Authorized", "Completed", "Cancelled", "Failed"]
        if status not in valid_statuses:
            status = "Failed"  # Default to "Failed" if status is invalid

        integration_request = frappe.get_doc({
            "doctype": "Integration Request",
            "integration_type": "Remote",
            "integration_request_service":"Goods Stock Maintain",
            "is_remote_request":True,
            "method": "POST",
            "status": status,
            "url": url,
            "request_headers": json.dumps(headers, indent=4),
            "data": json.dumps(data, indent=4),
            "output": json.dumps(response, indent=4),
            "error": error,
            "execution_time": datetime.now()
        })
        integration_request.insert(ignore_permissions=True)  # This line inserts the integration request into ERPNext
        frappe.db.commit()

    try:
        data_to_post = {
            "data": {
                "content": encoded_json,
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
                "interfaceCode": "T131",
                "requestCode": "TP",
                "requestTime": datetime_combined,
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

        print(f"Request Data: {json.dumps(data_to_post, indent=4)}")
        doc.custom_post_request = json.dumps(data_to_post, indent=4)

        api_url = server_url  # Replace with your actual endpoint
        headers = {'Content-Type': 'application/json'}
        response = requests.post(api_url, json=data_to_post, headers=headers)
        response.raise_for_status()

        response_data = json.loads(response.text)
        json_response = json.dumps(response_data, indent=4)  # Convert the parsed JSON object to a JSON string
        doc.custom_response_ = json_response  # Save the JSON string in the document

        return_message = response_data["returnStateInfo"]["returnMessage"]
        doc.custom_return_status = return_message

        # Log the successful integration request
        log_integration_request('Completed', api_url, headers, data_to_post, response_data)

        if response.status_code == 200 and return_message == "SUCCESS":
            frappe.msgprint("Thanks, your stock has been successfully recorded in EFIRS.")
        elif return_message == "Partial failure!":
            encoded_content = response_data["data"]["content"]
            decoded_content = base64.b64decode(encoded_content).decode("utf-8")
            data = json.loads(decoded_content)
            erroMessage = data[0]["returnMessage"]
            frappe.throw(title="", msg=erroMessage)
        else:
            # Log failure and throw an exception with the return message
            log_integration_request('Failed', server_url, headers, data_to_post, response_data, return_message)
            frappe.throw(title="EFRIS API Error", msg=f"{return_message}")

            doc.docstatus = 0
            doc.save()
    except requests.exceptions.RequestException as e:
        # Log the failed integration request
        log_integration_request('Failed', api_url, headers, data_to_post, {}, str(e))

        frappe.msgprint(f"Error making API request: {e}")
        doc.docstatus = 0
        doc.save()
