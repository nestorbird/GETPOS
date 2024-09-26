import React, { useContext, useEffect, useState } from "react";
import {
  Button,
  Spin,
  Menu,
  notification,
  Modal,
  AutoComplete,
  Input,
} from "antd";
import {
  createSalesOrder,
  fetchCustomers,
  getCouponCodeList,
  getCustomerDetail,
  getGuestCustomer,
  validatePromoCode,
  validateGiftCard,
  login,
} from "../modules/LandingPage";
import DeleteImg from "../../src/assets/images/Delete.png";
import IconCash from "../../src/assets/images/cash.png";
import IconCard from "../../src/assets/images/card.png";
import IconCredit from "../../src/assets/images/Credit.png";
import ButtonTick from "../../src/assets/images/btn-tick.png";
import ButtonCross from "../../src/assets/images/btn-cross.png";
import EmptyCart from "../../src/assets/images/empty-cart.png";
import CashPaymentPopup from "./CashPaymentPopup";
import { CartContext } from "../common/CartContext";
import AddCustomerForm from "./Addcustomer";
import PromoCodePopup from "./PromoCodePopup";
import { useThemeSettings } from "./ThemeSettingContext";

const Cart = ({ onPlaceOrder, onReservationClick }) => {
  const [selectedTab, setSelectedTab] = useState("Takeaway");
  const [customers, setCustomers] = useState([]);
  const [guestCustomer, setGuestCustomer] = useState();
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredCustomers, setFilteredCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isInputFocused, setIsInputFocused] = useState(false);
  const [isPopupVisible, setIsPopupVisible] = useState(false);
  const [cashReceived, setCashReceived] = useState(0);
  const [customerSelected, setCustomerSelected] = useState(false);
  const [customerSelectedDetails, setCustomerSelectedDetails] = useState([]);
  const [showAddCustomerForm, setShowAddCustomerForm] = useState(false);

  const {
    cartItems,
    removeItemFromCart,
    resetCart,
    completeOrder,
    setCartItems,
  } = useContext(CartContext);
  const [isPromoCodePopupVisible, setIsPromoCodePopupVisible] = useState(false);
  const [couponDiscount, setCouponDiscount] = useState(0);
  const [giftCardDiscount, setGiftCardDiscount] = useState(0);
  const [redeem, setRedeem] = useState(0);
  const [loyaltyProgram, setLoyaltyProgram] = useState("");

  const [promoCode, setPromoCode] = useState("");
  const [couponCodes, setCouponCodes] = useState([]);
  const [validatedPromoCode, setValidatedPromoCode] = useState("");
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState(null);
  const [loyaltyInput, setLoyaltyInput] = useState("");
  const [loyaltyAmount, setLoyaltyAmount] = useState(0);
  const [loyaltyRedemptionAccount, setLoyaltyRedemptionAccount] = useState("");
  const [giftCard, setGiftCard] = useState("");
  const [isPromoCodeValid, setIsPromoCodeValid] = useState(false);
  const [isGiftCardValid, setIsGiftCardValid] = useState(false);
  const [isLoyaltyPointsValid, setIsLoyaltyPointsValid] = useState(false);
  const [discountAmount, setDiscountAmount] = useState(0);
  const [editedPrices, setEditedPrices] = useState({});
  const [authModalVisible, setAuthModalVisible] = useState(false);
  const [authPendingItem, setAuthPendingItem] = useState(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [editPriceDiscount, setEditpriceDiscount] = useState(0);
  const [storedPassword, setStoredPassword] = useState("");
  const [lastAuthorizedPrices, setLastAuthorizedPrices] = useState({});
  const themeSettings = useThemeSettings();
  const [isTaxExpanded, setIsTaxExpanded] = useState(false);

  useEffect(() => {
    const storedPromoCode = localStorage.getItem("promoCode");
    const storedDiscount = localStorage.getItem("couponDiscount");
    const storedEmail = JSON.parse(localStorage.getItem("user"));

    if (storedEmail && storedEmail.email) {
      setEmail(storedEmail.email);
    } else {
      console.error("Email not found in local storage.");
      setEmail("");
    }

    if (storedPromoCode) {
      setPromoCode(storedPromoCode);
      setValidatedPromoCode(`${storedPromoCode}`);
    }

    if (storedDiscount) {
      setCouponDiscount(parseFloat(storedDiscount));
    }
  }, []);

 
  
  const calculateSubtotal = (items) => {
    if (!Array.isArray(items)) {
      console.error("Invalid items array:", items);
      return 0;
    }

    return items.reduce((sum, item) => {
      const selectedAttributesTotal = item.selectedAttributes
        ? Object.values(item.selectedAttributes)
            .flat()
            .reduce((attrSum, attr) => {
              // Find the attribute price from item's attributes
              const attributeOption = item.attributes
                .flatMap((attrGroup) => attrGroup.options)
                .find((option) => option.item_name === attr);
              return attrSum + (attributeOption?.price || 0);
            }, 0)
        : 0;

      const itemTotalPrice = item.product_price + selectedAttributesTotal;
      return sum + itemTotalPrice * item.quantity;
    }, 0);
  };

  const calculateTaxForItem = (item) => {
    if (!item.tax || item.tax.length === 0) return 0;

    const taxPercentage = parseFloat(
      item.tax[0].custom_tax_percentage.replace("%", "")
    );
    const itemTotal = item.product_price * item.quantity;
    const taxAmount = (itemTotal * taxPercentage) / 100;

    return taxAmount;
  };

  const calculateTotalTax = (items) => {
    return items.reduce((total, item) => {
      if (!item.tax || item.tax.length === 0) return total;

      const selectedAttributesTotal = item.selectedAttributes
        ? Object.values(item.selectedAttributes)
            .flat()
            .reduce((attrSum, attr) => {
              const attributeOption = item.attributes
                .flatMap((attrGroup) => attrGroup.options)
                .find((option) => option.item_name === attr);
              return attrSum + (attributeOption?.price || 0);
            }, 0)
        : 0;

      const itemTotalPrice = item.product_price + selectedAttributesTotal;

      const itemTotalTax = item.tax.reduce((itemTaxSum, taxEntry) => {
        return (
          itemTaxSum +
          (itemTotalPrice * parseFloat(taxEntry.custom_tax_percentage)) / 100
        );
      }, 0);

      return total + itemTotalTax;
    }, 0);
  };

  const calculateTotalWithTax = (items) => {
    const subtotal = calculateSubtotal(items);
    const totalTax = calculateTotalTax(items);
    return subtotal + totalTax;
  };

  const groupTaxesByRate = (items) => {
    const taxGroups = {};

    items.forEach((item) => {
      const sortedTaxes = item.tax.sort((a, b) => {
        if (a.tax_type.includes("CGST") && b.tax_type.includes("SGST"))
          return -1;
        if (a.tax_type.includes("SGST") && b.tax_type.includes("CGST"))
          return 1;
        return 0;
      });

      const selectedAttributesTotal = item.selectedAttributes
        ? Object.values(item.selectedAttributes)
            .flat()
            .reduce((attrSum, attr) => {
              const attributeOption = item.attributes
                .flatMap((attrGroup) => attrGroup.options)
                .find((option) => option.item_name === attr);
              return attrSum + (attributeOption?.price || 0);
            }, 0)
        : 0;

      const itemTotalPrice = item.product_price + selectedAttributesTotal;

      sortedTaxes.forEach((taxEntry) => {
        const taxType = taxEntry.tax_type;
        const hyphenIndex = taxType.lastIndexOf(" -");
        let taxLabel = "";

        if (hyphenIndex !== -1) {
          const taxFragment = taxType
            .slice(Math.max(0, hyphenIndex - 4), hyphenIndex)
            .trim();
          taxLabel = taxFragment.length >= 3 ? taxFragment : "Unknown";
        } else {
          taxLabel = "Unknown";
        }

        const taxKey = `${taxLabel}-${taxEntry.custom_tax_percentage}`;

        if (!taxGroups[taxKey]) {
          taxGroups[taxKey] = {
            taxLabel,
            custom_tax_percentage: taxEntry.custom_tax_percentage,
            totalTaxAmount: 0,
          };
        }

        const taxAmount =
          (itemTotalPrice * parseFloat(taxEntry.custom_tax_percentage)) / 100;
        taxGroups[taxKey].totalTaxAmount += taxAmount;
      });
    });

    return Object.values(taxGroups);
  };

  const calculateTaxForEntry = (item, taxEntry) => {
    const taxPercentage = parseFloat(
      taxEntry.custom_tax_percentage.replace("%", "")
    );
    const itemTotal = item.product_price * item.quantity;
    return (itemTotal * taxPercentage) / 100;
  };

  const getTotalTaxForItem = (item) => {
    if (!item.tax || item.tax.length === 0) return 0;

    return item.tax.reduce((total, taxEntry) => {
      return total + calculateTaxForEntry(item, taxEntry);
    }, 0);
  };

  const toggleTaxExpand = () => {
    setIsTaxExpanded((prev) => !prev);
  };

  const [subtotal, setSubtotal] = useState(calculateSubtotal(cartItems));
  const [totalTax, setTotalTax] = useState(calculateTotalTax(cartItems));
  const [totalWithTax, setTotalWithTax] = useState(
    calculateTotalWithTax(cartItems)
  );

  useEffect(() => {
    setSubtotal(calculateSubtotal(cartItems));
    setTotalTax(calculateTotalTax(cartItems));
    setTotalWithTax(calculateTotalWithTax(cartItems));
  }, [cartItems]);

  const discount = 0;
  // const taxRate = 0.1;
  // const taxRate = 0;
  // const total = subtotal - couponDiscount + tax;

  const handleCashButtonClick = () => {
    localStorage.removeItem("cashTransaction");
    setIsPopupVisible(true);
  };

  const handlePopupClose = () => {
    setIsPopupVisible(false);
    setCashReceived(0);
  };

  const handlePromoCodeClick = () => {
    if (promoCode) {
      setIsPromoCodeValid(true);
      setIsGiftCardValid(false);
    }
    setIsPromoCodePopupVisible(true);
  };
  const handlePromoPopupClose = () => {
    setIsPromoCodePopupVisible(false);
  };
  useEffect(() => {
    setSubtotal(calculateSubtotal(cartItems));
  }, [cartItems]);

  const customerOptions = filteredCustomers.map((customer) => ({
    value: `${customer.mobile_no || ""} | ${customer.customer_name || ""}`,
    label: (
      <div className="search-customer-list">
        <span className="search-cust-name">
          {customer.customer_name || "No Name"}
        </span>
        <span className="search-cust-number">
          {customer.mobile_no || "No Mobile Number"}
        </span>
      </div>
    ),
    customer: customer, // Include the customer object for onSelect
  }));

  const handleSearchChange = (value) => {
    setSearchTerm(value);
    if (value.trim() === "") {
      setFilteredCustomers(customers);
      setShowAddCustomerForm(false);
      setSelectedCustomer(null);
      localStorage.removeItem("selectedCustomer");
    } else {
      const filtered = customers.filter(
        (customer) =>
          customer.customer_name.toLowerCase().includes(value.toLowerCase()) ||
          customer.mobile_no.toLowerCase().includes(value.toLowerCase())
      );

      setFilteredCustomers(filtered);
      setShowAddCustomerForm(filtered.length === 0);
      if (filtered.length === 0) {
        setSelectedCustomer(null);
        localStorage.removeItem("selectedCustomer");
      }
    }
  };

  const handleCustomerSelect = (customer) => {
    if (customer && customer.mobile_no) {
      setSelectedCustomer(customer);
      setSearchTerm(`${customer.mobile_no} | ${customer.customer_name}`);
      setIsInputFocused(false);
      setCustomerSelected(true);
      setShowAddCustomerForm(false);
      localStorage.setItem("selectedCustomer", JSON.stringify(customer));
    } else {
      setShowAddCustomerForm(true);
    }
  };

  const loadCustomers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchCustomers();
      if (data) {
        setCustomers(data);
        setFilteredCustomers(data);
        localStorage.setItem("customers", JSON.stringify(data));
      } else {
        setCustomers([]);
        setFilteredCustomers([]);
        setError("No Customer Found");
      }
    } catch (err) {
      setCustomers([]);
      setFilteredCustomers([]);
      setError("Failed to fetch customers");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCustomers();

    const handleStorageChange = () => {
      const savedCustomer = localStorage.getItem("selectedCustomer");
      if (savedCustomer) {
        const customer = JSON.parse(savedCustomer);
        setSelectedCustomer(customer);
        setSearchTerm(`${customer.mobile_no} | ${customer.customer_name}`);
        setCustomerSelected(true);
      }
    };

    window.addEventListener("storage", handleStorageChange);

    // Initial check
    handleStorageChange();

    // Cleanup
    return () => {
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []);

  useEffect(() => {
    if (customerSelected && selectedCustomer) {
      getCustomerDetails(selectedCustomer.name);
    }
  }, [customerSelected, selectedCustomer]);

  const handleSetLoyaltyProgram = (res) => {
    if (
      res.data &&
      res.data.message &&
      Array.isArray(res.data.message.customer)
    ) {
      const customer = res.data.message.customer[0];
      if (customer && customer.loyalty_program) {
        setLoyaltyProgram(customer.loyalty_program);
      }
    } else {
      setLoyaltyProgram(null);
    }
  };

  const getCustomerDetails = async (customerName) => {
    try {
      const res = await getCustomerDetail(customerName);
      if (res.status === 200) {
        setCustomerSelectedDetails(res.data.message);
        handleSetLoyaltyProgram(res);
      } else {
        console.log("error fetching details of customer");
      }
    } catch (error) {
      console.error("Error fetching customer details:", error);
    }
  };

  // {customerSelectedDetails.customer.map((customer, index) => (
  //   loyalProgram = customer.loyalty_program,
  // ))}

  useEffect(() => {
    if (searchTerm) {
      const filtered = customers.filter(
        (customer) =>
          (customer.customer_name &&
            customer.customer_name
              .toLowerCase()
              .includes(searchTerm.toLowerCase())) ||
          (customer.mobile_no &&
            customer.mobile_no.toLowerCase().includes(searchTerm.toLowerCase()))
      );
      setFilteredCustomers(filtered);
      setShowAddCustomerForm(filtered.length === 0 && !selectedCustomer);
    } else {
      setFilteredCustomers(customers);
      setShowAddCustomerForm(false);
    }
  }, [searchTerm, customers, selectedCustomer]);

  const handleAddCustomer = (newCustomer) => {
    setCustomers([...customers, newCustomer]);
    setSelectedCustomer(newCustomer);
    setSearchTerm(`${newCustomer.mobile_no} | ${newCustomer.customer_name}`);
    localStorage.setItem("selectedCustomer", JSON.stringify(newCustomer));
    setShowAddCustomerForm(false); // Remove form is hidden after adding customer
  };

  const customerMenu = (
    <Menu>
      {filteredCustomers.length > 0 ? (
        filteredCustomers.map((customer) => (
          <Menu.Item
            key={customer.mobile_no}
            onClick={() => handleCustomerSelect(customer)}
          >
            {customer.mobile_no} | {customer.customer_name}
          </Menu.Item>
        ))
      ) : (
        <Menu.Item disabled>No Data Found</Menu.Item>
      )}
      {/* Conditionally render AddCustomerForm only if no customer is selected */}
      {!selectedCustomer && showAddCustomerForm && (
        <Menu.Item key="addCustomer">
          <AddCustomerForm
            searchTerm={searchTerm}
            onAddCustomer={handleAddCustomer}
          />
        </Menu.Item>
      )}
    </Menu>
  );

  const stockQtyMap = cartItems.reduce((map, cartItem) => {
    const stockQty =
      cartItem.stock.length > 0 ? cartItem.stock[0].stock_qty : 0;
    map[cartItem.id] = stockQty;
    return map;
  }, {});

  const handleIncrement = (index) => {
    const updatedCartItems = [...cartItems];
    const selectedItem = updatedCartItems[index];
    const stockQty = stockQtyMap[selectedItem.id];

    if (selectedItem.quantity < stockQty) {
      updatedCartItems[index].quantity += 1;
      setCartItems(updatedCartItems);
    } else {
      Modal.warning({
        title: "Stock Limit Reached",
        content: `Cannot add more ${selectedItem.name}. Available stock: ${stockQty}.`,
      });
    }
  };

  const handleDecrement = (index) => {
    const updatedCartItems = [...cartItems];
    if (updatedCartItems[index].quantity > 1) {
      updatedCartItems[index].quantity -= 1;
      setCartItems(updatedCartItems);
    }
  };

  const handleRemoveFromCart = (index) => {
    const updatedCartItems = cartItems.filter((_, i) => i !== index);
    setCartItems([]);
    setValidatedPromoCode("");
    setCouponDiscount(0);
    setPromoCode("");
    setIsPromoCodeValid(false);
    handleRemoveLoyaltyPoints();
    localStorage.removeItem("promoCode");
    localStorage.removeItem("couponDiscount");
    localStorage.removeItem("originalPrices");
    setCartItems(updatedCartItems);
    const itemId = cartItems[index].id;
    removeItemFromCart(itemId);
  };

  const handleEmptyCart = () => {
    setCartItems([]);
    setSelectedCustomer(null);
    setSearchTerm("");
    setValidatedPromoCode("");
    setCouponDiscount(0);
    setPromoCode("");
    setIsPromoCodeValid(false);
    handleRemoveLoyaltyPoints();
    localStorage.removeItem("promoCode");
    localStorage.removeItem("couponDiscount");
    localStorage.removeItem("selectedCustomer");
    localStorage.removeItem("originalPrices");
    resetCart();
  };

  const handleParkOrder = () => {
    if (!selectedCustomer) {
      Modal.error({
        title: "Attention!",
        content: "Please select a customer before parking the order.",
        className: "customer-error-modal",
      });
      return;
    }

    let parkedOrders = JSON.parse(localStorage.getItem("parkedOrders"));
    if (!Array.isArray(parkedOrders)) {
      parkedOrders = [];
    }
    const newParkedOrder = {
      name: new Date().getTime(),
      items: cartItems,
      subtotal: subtotal,
      total: totalWithTax,
      grand_total: totalWithTax,
      loyalty_amount: loyaltyAmount,
      customer: {
        customer_name: selectedCustomer.customer_name,
        mobile_no: selectedCustomer.mobile_no,
        name: selectedCustomer.name,
      },
      status: "cartItems",
      creation: new Date().toLocaleString(),
      contact_name: selectedCustomer.customer_name || "Guest",
      contact_mobile: selectedCustomer.mobile_no || "N/A",
    };

    parkedOrders.push(newParkedOrder);
    localStorage.setItem("parkedOrders", JSON.stringify(parkedOrders));
    localStorage.removeItem("couponDiscount");
    localStorage.removeItem("promoCode");
    setCartItems([]);
    setPromoCode("");
    setDiscountAmount(0);
    setSelectedCustomer(null);
    setSearchTerm("");
    setCouponCodes("");
    setCouponDiscount("");
    setValidatedPromoCode("");
    setRedeem(0);
    setCustomerSelectedDetails([]);
    setLoyaltyAmount(0);
    setLoyaltyInput("");
    localStorage.removeItem("GiftCardDiscount");
    setGiftCardDiscount("");
    setGiftCard("");
    setIsGiftCardValid(false);
    setIsPromoCodeValid(false);

    localStorage.removeItem("cartItems");
    localStorage.removeItem("selectedCustomer");
    localStorage.removeItem("CustomerDetails");

    Modal.success({
      message: "Success",
      content: "Order parked successfully.",
    });
  };

  // Function to format date to "YYYY-MM-DD HH:MM"
  const formatDateTime = (date) => {
    const pad = (n) => (n < 10 ? "0" + n : n);
    return (
      date.getFullYear() +
      "-" +
      pad(date.getMonth() + 1) +
      "-" +
      pad(date.getDate()) +
      " " +
      pad(date.getHours()) +
      ":" +
      pad(date.getMinutes()) +
      ":" +
      pad(date.getSeconds())
    );
  };

  // Function to format date to "YYYY-MM-DD"
  const formatDate = (date) => {
    const pad = (n) => (n < 10 ? "0" + n : n);
    return (
      date.getFullYear() +
      "-" +
      pad(date.getMonth() + 1) +
      "-" +
      pad(date.getDate())
    );
  };
  // const subtotal = calculateSubtotal(cartItems);
  // const tax = subtotal * taxRate;
  let grandTotal = totalWithTax - loyaltyAmount - discountAmount;
  grandTotal = Math.max(grandTotal - couponDiscount, 0);
  const placeOrder = async (customer) => {
    if (grandTotal <= 0) {
      Modal.error({
        title: "Please add more items.",
        className: "success-modal",
      });
    }
    const savedCustomer = JSON.parse(localStorage.getItem("selectedCustomer"));
    if (!savedCustomer || cartItems.length === 0) return;

    const now = new Date();
    const transactionDate = formatDateTime(now);
    const deliveryDate = formatDate(
      new Date(now.getTime() + 24 * 60 * 60 * 1000)
    );
    const openingShiftResponse = JSON.parse(
      localStorage.getItem("openingShiftResponse")
    );
    const user = JSON.parse(localStorage.getItem("user"));

    const costCenter = localStorage.getItem("costCenter");

    const orderDetails = {
      pos_profile: openingShiftResponse?.message?.pos_profile?.name || "",
      pos_opening_shift:
        openingShiftResponse?.message?.pos_opening_shift?.name || "",
      hub_manager: user.email,
      customer: customer.name || customer.customer_name || customer,
      customer_name: customer.name,
      transaction_date: transactionDate,
      delivery_date: deliveryDate,
      items: cartItems.map((item) => ({
        item_code: item.id,
        item_name: item.name,
        rate: item.product_price,
        sub_items: [],
        qty: item.quantity,
        ordered_price: item.product_price * item.quantity,
        tax: item.tax || [],
        estimated_time: 30,
      })),
      mode_of_payment: selectedPaymentMethod || "Credit",
      mpesa_No: "",
      tax: [],
      cost_center: costCenter,
      source: "POS",
      coupon_code: promoCode,
      grand_total: grandTotal,
      redeem_loyalty_points: redeem,
      loyalty_points: loyaltyInput,
      loyalty_amount: loyaltyAmount,
      loyalty_program: loyaltyProgram,
      loyalty_redemption_account: loyaltyRedemptionAccount,
      discount_amount: discountAmount,
      gift_card_code: giftCard,
    };

    try {
      const res = await createSalesOrder(orderDetails);
      console.log(res);
      if (res && res.message && res.message.success_key === 1) {
        Modal.success({
          title: "Congratulations!",
          content: (
            <>
              <div>
                Order placed successfully.
                {/* <br />
                <strong>to {customer.customer_name || customer}</strong> */}
              </div>
            </>
          ),
          className: "success-modal",
        });
        completeOrder();
        setCartItems([]);
        setSelectedCustomer(null);
        setSearchTerm("");
        setCouponCodes("");
        setCouponDiscount("");
        setValidatedPromoCode("");
        localStorage.removeItem("selectedCustomer")
        localStorage.removeItem("couponDiscount");
        localStorage.removeItem("promoCode");
        setRedeem(0);
        setCustomerSelectedDetails([]);
        setLoyaltyAmount(0);
        setLoyaltyInput("");
        localStorage.removeItem("GiftCardDiscount");
        setGiftCardDiscount("");
        setGiftCard("");
        localStorage.removeItem("cashTransaction");
        setDiscountAmount(0);
        setIsGiftCardValid(false);
        setIsPromoCodeValid(false);
        setStoredPassword("");
        setSelectedPaymentMethod("");
      } else {
        console.log(`Error placing order: ${error.message}`);
        setCouponCodes("");
        setCouponDiscount("");
        setValidatedPromoCode("");
        setGiftCard("");
        localStorage.removeItem("couponDiscount");
        localStorage.removeItem("promoCode");
        grandTotal = 0;
        setDiscountAmount(0);
        setIsGiftCardValid(false);
        setIsPromoCodeValid(false);
        setStoredPassword("");
        setSelectedPaymentMethod("");
      }
    } catch (error) {
      console.log(`Error placing order: ${error.message}`);
    }
  };

  const handleSelectPaymentMethod = (method) => {
    setSelectedPaymentMethod(method);
  };

  const handlePlaceOrder = async () => {
    if (!selectedCustomer) {
      Modal.error({
        title: "Attention!",
        content: "Please select a customer before placing the order.",
        className: "customer-error-modal",
      });
      return;
    }

    if (!selectedPaymentMethod) {
      notification.error({
        message: "Payment Method Required",
        description: "Please select a payment method before placing the order.",
      });
      return;
    }

    await placeOrder(selectedCustomer);
  };

  const handleGetGuestCustomer = async () => {
    try {
      const res = await getGuestCustomer();
      if (res.status === 200) {
        const guestCustomer = res.data.message.data.guest_customer;
        setLoyaltyRedemptionAccount(
          res.data.message.data.loyalty_redemption_account
        );
        setEditpriceDiscount(
          res.data.message.data.edit_price_discount_in_percentage
        );
        setGuestCustomer(guestCustomer);
        console.log("Guest customer", guestCustomer);
      } else {
        console.log("Error in getting the Guest Customer");
      }
    } catch (error) {
      console.log("Error in fetching guest customer:", error.message);
    }
  };

  useEffect(() => {
    handleGetGuestCustomer();
  }, []);
  
 
  const validatePriceChange = (index) => {
    const originalPrices = JSON.parse(localStorage.getItem("originalPrices"));
    const cartItem = cartItems[index];

    if (!originalPrices) {
      console.error("Original prices not found in localStorage.");
      return;
    }

    if (!cartItem) {
      console.error(`Cart item at index ${index} not found.`);
      return;
    }

    const originalPrice = originalPrices[cartItem.id];

    if (originalPrice === undefined) {
      console.error(`Original price for item ID ${cartItem.id} not found.`);
      return;
    }

    const newPrice = parseFloat(editedPrices[cartItem.id]);
    if (isNaN(newPrice)) {
      console.error(
        `Invalid price entered for item at index ${index}: ${
          editedPrices[cartItem.id]
        }`
      );
      return;
    }

    const minPrice = originalPrice * (1 - editPriceDiscount / 100);
    const maxPrice = originalPrice * (1 + editPriceDiscount / 100);

    if (newPrice < minPrice || newPrice > maxPrice) {
      setAuthPendingItem({ id: cartItem.id, index, newPrice, originalPrice });
      setAuthModalVisible(true);
    } else {
      const newCartItems = [...cartItems];
      newCartItems[index].product_price = newPrice;
      setCartItems(newCartItems);
      setEditedPrices((prev) => {
        const updatedPrices = { ...prev };
        delete updatedPrices[cartItem.id];
        return updatedPrices;
      });
    }
  };

  const handleAuth = async () => {
    try {
      if (!storedPassword) {
        const response = await login(email, password);
        if (response.message.success_key === 1) {
          setStoredPassword(password);
          updateCartWithNewPrice();
        } else {
          alert("Authorization failed");
          resetToOriginalPrice();
        }
      } else {
        if (password === storedPassword) {
          updateCartWithNewPrice();
        } else {
          alert("Authorization failed");
          resetToOriginalPrice();
        }
      }
    } catch (error) {
      console.error("Authorization error:", error);
      alert("Authorization error");
      resetToOriginalPrice();
    } finally {
      setAuthPendingItem(null);
      setAuthModalVisible(false);
      setPassword("");
    }
  };

  const updateCartWithNewPrice = () => {
    const newCartItems = [...cartItems];
    const { id, index, newPrice } = authPendingItem;
    newCartItems[index].product_price = newPrice;
    setCartItems(newCartItems);
    setLastAuthorizedPrices((prev) => ({ ...prev, [id]: newPrice }));
    setEditedPrices((prev) => {
      const updatedPrices = { ...prev };
      delete updatedPrices[id];
      return updatedPrices;
    });
  };

  const resetToOriginalPrice = () => {
    const { id, originalPrice } = authPendingItem;
    setEditedPrices((prev) => ({
      ...prev,
      [id]:
        lastAuthorizedPrices[id] !== undefined
          ? lastAuthorizedPrices[id]
          : originalPrice,
    }));
  };

  const handleAuthCancel = () => {
    resetToOriginalPrice();
    setAuthModalVisible(false);
    setPassword("");
  };

  const renderCartItems = () => {
    if (cartItems.length === 0) {
      return (
        <div className="empty-cart">
          <img src={EmptyCart} alt="Empty Cart" />
          <h2>No items in the cart</h2>
        </div>
      );
    }

    const calculateTotalTaxPercentage = (item) => {
      if (!item.tax || item.tax.length === 0) return "0.0%";

      const totalPercentage = item.tax.reduce((total, taxEntry) => {
        return total + parseFloat(taxEntry.custom_tax_percentage);
      }, 0);

      return `${totalPercentage}%`;
    };

    // Helper to calculate the price including selected attributes
    const calculateItemPriceWithAttributes = (item) => {
      let itemPrice = item.product_price;

      if (item.selectedAttributes) {
        Object.keys(item.selectedAttributes).forEach((attributeIndex) => {
          const selectedOptions = item.selectedAttributes[attributeIndex];

          selectedOptions.forEach((selectedItemName) => {
            const attribute = item.attributes[attributeIndex];
            const selectedOption = attribute.options.find(
              (option) => option.item_name === selectedItemName
            );

            if (selectedOption && selectedOption.price) {
              itemPrice += selectedOption.price; // Add the price of the selected attribute
            }
          });
        });
      }

      return itemPrice;
    };

    return cartItems.map((item, index) => {
      const totalTaxRate = item?.tax?.length
        ? item.tax.reduce((acc, tax) => acc + tax.rate, 0)
        : 0;

      const finalItemPrice = calculateItemPriceWithAttributes(item);

      return (
        <div key={index} className="cart-item">
          <span className="cart-item-name">{item.name}</span>

          {/* Tax Rate Column */}
          <span className="cart-item-taxrate">
            {calculateTotalTaxPercentage(item)}
          </span>

          {/* Unit Price Input */}
          <span className="cart-item-unitprice">
            <Input disabled
              type="number"
              value={
                editedPrices[item.id] !== undefined
                  ? editedPrices[item.id]
                  : finalItemPrice
              }
            
              onBlur={() => validatePriceChange(index)}
              className="unit-price-input"
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  validatePriceChange(index);
                }
              }}
              step="any"
            />
          </span>

          {/* Quantity Controls */}
          <span className="cart-item-qty quantity-control">
            <Button onClick={() => handleDecrement(index)}>-</Button>
            <span>{item.quantity}</span>
            <Button onClick={() => handleIncrement(index)}>+</Button>
          </span>

          {/* Total Price */}
          <span className="cart-item-totalprice">
            {themeSettings?.currency_symbol || "$"}
            {(finalItemPrice * item.quantity).toFixed(2)}
          </span>

          {/* Delete Action */}
          <span className="cart-item-action">
            <img
              src={DeleteImg}
              alt="Delete"
              onClick={() => handleRemoveFromCart(index)}
              style={{ cursor: "pointer", marginRight: "4px" }}
            />
          </span>
        </div>
      );
    });
  };

  const handleClearStorage = () => {
    // localStorage.clear();
    sessionStorage.clear();
    console.log("Local storage and session storage cleared");
  };

  useEffect(() => {
    handleClearStorage();
  }, []);

  const handleLoyaltyInputChange = (e) => {
    const value = e.target.value;
    const parsedValue = parseInt(value, 10);
    if (value === "") {
      setLoyaltyInput("");
      setRedeem(0);
    } else if (!isNaN(parsedValue)) {
      if (parsedValue <= customerSelectedDetails.loyalty_points) {
        setLoyaltyInput(parsedValue);
        setRedeem(1);
      } else {
        notification.error({
          message: "Invalid Loyalty Points",
          description: `You cannot enter more than ${customerSelectedDetails.loyalty_points} loyalty points`,
        });
      }
    }
  };

  const handleRemoveLoyaltyPoints = () => {
    setLoyaltyInput("");
    setIsLoyaltyPointsValid(false);
    setLoyaltyAmount(0);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const appliedPoints =
      loyaltyInput * customerSelectedDetails.conversion_factor;
    setLoyaltyAmount(appliedPoints);
    setIsLoyaltyPointsValid(true);
  };

 

  const handleRemoveGiftCard = () => {
    setGiftCard("");
    setIsGiftCardValid(false);
    setGiftCardDiscount(0);
    localStorage.removeItem("GiftCardDiscount");
    setGiftCardDiscount("");
    notification.info({
      message: "Gift card Removed",
      description: `Gift card has been removed.`,
    });
  };

  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const isguestCustomer = selectedCustomer?.customer_name === "Guest Customer";

  

  return (
    <div className="cartItems">
      {console.log(cartItems)}
      <div>
        <ul className="tab-header">
         
          <li className="active"></li>
        </ul>
        <div className="tab-content">
          <div
            className={`tab-pane ${selectedTab === "Takeaway" ? "active" : ""}`}
          >
            <div className="quick-order">
              <div className="cart-search-cont">
                <div className="cart-search">
                  <AutoComplete
                    options={customerOptions}
                    onSelect={(value, option) =>
                      handleCustomerSelect(option.customer)
                    }
                    onSearch={handleSearchChange}
                    placeholder="Search by Customer Name/Number"
                    value={searchTerm}
                    onChange={(value) => setSearchTerm(value)} // Ensure onChange is added to update searchTerm
                    onFocus={() => setIsInputFocused(true)}
                  />

                  {loading && <Spin />}
                  {filteredCustomers.length === 0 &&
                    searchTerm &&
                    showAddCustomerForm && (
                      <AddCustomerForm
                        searchTerm={searchTerm}
                        onAddCustomer={handleAddCustomer}
                      />
                    )}
                </div>
              </div>
            
            </div>
            <div className="cart-header d-flex justify-content-between">
              <div className="cart-head-left">
                <h3>Cart</h3>
                {/* <span className="cart-head-items">
                  {cartItems.length} Items
                </span>
                <span className="cart-head-total">
                  Total - ${grandTotal.toFixed(2)}
                </span> */}
              </div>
              <div className="cart-head-right">
                <button
                  onClick={handleEmptyCart}
                  disabled={cartItems.length === 0}
                >
                  Reset Order
                </button>
                <button
                  onClick={handleParkOrder}
                  disabled={cartItems.length === 0}
                >
                  Park
                </button>
              </div>
            </div>
            <div className="cart-body">
              {cartItems.length === 0 ? (
                <div className="empty-cart">
                  <img src={EmptyCart} alt="Empty Cart" />
                </div>
              ) : (
                <>
                  <div className="cart-item-cont">
                    <div className="cart-item cart-item-head">
                      <span className="cart-item-name">Product Name</span>
                      <span className="cart-item-taxrate">Tax Rate</span>{" "}
                      {/* New Tax Rate Column */}
                      <span className="cart-item-unitprice">Unit Price</span>
                      <span className="cart-item-qty">Qty</span>
                      <span className="cart-item-totalprice">Total</span>
                      <span className="cart-item-action">&nbsp;</span>
                    </div>
                    {renderCartItems()}
                  </div>
                  <div className="cart-sub-total">
                    <span>Subtotal</span>
                    <span>
                      {themeSettings?.currency_symbol || "$"}
                      {subtotal.toFixed(2)}
                    </span>
                  </div>
                
                  <div className="cart-footer">
                    <div className="cart-summary">
                     
                      <div className="tax-header" onClick={toggleTaxExpand}>
                        <span>{isTaxExpanded ? "▼" : "►"} Total Tax</span>
                        <span>
                          {themeSettings?.currency_symbol || "$"}
                          {groupTaxesByRate(cartItems)
                            .reduce(
                              (total, group) => total + group.totalTaxAmount,
                              0
                            )
                            .toFixed(2)}
                        </span>
                      </div>

                      {isTaxExpanded && (
                        <span className="tax-details-section">
                          {groupTaxesByRate(cartItems).map(
                            (group, index, array) => (
                              <span
                                key={index}
                                className={`tax-group ${
                                  index % 2 === 1 && index !== array.length - 1
                                    ? "with-separator sgst"
                                    : ""
                                }${
                                  index === array.length - 1 ? "last-tax" : ""
                                }`}
                              >
                                {/* Display CGST or SGST with percentage */}
                                <span className="tax-name">
                                  {group.taxLabel}{" "}
                                  {parseFloat(group.custom_tax_percentage)}%
                                </span>
                                <span className="tax-amount">
                                  {themeSettings?.currency_symbol || "$"}
                                  {group.totalTaxAmount.toFixed(2)}
                                </span>
                              </span>
                            )
                          )}
                        </span>
                      )}
                      {/* <div className="total-tax">
                        <span>Total Tax</span>
                        <span>
                          {themeSettings?.currency_symbol || "$"}
                          {totalTax.toFixed(2)}
                        </span>
                      </div> */}
                      {/* <div>
                        <span>Tax</span>
                        <span>${totalTax.toFixed(2)}</span>
                      </div> */}
                    </div>
                    {/* <div className="cart-grand-total">
                      <span>Grand Total</span>
                      <span>${grandTotal.toFixed(2)}</span>
                    </div> */}
                    {/* <div className="order-note">
                      <span className="order-request">Order Request</span>
                        <input
                          type="text"
                          placeholder="Enter your order request"
                          // value={orderRequest}
                          // onChange={(e) => setOrderRequest(e.target.value)}
                          className="form-control p-0"
                          style={{ border: "none", boxShadow: "none" }}
                        />
                    </div> */}
                  </div>
                </>
              )}
            </div>
          </div>
          <div
            className={`tab-pane ${selectedTab === "Delivery" ? "active" : ""}`}
          >
            <h2>Delivery</h2>
            <div className="quick-order">
              <Button className="quick-order-btn">Quick Order</Button>
            </div>
            <div className="cart-header d-flex justify-content-between">
              <div className="cart-head-left">
                <h3>Cart</h3>
                <span className="cart-head-items">
                  {cartItems.length} Items
                </span>
                <span className="cart-head-total">
                  Total - {themeSettings?.currency_symbol || "$"}
                  {subtotal.toFixed(2)}
                </span>
              </div>
              <div className="cart-head-right">
                <button>Empty cart</button>
                <button>Park</button>
              </div>
            </div>
            <div className="cart-body">
              {cartItems.length === 0 ? (
                <div className="empty-cart">
                  <img src={EmptyCart} alt="Empty Cart" />
                </div>
              ) : (
                <>
                  <div className="cart-item-cont">
                    <div className="cart-item cart-item-head">
                      <span className="cart-item-name">Product Name</span>
                      <span className="cart-item-unitprice">Unit Price</span>
                      <span className="cart-item-qty">&nbsp;</span>
                      <span className="cart-item-totalprice">Total</span>
                      <span className="cart-item-action">&nbsp;</span>
                    </div>
                    {cartItems.map((item, index) => (
                      <div key={index} className="cart-item">
                        <span className="cart-item-name">{item.name}</span>
                        <span className="cart-item-unitprice">
                          {themeSettings?.currency_symbol || "$"}
                          {item.product_price}
                        </span>
                        <span className="cart-item-qty quantity-control">
                          <Button onClick={() => handleDecrement(index)}>
                            -
                          </Button>
                          <span>{item.quantity}</span>
                          <Button onClick={() => handleIncrement(index)}>
                            +
                          </Button>
                        </span>
                        <span className="cart-item-totalprice">
                          {themeSettings?.currency_symbol || "$"}
                          {(item.product_price * item.quantity).toFixed(2)}
                        </span>
                        <span className="cart-item-action">
                          <img
                            src={DeleteImg}
                            alt="Delete"
                            onClick={() => handleRemoveFromCart(index)}
                            style={{ cursor: "pointer", marginRight: "4px" }}
                          />
                        </span>
                      </div>
                    ))}
                  </div>
                  <div className="cart-sub-total">
                    <span>Subtotal</span>
                    <span>
                      {themeSettings?.currency_symbol || "$"}
                      {subtotal.toFixed(2)}
                    </span>
                  </div>

                  <div className="promocode">
                    <div>
                      <label>Enter Promo Code</label>
                      <span className="promo-input-wrap">
                        <input type="text" placeholder="" />
                        <Button type="submit">
                          <img src={ButtonTick} alt="" />
                        </Button>
                      </span>
                    </div>
                    <div>
                      <label>Enter Promo Code</label>
                      <span className="promo-input-wrap">
                        <input type="text" placeholder="" />
                        <Button type="submit">
                          <img src={ButtonTick} alt="" />
                        </Button>
                      </span>
                    </div>
                    <div>
                      <label>Enter Promo Code</label>
                      <span className="promo-input-wrap">
                        <input type="text" placeholder="" />
                        <Button type="submit">
                          <img src={ButtonCross} alt="" />
                        </Button>
                      </span>
                    </div>
                  </div>
                  <div className="cart-footer">
                    <div className="cart-summary">
                      <div>
                        <span>
                          Promo Code - <span className="deal-name">DEAL20</span>
                        </span>
                        <span className="color-text">
                          - ${discount.toFixed(2)}
                        </span>
                      </div>
                      <div>
                        <span>Loyalty Points</span>
                        <span className="color-text">
                          - ${discount.toFixed(2)}
                        </span>
                      </div>
                      <div>
                        <span>Tax</span>
                        <span>${totalTax.toFixed(2)}</span>
                      </div>
                    </div>
                    <div className="cart-grand-total">
                      <span>Grand Total</span>
                      <span>${grandTotal.toFixed(2)}</span>
                    </div>
                    <div className="cart-header d-flex justify-content-between">
                      <div className="order-controls">
                        <Button
                          type={
                            selectedPaymentMethod === "Cash"
                              ? "primary"
                              : "default"
                          }
                          onClick={() => handleSelectPaymentMethod("Cash")}
                        >
                          <img src={IconCash} alt="" />
                          Cash
                        </Button>
                        <Button
                          type={
                            selectedPaymentMethod === "Card"
                              ? "primary"
                              : "default"
                          }
                          onClick={() => handleSelectPaymentMethod("Card")}
                        >
                          <img src={IconCard} alt="" />
                          Card
                        </Button>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
      {/* <div className="place-order">
        <Button
          type="primary"
          className="cart-place-order-btn"
          disabled={cartItems.length === 0}
          onClick={handlePlaceOrder}
          id="Placeorder-button"
        >
          Place Order
        </Button>
      </div> */}
     
      <CashPaymentPopup
        total={grandTotal}
        isVisible={isPopupVisible}
        onClose={handlePopupClose}
        handlePlaceOrder={handlePlaceOrder}
      />
      <div className="cart-footer-cards d-flex justify-content-between">
        <div className="d-flex flex-column cart-place-order">
          <span className="">{cartItems.length} Items</span>
          <span className="cart-head-total">
            {themeSettings?.currency_symbol || "$"}
            {grandTotal.toFixed(2)}
          </span>
        </div>
        <div className="order-controls">
          <Button
            className="cash-card-btn"
            type={selectedPaymentMethod === "Cash" ? "primary" : "default"}
            onClick={() => {
              handleSelectPaymentMethod("Cash");
              handleCashButtonClick();
            }}
          >
            <img src={IconCash} alt="" />
            Cash
          </Button>
          <Button
            className="cash-card-btn"
            type={selectedPaymentMethod === "Card" ? "primary" : "default"}
            onClick={() => handleSelectPaymentMethod("Card")}
          >
            <img src={IconCard} alt="" />
            Card
          </Button>
        
        </div>
      </div>
      {authModalVisible && (
        <Modal
          visible={authModalVisible}
          onCancel={handleAuthCancel}
          footer={null}
          className="Auth-modal"
        >
          <div className="text-center">
            <h3>Authorization Required</h3>
            <p>
              The new price is outside the allowed range. Please authorize this
              change.
            </p>
          </div>
          <Input className="Auth-input" type="text" value={email} readOnly />
          <Input
            type="password"
            placeholder="Enter your password"
            className="Auth-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <div className="authbtndiv">
            <button className="Authbtn" onClick={handleAuth}>
              Authorize
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default Cart;
