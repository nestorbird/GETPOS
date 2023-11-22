// Copyright (c) 2023, swapnil and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sync Register", {
  refresh: function (frm) {
    frm.disable_save();
  },
});
