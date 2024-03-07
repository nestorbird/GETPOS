frappe.ui.form.on('POS Closing List', {
    onload: function (frm) {
        frm.set_query("pos_opening_entry", function(doc) {
            return { filters: { 'status': 'Open', 'docstatus': 1 } };
        });
    },
    pos_opening_entry: function (frm) {
        if (!frm.doc.pos_opening_entry) {
            resetChildTableData(frm); 
        } 
        else if (frm.doc.pos_opening_entry && frm.doc.period_start_date && frm.doc.period_end_date && frm.doc.user) {
            frappe.run_serially([
                () => frm.trigger("get_sales_invoices"),
                () => frm.trigger("set_opening_amounts"),
                () => frm.trigger("get_data") 
            ]);
        }
    },
    resetChildTableData: function(frm) {
        
        frm.doc.pos_transactions = [];
        refresh_field("pos_transactions");
    },
    
    
    
    set_opening_amounts: function(frm) {
        return frappe.db.get_doc("POS Opening List", frm.doc.pos_opening_entry)
            .then(({ balance_details }) => {
                balance_details.forEach(detail => {
                    frm.add_child("payment_reconciliation", {
                        mode_of_payment: detail.mode_of_payment,
                        opening_amount: detail.opening_amount,
                        expected_amount: detail.opening_amount
                    });
                });
                frm.refresh_field("payment_reconciliation");
            })
            .catch(err => {
                console.error(err);
            });
    },
    
    get_sales_invoices: function(frm) {
        return frappe.call({
            method: 'getpos.getpos.doctype.pos_closing_list.pos_closing_list.get_sales_invoices',
            args: {
                start: frappe.datetime.get_datetime_as_string(frm.doc.period_start_date),
                end: frappe.datetime.get_datetime_as_string(frm.doc.period_end_date),
                pos_profile: frm.doc.pos_profile,
                pos_opening_entry: frm.doc.pos_opening_entry,
                user: frm.doc.user
            },
            callback: function(response) {
                if (response.message && response.message.length > 0) {
                    var total_amount = 0;
                    var quantity = 0;
                    var net_total = 0;
                    for (let i = 0; i < response.message.length; i++) {
                        let invoice = response.message[i];
                        quantity += invoice.total_qty;
                        total_amount += invoice.grand_total;
                        net_total += invoice.net_total;
            
                        frm.add_child("pos_transactions", {
                            "pos_invoice": invoice.name,
                            "posting_date": invoice.posting_date,
                            "customer": invoice.customer,
                            "grand_total": invoice.grand_total,
                            "is_return": invoice.is_return,
                            "return_against": invoice.return_against,
                        });
                    }
                    frm.set_value({
                        grand_total: flt(total_amount),
                        net_total: flt(net_total),
                        total_quantity: flt(quantity),
                    });
                    frm.refresh_field("pos_transactions");
                } else {
                    frappe.msgprint("No Sales Invoice Found in the specified period.");
                }
            }
        });
    },
    
    get_data: function (frm) {
        return frappe.call({
            method: 'getpos.getpos.doctype.pos_closing_list.pos_closing_list.get_tax_data',
            args: {
                pos_opening_entry: frm.doc.pos_opening_entry,
            },
            callback: function (response) {
                if (response.message && response.message.length > 0) {
                    for (let i = 0; i < response.message.length; i++) {
                        let tax_data = response.message[i];
                        frm.add_child("taxes_details", {
                            "account_head": tax_data.account_head,
                            "rate": tax_data.rate,
                            "amount": tax_data.tax_amount,
                        });
                    }
                    frm.refresh_field("taxes_details");
                }
            }
        });
    }
});

