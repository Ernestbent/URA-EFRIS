frappe.ui.form.on('Sales Invoice', {
    after_cancel: function(frm) {
        // Create a new prompt dialog with three options
        let dialog = frappe.prompt([
            {
                label: 'Refund Reason',
                fieldname: 'refund_reason',
                fieldtype: 'Select',
                options: [
                    {'label': 'Buyer refused to accept the invoice due to incorrect invoice/receipt', 'value': '101'},
                    {'label': 'Not delivered due to incorrect invoice/receipt', 'value': '102'},
                    {'label': 'Other reasons', 'value': '103'}
                ],
                reqd: 1
            }
        ], 
        (data) => {
            if (data.refund_reason) {
                // Set the refund reason on the form
                frm.set_value('refund_reason', data.refund_reason);

                // Proceed with the cancellation
                frm.save('Cancel', function() {
                    frappe.show_alert('Document cancelled with reason: ' + data.refund_reason);
                });
            }
        },
        'Select Refund Reason', 'Submit');
        
        // Ensure the dialog is shown
        dialog.show();
    }
});
