frappe.ui.form.on('Customer', {
    refresh: function(frm) {
        // Add a custom button to fetch taxpayer information
        frm.add_custom_button(__('Get Taxpayer Information'), function() {
            // Call the server-side method for retrieving taxpayer info
            get_taxpayer_information(frm);
        }, __("EFRIS Actions"));
    }
});

// Function to call the server-side method for retrieving taxpayer info
function get_taxpayer_information(frm) {
    if (!frm.doc.tax_id) {
        frappe.msgprint(__('No Tax ID found. Please enter a Tax ID before proceeding.'));
        return;
    }

    frappe.call({
        method: "efris.efris.custom_scripts.validate_tax_payer.make_api_call",  
        args: {
            tax_id: frm.doc.tax_id  // Pass the Tax ID directly instead of customer name
        },
        callback: function(response) {
            if (response.message && response.message.status === "success") {
                let data = response.message;

                // Update the Customer form with the retrieved data
                frm.set_value("customer_name", data.customer_name || "");
                frm.set_value("custom_business_name", data.business_name || "");
                frm.set_value("custom_ninbrn", data.nin_brn || "");
                frm.set_value("custom_tax_payer_type", data.taxpayer_type || "");
                frm.set_value("custom_contact_email", data.contact_email || "");
                frm.set_value("custom_contact_number", data.contact_number || "");
                frm.set_value("custom_address", data.address || "");
                frm.set_value("custom_govenrment_tin", data.government_tin || "");
    

                frappe.msgprint(__('Success'));
                frm.refresh(); // Refresh the form to reflect updated values
            } else {
                let errorMessage = response.message ? response.message.message : "Unknown error";
                frappe.msgprint(__('Failed to retrieve taxpayer information: ') + errorMessage);
            }
        }
    });
}
