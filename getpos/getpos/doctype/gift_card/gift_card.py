import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import strip
from frappe.utils.pdf import get_pdf

class GiftCard(Document):

	def autoname(self):
		self.gift_card_name = strip(self.gift_card_name)
		self.name = self.gift_card_name

		if not self.code:			
			self.code = frappe.generate_hash()[:10].upper()

	def on_submit(doc,method=None):     
		company_name = frappe.get_doc("Global Defaults").default_company
		company=frappe.get_doc("Company",company_name)		
		journal_entry = frappe.new_doc("Journal Entry")
		journal_entry.voucher_type="Journal Entry"
		journal_entry.company=company.name
		journal_entry.posting_date=frappe.utils.getdate()	
		if doc.gift_card_type=="Free":
			journal_entry.user_remark="gift card worth $" + str(doc.discount_amount) + " sold to customer for cash"		
			journal_entry.append(
				"accounts",
				{
				'account': "Cash - " + company.abbr,
				'debit_in_account_currency': float(doc.discount_amount),
				'credit_in_account_currency': float(0)
				})
			journal_entry.append(
				"accounts",
				{
				'account': "Gift card Revenue - " + company.abbr,
				'debit_in_account_currency': float(0),
				'credit_in_account_currency':float(doc.discount_amount)
        		})	
		else:
			journal_entry.user_remark="Gift card given to customer free of cost, hence considering it our expense for $" + str(doc.discount_amount)			
			journal_entry.append(
				"accounts",
				{
				'account': "Marketing Expenses - " + company.abbr,
				'debit_in_account_currency': float(doc.discount_amount),
				'credit_in_account_currency': float(0)
				})
			journal_entry.append(				
				"accounts",
				{
				'account': "Gift card Revenue - " + company.abbr,
				'debit_in_account_currency': float(0),
				'credit_in_account_currency': float(doc.discount_amount)
        		})	
		journal_entry.save(ignore_permissions=True)
		journal_entry.submit()   
		frappe.set_value('Gift Card', doc.name, 'amount_balance', float(doc.discount_amount))      
		customer = frappe.get_doc("Customer", doc.customer)
		contact_doc = frappe.get_doc("Contact", customer.customer_primary_contact)
		recipient = contact_doc.email_id
		# Check if the recipient email is present
		if recipient:
			subject = "Your Gift Card: {}".format(doc.name)
			message = "Dear {},\n\nPlease find attached your Gift Card: {}.\n\nBest regards,\nYour Company Name".format(customer.customer_name, doc.code)
			html = frappe.render_template('getpos/templates/pages/gift_card_template.html', context={'doc': doc})
			pdf_content = get_pdf(html)
			attachment = {
				"fname": "Gift_Card_{}.pdf".format(doc.name.replace(" ", "_")),
				"fcontent": pdf_content
			}
			try:
				# Send the email
				frappe.sendmail(
					recipients=[recipient],
					subject=subject,
					message=message,
					attachments=[attachment],
					now=True
				)
			except Exception as e:
				frappe.local.response["message"] = {
					"success_key": 0,
					"message": str(e)
				}
