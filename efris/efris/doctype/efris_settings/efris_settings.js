frappe.ui.form.on('Efris Settings', {
    refresh: function(frm) {
        // Only add the custom buttons if the document is not new
        if (!frm.is_new()) {
            // Add a custom button to send fixed data
            frm.add_custom_button(__('Get Units Of Measure'), function() {
                // Call the server-side method for sending fixed data
                send_fixed_data_to_server();
            }, __("Actions"));

            // Add a custom button for server initialization
            frm.add_custom_button(__('Server Initialization'), function() {
                // Call the server-side method for server initialization
                initialize_server();
            }, __("Actions"));

            // Add a custom button to get exchange rates
            frm.add_custom_button(__('Get Exchange Rates'), function() {
                // Call the server-side method for getting exchange rates
                get_exchange_rates();
            }, __("Actions"));
        }
    }
});

function send_fixed_data_to_server() {
    // Call the server-side method for sending fixed data
    frappe.call({
        method: 'efris.efris.api.send_fixed_data_to_external_system',  // Adjust the path if necessary
        callback: function(response) {
            if (response.message) {
                if (response.message.status === "success") {
                    frappe.msgprint("Efris Units Of Measure Fetched Successfully")
                } else {
                    frappe.msgprint(__('Failed to send data: ' + JSON.stringify(response.message.message)));
                }
            } else {
                frappe.msgprint(__('Failed to send data'));
            }
        }
    });
}

function initialize_server() {
    // Call the server-side method for server initialization
    frappe.call({
        method: 'efris.efris.server_time.get_server_time',  // Adjust the path if necessary
        callback: function(response) {
            if (response.message) {
                if (response.message.status === "success") {
                    frappe.msgprint("Server Initialized");
                } else {
                    frappe.msgprint(__('Failed to initialize server: ' + JSON.stringify(response.message.message)));
                }
            } else {
                frappe.msgprint(__('Failed to initialize server'));
            }
        }
    });
}
function get_exchange_rates() {
    // Call the server-side method for getting exchange rates
    frappe.call({
        method: 'efris.efris.exchange_rates.get_exchange_rates',  // Adjust the path if necessary
        callback: function(response) {
            if (response.message) {
                if (response.message.status === "success") {
                    frappe.msgprint(__('Exchange rates retrieved successfully.'));
                } else {
                    frappe.msgprint(__('Failed to retrieve exchange rates.'));
                }
            } else {
                frappe.msgprint(__('Failed to retrieve exchange rates'));
            }
        }
    });
}
