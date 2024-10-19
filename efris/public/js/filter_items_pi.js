frappe.ui.form.on('Purchase Invoice', {
    onload: function(frm) {
        apply_item_filter(frm);
    },
    refresh: function(frm) {
        apply_item_filter(frm);
    },
    company: function(frm) {
        apply_item_filter(frm);
    }
});

function apply_item_filter(frm) {
    if (frm.doc.company) {
        frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc) {
            return {
                filters: {
                    'custom_company': frm.doc.company
                }
            };
        };
        frm.refresh_field('items');
    }
}
