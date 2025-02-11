frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        // Add a custom button to fetch taxpayer information
        frm.add_custom_button(__('Query Credit Note Number'), function() {
            // Call the server-side method for retrieving taxpayer info
            get_credit_note_number(frm);
        }, __("Credit Note Actions"));
    }
});

// Function to call the server-side method for retrieving taxpayer info
function get_credit_note_number(frm) {
    if (!frm.doc.custom_reference_number || !frm.doc.custom_fdn) {
        frappe.msgprint(__('Please enter both Custom Reference Number and Custom FDN before proceeding.'));
        return;
    }

    frappe.call({
        method: "efris.efris.custom_scripts.query_ccn.query_credit_note",  // Ensure this matches your server-side function
        args: {
            custom_reference_number: frm.doc.custom_reference_number,  // Pass custom_reference_number
            custom_fdn: frm.doc.custom_fdn  // Pass custom_fdn
        },
        callback: function(response) {
            if (response.message && response.message.status === "success") {
                let data = response.message;

                // Update the Customer form with the retrieved data
                frm.set_value("custom_credit_note_no", data.custom_credit_note_number|| "");  // Set custom_credit_note_no

                frappe.msgprint(__('Success'));
                frm.refresh(); // Refresh the form to reflect updated values
            } else {
                let errorMessage = response.message ? response.message.message : "Unknown error";
                frappe.msgprint(__('Failed to retrieve taxpayer information: ') + errorMessage);
            }
        }
    });
}
