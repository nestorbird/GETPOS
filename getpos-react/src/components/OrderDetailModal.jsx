import React, { useEffect, useState } from "react";
import { Checkbox, Modal, message } from "antd";
import { returnSalesOrder } from "../modules/LandingPage";

const OrderDetailModal = ({ visible, onClose, order, onUpdateOrder, currency }) => {
  const [selectedItems, setSelectedItems] = useState({});
  const [itemQuantities, setItemQuantities] = useState({});
  const [disabledInputs, setDisabledInputs] = useState({});
  const [loading, setLoading] = useState(false);
  const [returnedItems, setReturnedItems] = useState(null);


  console.log(order,"checking in the order modal")
  

  useEffect(() => {
    if (order) {
      const initialSelected = {};
      order.items.forEach((item) => {
        initialSelected[item.item_code] = false;
      });
      setSelectedItems(initialSelected);

      const initialQuantities = {};
      order.items.forEach((item) => {
        initialQuantities[item.item_code] = item.qty;
      });
      setItemQuantities(initialQuantities);

      const initialDisabled = {};
      order.items.forEach((item) => {
        initialDisabled[item.item_code] = true;
      });
      setDisabledInputs(initialDisabled);
    }
  }, [order]);

  if (!order) return null;

  const getReturnStatusText = (status) => {
    if (status === "Fully") {
      return "This order is fully returned.";
    } else if (status === "Partially") {
      return "This order is partially returned.";
    } else {
      return "";
    }
  };

  const handleCheckboxChange = (itemCode) => {
    setSelectedItems((prevSelectedItems) => ({
      ...prevSelectedItems,
      [itemCode]: !prevSelectedItems[itemCode],
    }));

    setDisabledInputs((prevDisabledInputs) => ({
      ...prevDisabledInputs,
      [itemCode]: !prevDisabledInputs[itemCode],
    }));
  };

  const handleQuantityChange = (itemCode, quantity) => {
    const item = order.items.find((item) => item.item_code === itemCode);
    if (!item) return;

    quantity = parseInt(quantity) || 0;

    if (quantity > item.qty) {
      message.error("Quantity cannot exceed purchased quantity.");
      quantity = item.qty;
    }

    setItemQuantities((prevQuantities) => ({
      ...prevQuantities,
      [itemCode]: quantity,
    }));
  };

  const handleReturnItems = async () => {
    const returnItems = {};
    order.items.forEach((item) => {
      returnItems[item.item_code] = 0;
    });

    Object.keys(selectedItems).forEach((itemCode) => {
      if (selectedItems[itemCode]) {
        const item = order.items.find((item) => item.item_code === itemCode);
        if (item) {
          returnItems[itemCode] = itemQuantities[itemCode];
        } else {
          console.warn(`Item with item_code ${itemCode} not found in order.`);
        }
      }
    });

    let total_qty = Object.keys(returnItems).length;

    const salesInvoice = {
      sales_order_number: order.name,
      return_items: returnItems,
      total_qty: total_qty,
      return_type: "Partially",
    };

    try {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 1500));

      const response = await returnSalesOrder(salesInvoice);
      console.log("Return API Response:", response);

      if (response && response.message && response.message.success_key === 1) {
        const returnedItems = [];
        Object.keys(selectedItems).forEach((itemCode) => {
          if (selectedItems[itemCode] && itemQuantities[itemCode] > 0) {
            const item = order.items.find(
              (item) => item.item_code === itemCode
            );
            if (item) {
              returnedItems.push({
                item_name: item.item_name,
                qty: itemQuantities[itemCode],
                amount: itemQuantities[itemCode] * item.rate,
              });
            }
          }
        });

        // Calculate the total amount for the returned items
        const totalAmount = returnedItems.reduce((sum, item) => sum + item.amount, 0);
        const taxAmount = totalAmount * 0.10; // Calculate tax at 10%

        setReturnedItems(returnedItems);

        const returnedItemsContent = returnedItems.map((item, index) => (
          <div key={index} className="return-details">
            <span>
              <strong>Returned items:</strong> {item.item_name} <br />
            </span>
            <span>
              <strong>ID:</strong> {order.name}
            </span> 
            <br />
            <span>
              <strong>Amount:</strong> 
              <span className="text-red">-${item.amount.toFixed(2)}</span>
            </span>
            <br />
          </div>
        ));

        Modal.success({
          message: "Success",
          content: (
            <>
              Order Returned Successfully!
              <br />
              {returnedItemsContent}
              {/* <strong>Tax (10%):</strong> <span className="text-red">-${taxAmount.toFixed(2)}</span> */}
            </>
          ),
        });

        // Call the callback function to update the order status
        onUpdateOrder(order.name, "Partially");
      } else {
        console.error(
          "Error returning items:",
          response.message ? response.message : "Unknown error"
        );
      }
    } catch (error) {
      console.error("Error returning items:", error);
    } finally {
      setLoading(false);
      onClose();
    }
  };

  const handleReturnOrder = async () => {
    const returnItems = {};
    order.items.forEach((item) => {
      returnItems[item.item_code] = item.qty;
    });

    const salesInvoice = {
      sales_order_number: order.name,
      return_items: returnItems,
      total_qty: order.items.length,
      return_type: "Fully",
    };

    try {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 1500));

      const response = await returnSalesOrder(salesInvoice);
      console.log("Return API Response:", response);

      if (response && response.message && response.message.success_key === 1) {
        const totalAmount = order.grand_total;
        const taxAmount = totalAmount * 0.10; // Calculate tax at 10%

        Modal.success({
          message: "Success",
          content: (
            <>
              Full Order Returned Successfully!
              <br />
              <strong>ID:</strong> {order.name}
              <br />
              <strong>Amount:</strong>
              <span className="text-red">
                - {(currency || "$")}{totalAmount.toFixed(2)}
              </span>
              {/* <br />
              <strong>Tax (10%):</strong> <span className="text-red">-${taxAmount.toFixed(2)}</span> */}
            </>
          ),
        });
        // Call the callback function to update the order status
        onUpdateOrder(order.name, "Fully");
      } else {
        console.error(
          "Error returning items:",
          response.message ? response.message : "Unknown error"
        );
      }
    } catch (error) {
      console.error("Error returning items:", error);
    } finally {
      setLoading(false);
      onClose();
    }
  };

  const isReturnItemsDisabled = !Object.values(selectedItems).some(
    (isSelected) => isSelected
  ) || Object.values(itemQuantities).filter((quantity) => quantity === 0).length > 0 || loading;
  
  const isReturnOrderDisabled = Object.values(selectedItems).some(
    (isSelected) => isSelected
  ) || Object.values(itemQuantities).filter((quantity) => quantity === 0).length > 0;

  const modalClassName = `order-detail ${
    order.return_order_status === "Fully" ? "returned" : ""
  } ${order.return_order_status === "Partially" ? "returned" : ""}`;

  return (
    <Modal
      visible={visible}
      onCancel={onClose}
      footer={null}
      className={modalClassName}
    >
      {loading && (
        <div className="loading-message">
          <p>Return Processing ...</p>
        </div>
      )}
      <h3>
        <span>ID: {order.name} </span> <span>{(currency || "$")}{order.grand_total.toFixed(2)}</span>
      </h3>
      <span className="return-msg">
        {getReturnStatusText(order.return_order_status)}
      </span>
      <p className="order-time">
        <p>{order.transaction_date}, {order.transaction_time}</p>
        <p>{order.mode_of_payment}</p>
      </p>
      <p className="order-cus-details">
        {order.contact_mobile} <span> {order.customer_name}</span>
      </p>

      <ul className="order-items">
        {order.items.map((item, index) => (
          <li key={index}>
            
            <span className="select-name">
            {order.mode_of_payment !== "Credit" && (
              <Checkbox
                className="custom-checkbox"
                onChange={() => handleCheckboxChange(item.item_code)}
                checked={selectedItems[item.item_code]}
              />
              )}
              {item.item_name}
            </span>
            
            <span className="prod-detail-price">{(currency || "$")} {item.rate.toFixed(2)}</span>
            <span>
              <input
                type="number"
                min="0"
                value={itemQuantities[item.item_code] || 0}
                className="return-qty"
                onChange={(e) =>
                  handleQuantityChange(item.item_code, e.target.value)
                }
                disabled={!selectedItems[item.item_code]}
              />
            </span>
            <span className="prod-detail-price">{(currency || "$")} {item.amount.toFixed(2)}</span>
          </li>
        ))}
      </ul>
      <div className="order-pricing">
        <p>
          <span>Subtotal</span>
          <span>{(currency || "$")} {order.total.toFixed(2)}</span>
        </p>
        <p>
          <span>Tax</span>
          <span>{(currency || "$")} {order.total_taxes_and_charges}</span>
        </p>
        <p>
          <span>Total</span>
          <span>{(currency || "$")} {(order.total).toFixed(2)}</span>
        </p>
      </div>
    </Modal>
  );
};

export default OrderDetailModal;
