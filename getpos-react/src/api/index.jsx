

const APIs = {
  getGuestCustomer: '/api/method/getpos.getpos.api.get_theme_settings',
  login: '/api/method/getpos.getpos.api.login', 
  getOpeningData : '/api/method/getpos.custom_api.pos_api.get_opening_data',
  createOpeningShift:'/api/method/getpos.custom_api.pos_api.create_opening_voucher',
  createClosingShift:'/api/method/getpos.getpos.doctype.pos_closing_shift.pos_closing_shift.submit_closing_shift',
  getCategoriesAndProducts: '/api/method/getpos.custom_api.item_variant_api.get_items',
  getAllCustomers: '/api/method/getpos.getpos.api.get_all_customer',
  getSalesOrderList: '/api/method/getpos.getpos.api.get_sales_order_list',
  changePassword: '/api/method/getpos.getpos.api.change_password',
  getBasicInfo: '/api/method/getpos.getpos.api.get_details_by_hubmanager',
  createCustomer:'/api/method/getpos.getpos.api.create_customer',
  editCustomer: '/api/method/getpos.getpos.api.edit_customer',
  createOrder:'/api/method/getpos.getpos.api.create_sales_order_kiosk',
  returnSalesOrder: '/api/method/getpos.getpos.api.return_sales_order',
  getCouponCodeList: '/api/method/getpos.getpos.api.coupon_code_details',
  validatePromoCode:'/api/method/getpos.getpos.api.validate_coupon_code',
  getCustomerDetails:'/api/method/getpos.getpos.api.get_customer',
  getlocation:'/api/method/getpos.getpos.api.get_location',

  validateGiftCode:'api/method/getpos.getpos.api.validate_gift_card',
  sendMail:"api/method/getpos.getpos.api.resend_sales_invoice_email",
  getShiftDetails:"/api/method/getpos.getpos.doctype.pos_closing_shift.pos_closing_shift.get_shift_details",
  
};

export default APIs;
