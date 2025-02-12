frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        // Check if the document is in Return status
        if (frm.doc.docstatus === 1 && frm.doc.is_return) {  
            frm.add_custom_button(__('Query Credit Note Details(CN and id)'), function() {
                get_credit_note_number(frm);
            }, __("Credit Note Actions"));

            frm.add_custom_button(__('Get Verification Code for CN'), function() {
                get_verification_code_for_cn(frm);
            }, __("Credit Note Actions"));
            frm.add_custom_button(__('Cancel Credit Note Awaiting Approval'), function() {
                cancel_credit_note_awaiting_approval(frm);
            }, __("Credit Note Actions"));
        }
    }
});

// Function to call the server-side method for retrieving credit note number
function get_credit_note_number(frm) {
    if (!frm.doc.custom_reference_number || !frm.doc.custom_fdn) {
        frappe.msgprint(__('Please enter both Custom Reference Number and Custom FDN before proceeding.'));
        return;
    }

    frappe.call({
        method: "efris.efris.custom_scripts.query_ccn.query_credit_note",  
        args: {
            custom_reference_number: frm.doc.custom_reference_number,  
            custom_fdn: frm.doc.custom_fdn  
        },
        callback: function(response) {
            if (response.message && response.message.status === "success") {
                let data = response.message;

                if (data.credit_note_no || data.credit_note_id) {
                    frm.set_value("custom_credit_note_number", data.credit_note_no || "");  
                    frm.set_value("custom_id", data.id || "");  

                    frappe.msgprint(__('Success'));
                    frm.refresh(); 
                } else {
                    frappe.msgprint(__('Credit Note Number or ID missing in the response.'));
                }
            } else {
                let errorMessage = response.message ? response.message.message : "Unknown error";
                frappe.msgprint(__('Failed to retrieve Credit Note Number: ') + errorMessage);
            }
        },
        error: function(error) {
            frappe.msgprint(__('Error in API call: ') + error.message);
        }
    });
}

// Function to get verification code for credit note
function get_verification_code_for_cn(frm) {
    if (!frm.doc.custom_credit_note_number) {
        frappe.msgprint(__('Please enter Credit Note Number before proceeding.'));
        return;
    }

    frappe.call({
        method: "efris.efris.custom_scripts.query_verification_code_ccn.query_verification_code_cn",  // Replace with the actual server-side method
        args: {
            credit_note_number: frm.doc.custom_credit_note_number
        },
        callback: function(response) {
            if (response.message && response.message.status === "success") {
                let data = response.message;

                if (data.verification_code) {
                    frm.set_value("custom_verification_codecn", data.verification_code || "");  

                    frappe.msgprint(__('Verification Code retrieved successfully.'));
                    frm.refresh(); 
                } else {
                    frappe.msgprint(__('Verification Code missing in the response.'));
                }
            } else {
                let errorMessage = response.message ? response.message.message : "Unknown error";
                frappe.msgprint(__('Failed to retrieve Verification Code: ') + errorMessage);
            }
        },
        error: function(error) {
            frappe.msgprint(__('Error in API call: ') + error.message);
        }
    });
}

// Function to call the server-side method for canceling credit note
function cancel_credit_note_awaiting_approval(frm) {
    if (!frm.doc.custom_id) {
        frappe.msgprint(__('Credit Note ID is missing. Please ensure the Credit Note has been queried first.'));
        return;
    }

    frappe.call({
        method: "efris.efris.custom_scripts.cancel_credit_note_awaiting_approval.cancel_credit_note_awaiting_ap",
        args: {
            custom_id: frm.doc.custom_id
        },
        callback: function(response) {
            if (response.message && response.message.status === "success") {
                frappe.msgprint(__('Credit Note Cancellation request sent successfully.'));
            } else {
                let errorMessage = response.message ? response.message.message : "Unknown error";
                frappe.msgprint(__('Failed to cancel Credit Note: ') + errorMessage);
            }
        },
        error: function(error) {
            frappe.msgprint(__('Error in API call: ') + error.message);
        }
    });
}
