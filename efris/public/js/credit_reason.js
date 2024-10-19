frappe.ui.form.on('Sales Invoice', {
    onload: function(frm) {
        // Show or hide the custom_reason field based on the initial value of is_return
        frm.toggle_display('custom_reason', frm.doc.is_return);
    },

    is_return: function(frm) {
        // Toggle the display of the custom_reason field based on the value of is_return
        frm.toggle_display('custom_reason', frm.doc.is_return);
    }
});
