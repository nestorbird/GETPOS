$(document).on("startup", function () {
if (frappe.session.user == "user@nestorbird.com") {
    frappe.set_route("/app/point-of-sale")
}

})