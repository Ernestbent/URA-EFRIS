from io import BytesIO
import json
import os
import tempfile
import frappe
from frappe.model.document import Document
from frappe.utils.data import image_to_base64
import requests
import random
import base64
from datetime import datetime, timedelta
import json
import frappe
from frappe.model.document import Document
import requests
import uuid
from datetime import datetime, timezone, timedelta

# Example events.py
import random


# Specify the East Africa Time (EAT) timezone
eat_timezone = timezone(timedelta(hours=3))  # UTC+3

# Get the current time in the EAT timezone
current_time = datetime.now(eat_timezone).strftime("%Y-%m-%d %H:%M:%S")
print("Current time in Uganda (EAT):", current_time)


def generate_unique_reference_number():
    return str(uuid.uuid4().int)[:10]  # Extract the first 10 digits of the UUID


unique_reference_number = generate_unique_reference_number()


def generate_random_8_digits():
    return random.randint(10000000, 99999999)


# Example usage
random_8_digits = generate_random_8_digits()

def log_integration_request(status, url, headers, data, response, error=""):
    valid_statuses = ["", "Queued", "Authorized", "Completed", "Cancelled", "Failed"]
    status = status if status in valid_statuses else "Failed"
    
    integration_request = frappe.get_doc({
        "doctype": "Integration Request",
        "integration_type": "Remote",
        "method": "POST",
        "integration_request_service":"Goods Upload/Credit Note Issue",
        "is_remote_request":True,
        "status": status,
        "url": url,
        "request_headers": json.dumps(headers, indent=4),
        "data": json.dumps(data, indent=4),
        "output": json.dumps(response, indent=4),
        "error": error,
        "execution_time": datetime.now()
    })
    integration_request.insert(ignore_permissions=True)
    frappe.db.commit()

# Hooking into the on-submit controller
def on_send(doc, event):
    if not doc.custom_efris_invoice:

        
        return
    # Example values from variables
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
    legal_name = efris_settings_doc.custom_legal_name
    business_name = efris_settings_doc.custom_business_name
    place_of_business = efris_settings_doc.custom_place_of_businesss
    email_id = efris_settings_doc.custom_email_address
    mobile_phone = efris_settings_doc.custom_mobile_phone
    line_phone = efris_settings_doc.custom_line_phone
    address = efris_settings_doc.custom_address
    

    def generate_unique_reference_number():
        return str(uuid.uuid4().int)[:10]  # Extract the first 10 digits of the UUID

    unique_reference_number = generate_unique_reference_number()

    def generate_random_8_digits():
        return random.randint(10000000, 99999999)

    # Example usage
    random_8_digits = generate_random_8_digits()

    items_data = []
    goods_details = []
    # Initialize goods_details list outside
    tax_categories = {}
    # Track the number of items created
    item_count = 0

    # Iterate through each item in the 'items' child table
    for item in doc.items:
        item_count += 1

        # Collect item details in a dictionary
        item_data = {
            "item_name": item.item_name,
            "item_code": item.item_code,
            # 'custom_goods_category': item.custom_goods_category,
            "qty": item.qty,
            "rate": item.rate,
            "uom": item.uom,
            "amount": item.amount,
            "description": item.description,
            "goods_category_id":item.custom_goods_category_id,
            "item_tax_template":item.item_tax_template,
            "discount_amount":item.discount_amount,
            "discount_percentage":item.discount_percentage
        }
        # Append the item_data dictionary to the items_data list
        items_data.append(item_data)

        # Check if 'exempt' is in the item_tax_template
        if item.item_tax_template.startswith("Exempt"):
            tax_rate = "-"
            tax_category_code = "03"
            tax = 0
            grossAmount = item.amount
            taxAmount = 0
            netAmount = item.amount
        elif item.item_tax_template.startswith("Zero"):
            tax_rate = 0
            tax_category_code = "02"
            tax = 0
            grossAmount = item.amount
            taxAmount = 0
            netAmount = item.amount

        else:
            tax_category_code = "01"
            tax_rate = "0.18"
            tax = round((18 / 118) * item.qty * item.rate, 2)
            grossAmount = item.amount
            taxAmount = round(((18 / 118) * item.amount), 2)
            netAmount = grossAmount - tax

        # Check if tax template already exists in tax_categories dictionary
        if item.item_tax_template in tax_categories:
            # Update values for existing tax template
            tax_categories[item.item_tax_template]["grossAmount"] += item.amount
            tax_categories[item.item_tax_template]["taxAmount"] += taxAmount
            tax_categories[item.item_tax_template]["netAmount"] += netAmount
            # Create goods_detail dictionary
        else:
            # Create new entry for tax template
            tax_categories[item.item_tax_template] = {
                "taxCategoryCode": tax_category_code,
                "netAmount": netAmount,
                "taxRate": tax_rate,
                "taxAmount": taxAmount,
                "grossAmount": item.amount,
                "exciseUnit": "",
                "exciseCurrency": "",
                "taxRateName": "",
            }
            # Round off the netAmount after completing all calculations
        for category in tax_categories.values():
            category["netAmount"] = round(category["netAmount"], 2)
            category["taxAmount"] = round(category["taxAmount"], 2)

            # Convert tax_categories dictionary to a list
        tax_categories_list = list(tax_categories.values())
        print(f"Rate: {item.item_tax_template}")

        

        goods_detail = {
        "item": item.item_name,
        "itemCode": item.item_code,
        "qty": item.qty,
        "unitOfMeasure": item.custom_uom_codeefris,
        "unitPrice": item.rate,
        "total": item.amount,
        "taxRate": tax_rate,
        "tax": tax,
        "discountTotal": item.discount_amount,
        "discountTaxRate": item.discount_percentage,
        "orderNumber": str(len(goods_details)),
        "discountFlag": "1" if item.discount_amount else "2",  # Set to '1' if discountTotal exists
        "deemedFlag": "2",
        "exciseFlag": "2",
        "categoryId": "",
        "categoryName": "",
        "goodsCategoryId": item.custom_goods_category_id,
        "goodsCategoryName": "",
        "exciseRate": "",
        "exciseRule": "",
        "exciseTax": "",
        "pack": "",
        "stick": "",
        "exciseUnit": "",
        "exciseCurrency": "",
        "exciseRateName": "",
        "vatApplicableFlag": "1",
    }


        goods_details.append(goods_detail)

        total_tax_amount = sum(
            tax_category["taxAmount"] for tax_category in tax_categories_list
        )

        print("\n\n\n\n")
        linked_doc = frappe.get_doc("Sales Taxes and Charges Template", doc.taxes)
        for taxes in linked_doc.taxes:
            taxes = {
                # 'rate': taxes.rate,
                "tax_amount": taxes.tax_amount,
                # Add other fields from the 'taxes' table as needed
            }

    json_data = [
        {
            "sellerDetails": {
                "tin": tin,
                "ninBrn": "",
                "legalName": legal_name,
                "businessName": business_name,
                "address": address,
                "mobilePhone": mobile_phone,
                "linePhone": line_phone,
                "emailAddress": email_id,
                "placeOfBusiness": place_of_business,
                "referenceNo": unique_reference_number,
                "branchId": "",
                "isCheckReferenceNo": "",
            },
            "basicInformation": {
                "invoiceNo": "",
                "antifakeCode": "",
                "deviceNo": device_number,
                "issuedDate": datetime_combined,
                "operator": legal_name,
                "currency": doc.currency,
                "oriInvoiceId": "1",
                "invoiceType": "1",
                "invoiceKind": "1",
                "dataSource": "106",
                "invoiceIndustryCode": "",
                "isBatch": "0",
            },
            "buyerDetails": {
                "buyerTin": doc.tax_id,
                "buyerNinBrn": "",
                "buyerPassportNum": "",
                "buyerLegalName": doc.customer,
                "buyerBusinessName": doc.customer,
                "buyerAddress": "",
                "buyerEmail": doc.custom_email_id,
                "buyerMobilePhone": "",
                "buyerLinePhone": "",
                "buyerPlaceOfBusi": "",
                "buyerType": "1",
                "buyerCitizenship": "",
                "buyerSector": "1",
                "buyerReferenceNo": "",
            },
            "buyerExtend": {
                "propertyType": "abc",
                "district": "",
                "municipalityCounty": "",
                "divisionSubcounty": "",
                "town": "",
                "cellVillage": "",
                "effectiveRegistrationDate": "",
                "meterStatus": "",
            },
            "goodsDetails": goods_details,
            "taxDetails": tax_categories_list,
            "summary": {
                "netAmount": round((doc.total - total_tax_amount), 2),
                "taxAmount": round(total_tax_amount, 2),
                "grossAmount": doc.total,
                "itemCount": item_count,
                "modeCode": "0",
                "remarks": "We appreciate your continued support",
                "qrCode": "",
            },
            "payWay": {
                "paymentMode": "102",
                "paymentAmount": doc.total,
                "orderNumber": "a",
            },
            "extend": {"reason": "reason", "reasonCode": "102"},
            "importServicesSeller": {
                "importBusinessName": "",
                "importEmailAddress": "",
                "importContactNumber": "",
                "importAddress": "",
                "importInvoiceDate": "",
                "importAttachmentName": "",
                "importAttachmentContent": "",
            },
            "airlineGoodsDetails": [
                {
                    "item": "",
                    "itemCode": "",
                    "qty": "",
                    "unitOfMeasure": "",
                    "unitPrice": "",
                    "total": "",
                    "taxRate": "",
                    "tax": "",
                    "discountTotal": "",
                    "discountTaxRate": "",
                    "orderNumber": "",
                    "discountFlag": "",
                    "deemedFlag": "",
                    "exciseFlag": "",
                    "categoryId": "",
                    "categoryName": "",
                    "goodsCategoryId": "",
                    "goodsCategoryName": "",
                    "exciseRate": "",
                    "exciseRule": "",
                    "exciseTax": "",
                    "pack": "1",
                    "stick": "",
                    "exciseUnit": "",
                    "exciseCurrency": "",
                    "exciseRateName": "",
                }
            ],
            "edcDetails": {
                "tankNo": "",
                "pumpNo": "",
                "nozzleNo": "",
                "controllerNo": "",
                "acquisitionEquipmentNo": "",
                "levelGaugeNo": "",
                "mvrn": "",
            },
        }
    ]

    # Convert JSON object to JSON-formatted string
    json_string = json.dumps(json_data)

    # Encode the JSON string to Base64
    encoded_json = base64.b64encode(json_string.encode("utf-8")).decode("utf-8")
    # print(encoded_json)

    if not doc.is_return:
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
                    "interfaceCode": "T109",
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
            #print Json Data
            print(f"Request Data: {json.dumps(data_to_post, indent=4)}")
            ###assign request in sales invoice
            doc.custom_post_request = {json.dumps(data_to_post, indent=4)}

            # Make a POST request to the external API.
            api_url = server_url
            headers = {"Content-Type": "application/json"}

            response = requests.post(api_url, json=data_to_post)
            ####response 
            
            response.raise_for_status()

            # Parse the JSON response content.
            response_data = json.loads(response.text)
            json_response= json.dumps(response_data, indent=4)

            ##########
            doc.custom_response = json_response

            return_message = response_data["returnStateInfo"]["returnMessage"]
            doc.custom_return_status = return_message
            # Handle the response status code
            if response.status_code == 200 and return_message == "SUCCESS":
                frappe.msgprint("Sales Invoice successfully submitted to EFIRS URA.")

                # Print the response status code and content.
                print(f"Response Status Code: {response.status_code}")
                print(f"Response Content: {response.text}")

                # Parse the JSON response content.
                response_data = json.loads(response.text)
                return_message = response_data["returnStateInfo"]["returnMessage"]

                # Extract and decode the 'content' string.
                encoded_content = response_data["data"]["content"]
                decoded_content = base64.b64decode(encoded_content).decode("utf-8")
                # Print the decoded content
                print("Decoded Content:", decoded_content)

                data = json.loads(decoded_content)

                # Access the 'basicInformation' key using camelCase.
                doc.custom_device_number = data.get("basicInformation", {}).get("deviceNo")
                # doc.qrcode = data.get("summary", {}).get("qrCode").
                doc.custom_verification_code = data.get("basicInformation", {}).get(
                    "antifakeCode"
                )
                doc.custom_fdn  = data.get("basicInformation", {}).get("invoiceNo")
                doc.custom_qr_code = data.get("summary", {}).get("qrCode")
                doc.custom_invoice_number = data.get("basicInformation", {}).get("invoiceId")

                # Log the successful integration request
                log_integration_request('Completed', api_url, headers, data_to_post, response_data)
        
                # Check if qr_data is not None and not an empty string.

                print("Device No:", doc.custom_device_number)
                print("QR Code:", doc.custom_qr_code)
                print("Verification Code:", doc.custom_verification_code)
                print("Fiscal Document Number:", doc.custom_fdn)
                print("Invoice ID:", doc.custom_invoice_number)

                doc.save()

            else:
                frappe.throw(
                    title="EFRIS API Error",
                    msg=return_message,
                )
                doc.docstatus = 0
               

        except requests.exceptions.RequestException as e:
            frappe.msgprint(f"Error making API request: {e}")
            # Set the document status to 'Draft'
            doc.docstatus = 0  # 0 represents 'Draft' status
            doc.save()
            # Log the failed integration request
            log_integration_request('Failed', api_url, headers, data, {}, str(e))
            frappe.throw(f"API request failed: {e}")


    else:
        data = {
            "oriInvoiceId": doc.custom_invoice_number,
            "oriInvoiceNo": doc.custom_fdn,
            "reasonCode": "102",
            "reason": "Refund",
            "applicationTime": datetime_combined,
            "invoiceApplyCategoryCode": "101",
            "currency": doc.currency,
            "contactName": "",
            "contactMobileNum": "",
            "contactEmail": "",
            "source": "106",
            "remarks": "Remarks",
            "sellersReferenceNo": "",
            "goodsDetails": goods_details,
            "taxDetails": tax_categories_list,
            "summary": {
                "netAmount": round((doc.total - total_tax_amount), 2),
                "taxAmount": round((total_tax_amount), 2),
                "grossAmount": doc.total,
                "itemCount": item_count,
                "modeCode": "0",
                "remarks": "We appreciate your continued support",
                "qrCode": doc.custom_qr_code,
            },
            "payWay": {
                "paymentMode": "102",
                "paymentAmount": doc.total,
                "orderNumber": "a",
            },
            "buyerDetails": {
                "buyerTin": doc.tax_id,
                "buyerNinBrn": "",
                "buyerPassportNum": "",
                "buyerLegalName": doc.customer,
                "buyerBusinessName": doc.customer,
                "buyerAddress": "",
                "buyerEmail": doc.custom_email_id,
                "buyerMobilePhone": "",
                "buyerLinePhone": "",
                "buyerPlaceOfBusi": "",
                "buyerType": "1",
                "buyerCitizenship": "",
                "buyerSector": "1",
                "buyerReferenceNo": "",
            },
            "importServicesSeller": {
                "importBusinessName": "",
                "importEmailAddress": "",
                "importContactNumber": "",
                "importAddress": "",
                "importInvoiceDate": "",
                "importAttachmentName": "",
                "importAttachmentContent": "",
            },
            "basicInformation": {
                "operator": "TGS-OSILLO CONSULTING",
                "invoiceKind": "1",
                "invoiceIndustryCode": "",
                "branchId": "",
            },
        }
        # Convert JSON object to JSON-formatted string
        json_string2 = json.dumps(data)

        # Encode the JSON string to Base64
        encoded_json2 = base64.b64encode(json_string2.encode("utf-8")).decode("utf-8")
        try:
            data_to_post2 = {
                "data": {
                    "content": encoded_json2,
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
                    "interfaceCode": "T110",
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
            print(f"Request data: {json.dumps(data_to_post2, indent=4)}")
            # Make a POST request to the external API.
            api_url = server_url # Replace with your actual endpoint
            headers = {"Content-Type": "application/json"}

            response = requests.post(api_url, json=data_to_post2)
            response.raise_for_status()  # Raise an HTTPError for bad responses.
            
            # Print the response status code and content.
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Content: {response.text}")
            
              # Parse the JSON response content.
            response_data2 = json.loads(response.text)
            return_message2 = response_data2["returnStateInfo"]["returnMessage"]

            # Handle the response status code
            if response.status_code == 200 and return_message2 == "SUCCESS":

                frappe.msgprint("Credit Note Submitted Successfully")
                # Log the successful integration request
                log_integration_request('Completed', api_url, headers, data_to_post2, response_data2)
                
            else:
                frappe.throw(
                title='EFRIS API Error',
                msg=f"{return_message2}"
            )
                doc.docstatus = 0

        except requests.exceptions.RequestException as e:
            frappe.msgprint(f"Error making API request: {e}")
            
            # Set the document status to 'Draft'
            doc.docstatus = 0  # 0 represents 'Draft' status
            doc.save()
            # Log the failed integration request
            log_integration_request('Failed', api_url, headers, data, {}, str(e))
            frappe.throw(f"API request failed: {e}")


    