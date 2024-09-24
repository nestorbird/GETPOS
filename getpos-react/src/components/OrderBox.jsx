import React, { useRef } from "react";
import { Card, notification } from "antd";
import PropTypes from "prop-types";
import IconDelete from "../assets/images/Delete.png";
import IconRightArrow from "../assets/images/icon-rightArrow.png";
import IconEmailButton from "../assets/images/email.png";
import IconPrintButton from "../assets/images/print.png";
import { sendMailToUser } from "../modules/LandingPage";
import PrintFormateOfOrder from "./PrintFormateOfOrder";
import { useThemeSettings } from "./ThemeSettingContext";

const OrderBox = ({
  order,
  showPayNow,
  showDelete,
  showMoveToCart,
  onClick,
  onDelete,
  indicator,
}) => {
  const getReturnStatusText = (status) => {
    if (status === "Fully") {
      return "Returned";
    } else if (status === "Partially") {
      return "Partially Returned";
    } else {
      return "";
    }
  };
  const themeSettings = useThemeSettings();
  const returnStatusText = getReturnStatusText(order.return_order_status);
  const boxClassName = `col-md-3 order-box ${
    order.return_order_status === "Fully" ? "returned" : ""
  } ${order.return_order_status === "Partially" ? "returned" : ""}`;

  const handleClickOrder = () => {
    onClick(order);
  };
  const handleDeleteOrder = (e) => {
    e.stopPropagation();
    onDelete(order.name);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    return `${day}-${month}-${year} ${hours}:${minutes}`;
  };

  const formattedDate = formatDate(order.creation);

  const emailClickHandler = async (e) => {
    e.stopPropagation();
    try {
      const apiResponse = await sendMailToUser(order.name);
      if (apiResponse && apiResponse.success_key === 1) {
        notification.success({
          message: "Email Sent Successfully",
          description: `An email has been sent to the user associated with order ${order.name}.`,
        });
      } else {
        notification.error({
          message: "Email Sending Failed",
          description: `Failed to send email: ${apiResponse.message}`,
        });
      }
    } catch (error) {
      notification.error({
        message: "Server Error",
        description: `An unexpected error occurred while sending the email: ${error.message}`,
      });
    }
  };

  const printRef = useRef();

  const handleButtonClick = (e) => {
    e.stopPropagation();
    if (printRef.current) {
      printRef.current.handlePrint();
    }
  };
  // console.log(order,"Check")

  return (
    <Card className={boxClassName} onClick={handleClickOrder}>
      <p>
        <span>ID: {order.name}</span>
        {returnStatusText && (
          <p className="return-status">{returnStatusText}</p>
        )}
      </p>

      <span className="amountAndDate">
        <span className="light-text">
          {themeSettings?.currency_symbol || "$"}{" "}
          {order.grand_total
            ? (order.grand_total - order.loyalty_amount).toFixed(2)
            : "0.00"}{" "}
          <span className="order-date">| {formattedDate}</span>
        </span>
      </span>
      <p className="status-row">
        <span>
          {order.contact_mobile}{" "}
          <span className="light-text">| {order.contact_name}</span>
        </span>
        <span>
          {showDelete && (
            <img src={IconDelete} alt="Delete" onClick={handleDeleteOrder} />
          )}
          {showMoveToCart && <img src={IconRightArrow} alt="Move to Cart" />}
          {showPayNow && <a href="#"> Pay Now</a>}
        </span>
      </p>
      {indicator && (
        <div className="button-container">
          <button className="icon-button" onClick={handleButtonClick}>
            <img src={IconPrintButton} alt="Print Button" />
          </button>
          <PrintFormateOfOrder ref={printRef} doc={order} />
          <button className="icon-button" onClick={emailClickHandler}>
            <img src={IconEmailButton} alt="Email Button" />
          </button>
        </div>
      )}
    </Card>
  );
};

OrderBox.propTypes = {
  order: PropTypes.shape({
    name: PropTypes.string.isRequired,
    total: PropTypes.number.isRequired,
    creation: PropTypes.string.isRequired,
    contact_mobile: PropTypes.string.isRequired,
    contact_name: PropTypes.string.isRequired,
    return_order_status: PropTypes.string,
  }).isRequired,
  showPayNow: PropTypes.bool,
  showDelete: PropTypes.bool,
  showMoveToCart: PropTypes.bool,
  onClick: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
};

export default OrderBox;
