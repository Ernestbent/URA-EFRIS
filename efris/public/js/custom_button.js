frappe.ui.form.on('UOM', {
    refresh: function(frm) {
        // Add a custom button
        frm.add_custom_button(__('Send Fixed Data'), function() {
            // Call the server-side method
            send_fixed_data_to_server();
        });
    }
});

function send_fixed_data_to_server() {
    // Call the server-side method
    frappe.call({
        method: 'efris.efris.api.send_fixed_data_to_external_system',  // Adjust the path if necessary
        callback: function(response) {
            if (response.message) {
                if (response.message.status === "success") {
                    frappe.msgprint(__('Data sent successfully: ' + JSON.stringify(response.message.message)));
                } else {
                    frappe.msgprint(__('Failed to send data: ' + JSON.stringify(response.message.message)));
                }
            } else {
                frappe.msgprint(__('Failed to send data'));
            }
        }
    });
}