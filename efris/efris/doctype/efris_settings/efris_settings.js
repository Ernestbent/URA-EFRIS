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
            // Add custom button Query Excise Items.
            frm.add_custom_button(__('Query Excise Duty'), function(){
                // Call the Server-side method for getting excise duty
                query_excise_duty();
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
function query_excise_duty() {
    // Call the server-side method for sending fixed data
    frappe.call({
        method: 'efris.efris.excise_duty.query_excise_duty_items',  // Adjust the path if necessary
        callback: function(response) {
            if (response.message) {
                if (response.message.status === "success") {
                    frappe.msgprint("Excise duty Goods/Services Fetched Successfully")
                } else {
                    frappe.msgprint(__('Failed to send data: ' + JSON.stringify(response.message.message)));
                }
            } else {
                frappe.msgprint(__('Failed to send data'));
            }
        }
    });
}
