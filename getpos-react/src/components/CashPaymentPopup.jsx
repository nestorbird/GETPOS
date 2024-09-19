import React, { useEffect, useState } from "react";
import { Input, Button, Modal } from "antd";
import CloseCalc from "../../src/assets/images/calc-close.png";

const CashPaymentPopup = ({ total, isVisible, onClose, handlePlaceOrder }) => {
  const [cashReceived, setCashReceived] = useState("");

  useEffect(() => {
    if (!isVisible) {
      setCashReceived("");
    }
  }, [isVisible]);

  const handleCashReceivedChange = (event) => {
    setCashReceived(event.target.value);
  };

  const handleKeypadClick = (value) => {
    setCashReceived((prev) => prev + value);
  };

  const handlePopupOK = () => {
    const received = cashReceived || total.toFixed(2); // Use total if cashReceived is empty
    const balance = received - total.toFixed(2);
    localStorage.setItem(
      "cashTransaction",
      JSON.stringify({
        total: total.toFixed(2),
        cashReceived: parseFloat(received).toFixed(2),
        balance: balance.toFixed(2),
      })
    );
    // Modal.success({
    //   title: "Transaction Recorded",
    //   content: (
    //     <>
    //       <p>
    //         <strong>Total:</strong>
    //         <span>$ {total.toFixed(2)}</span>
    //       </p>
    //       <p>
    //         <strong>Cash Received:</strong>
    //         <span>$ {parseFloat(received).toFixed(2)}</span>
    //       </p>
    //       <p>
    //         <strong>Balance:</strong>
    //         <span>$ {balance.toFixed(2)}</span>
    //       </p>
    //     </>
    //   ),
    // });
    handlePlaceOrder();
    onClose();
  };

  const handleKeypadClear = () => {
    setCashReceived("");
  };

  return (
    isVisible && (
      <div className="overlay">
        <div className="cash-popup-box">
          <div className="popup-content">
            <div className="popup-buttons">
              <Button onClick={onClose} className="close-calc">
                <img src={CloseCalc} alt="" />
              </Button>
            </div>
            <div className="popup-main">
              <div className="popup-left-cont">
                <div className="popup-row">
                  <label>Grand Total</label>
                  <Input value={total.toFixed(2)} readOnly />
                </div>
                <div className="popup-row">
                  <label>Cash Received</label>
                  <Input
                    type="text"
                    value={cashReceived}
                    onChange={handleCashReceivedChange}
                  />
                </div>
                <div className="popup-row">
                  <label>Balance</label>
                  <Input
                    value={(cashReceived ? cashReceived - total : 0).toFixed(2)}
                    readOnly
                  />
                </div>
              </div>
              <div className="keypad">
                {["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"].map(
                  (num) => (
                    <Button key={num} onClick={() => handleKeypadClick(num)}>
                      {num}
                    </Button>
                  )
                )}
                <Button onClick={handleKeypadClear} className="clearbtn">
                  Clear
                </Button>
                <Button onClick={handlePopupOK} className="ok-btn">
                  Ok
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  );
};

export default CashPaymentPopup;