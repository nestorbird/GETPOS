// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on("Pricing Rule", {
	custom_send_mail: function (frm) {
        if (frm.doc.customer && !frm.is_dirty() ){
            frappe.call({
                method:  "getpos.getpos.hooks.pricing_rule.coupon_code_email",  
                args: {                         
                    pricing_rule : frm.doc.name,
                    customer : frm.doc.customer,
                    discount_rate : frm.doc.rate,
                    discount_percentage : frm.doc.discount_percentage,
                    discount_amount : frm.doc.discount_amount,
                    coupon_code_based : frm.doc.coupon_code_based,
                },
                freeze: true,
                freeze_message: "Sending mail...",
                callback: function(response) { 
                        if(response.message){
                            for (const i of response.message) {
                                {
                                    frappe.show_alert({
                                        message:__('Email Sent on  ' + i),
                                        indicator:'green'
                                    }, 4);
                                   } 
                              }
                        }
                        else {
                            //
                      }
                 }                  
            });
        }
        else{
            frappe.msgprint("Form is not Saved")
        }

    },
});

