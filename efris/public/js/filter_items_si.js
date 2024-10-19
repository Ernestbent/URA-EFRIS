frappe.ui.form.on('Sales Invoice', {
    onload: function(frm) {
        console.log('Company onload:', frm.doc.company);
        if (frm.doc.company) {
            frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc) {
                return {
                    filters: {
                        'custom_company': frm.doc.company
                    }
                };
            };
        }
    },
    company: function(frm) {
        console.log('Company changed:', frm.doc.company);
        frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc) {
            return {
                filters: {
                    'custom_company': frm.doc.company
                }
            };
        };
        frm.refresh_field('items');
    }
});
