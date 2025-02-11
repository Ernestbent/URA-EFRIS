frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        // Check if the document is in Return status
        if (frm.doc.docstatus === 1 && frm.doc.is_return) {  
            frm.add_custom_button(__('Query Credit Note Number'), function() {
                get_credit_note_number(frm);
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
        method: "efris.efris.custom_scripts.query_ccn.query_credit_note",  // Correct server-side function path
        args: {
            custom_reference_number: frm.doc.custom_reference_number,  // Pass custom_reference_number
            custom_fdn: frm.doc.custom_fdn  // Pass custom_fdn
        },
        callback: function(response) {
            if (response.message && response.message.status === "success") {
                let data = response.message;

                // Check if the required fields exist in the response
                if (data.credit_note_no || data.credit_note_id) {
                    // Update the Sales Invoice form with the retrieved credit note number
                    frm.set_value("custom_credit_note_number", data.credit_note_no || "");  // Set custom_credit_note_number
                    frm.set_value("custom_id", data.id || "");  // Set custom_id if it exists

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
