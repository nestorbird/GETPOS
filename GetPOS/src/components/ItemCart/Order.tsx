import React, { useContext, useState } from "react";
import UserItemsContext from "../../common/cartContext";
import ModalBox from "../../common/popup";

const OrderSuccess = ({ orderData, clearData }) => {
  const cartListItems: any = useContext(UserItemsContext);
  const [visibility, setVisibility] = useState(true);

  const popupCloseHandler = (e) => {
    setVisibility(e);
  };

  const RenderOrderSuccess = () => {
    return (
      <div className="column order-success-content">
        <div>
          <img
            src="/assets/getpos/images/icons8-done.svg"
            style={{ height: "10rem" }}
          />
        </div>
        <div className="custom-btns-success">
          <button className="btn-order-success" onClick={handleReceipt}>
            Print Receipt
          </button>
          <button className="btn-order-success" onClick={handleNewOrder}>
            New Order
          </button>
        </div>
      </div>
    );
  };

  const handleNewOrder = (event) => {
    event.preventDefault();
    cartListItems.setPayloadData({});
    cartListItems.setCartItems([]);
    setVisibility(false);
    clearData(false);
  };

  const handleReceipt = (event) => {
    event.preventDefault();
    console.log(orderData, "Order Data");
    const url =
      "/printview?doctype=Sales%20Order&name=" +
      orderData?.name +
      "&trigger_print=1" +
      "&format=POS%20Print" +
      "&no_letterhead=";
    const printWindow = window.open(url, "Print");
    printWindow.addEventListener(
      "load",
      function () {
        printWindow.print();
        // printWindow.close();
        // NOTE : uncomoent this to auto closing printing window
      },
      true
    );
  };

  return (
    <ModalBox
      onClose={popupCloseHandler}
      visibility={visibility}
      title=""
      htmlRender={() => <RenderOrderSuccess />}
    />
  );
};

export default OrderSuccess;
