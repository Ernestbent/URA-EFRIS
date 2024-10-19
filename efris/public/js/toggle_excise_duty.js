frappe.ui.form.on('Item', {
    refresh: function(frm) {
        // Trigger toggle function on form load
        toggle_excise_duty_code(frm);
    },
    custom_has_excise_tax: function(frm) {
        // Trigger toggle function when the select field is changed
        toggle_excise_duty_code(frm);
    }
});

function toggle_excise_duty_code(frm) {
    // Get the value of the select field custom_has_excise_tax
    let selected_value = frm.doc.custom_has_excise_tax;
    
    // Show custom_excise_duty_code if value is 101, otherwise hide it
    if (selected_value === "101") {
        frm.set_df_property('custom_excise_duty_code', 'hidden', 0); // Show
    } else if (selected_value === "102") {
        frm.set_df_property('custom_excise_duty_code', 'hidden', 1); // Hide
    }
}
