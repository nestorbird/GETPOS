import React from "react";
import { Modal, Button } from "antd";

const BookingSummaryPopup = ({ visible, onClose, bookingData }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  return (
    <Modal visible={visible} onCancel={onClose} footer={null} centered>
      <h2 className="booking-summary-title">BOOKING SUMMARY</h2>
      {console.log(bookingData)}
      <div className="booking-summary-container">
        <div className="booking-summary-column">
          <div className="booking-summary-label">Booking Date</div>
          <div className="booking-summary-label">Booking Time</div>
          <div className="booking-summary-label">No. of Guests</div>
          <div className="booking-summary-label">Table Number</div>
          <div className="booking-summary-label">Special Request</div>
          <div className="booking-summary-label">Customer Name</div>
          <div className="booking-summary-label">Contact</div>
        </div>
        <div className="booking-summary-column">
          <div className="booking-summary-colon">:</div>
          <div className="booking-summary-colon">:</div>
          <div className="booking-summary-colon">:</div>
          <div className="booking-summary-colon">:</div>
          <div className="booking-summary-colon">:</div>
          <div className="booking-summary-colon">:</div>
          <div className="booking-summary-colon">:</div>
        </div>
        <div className="booking-summary-column">
          <div className="booking-summary-value">
            {formatDate(bookingData?.selectedDate)}
          </div>
          <div className="booking-summary-value">
            {bookingData?.selectedTime}
          </div>
          <div className="booking-summary-value">{bookingData?.numGuests}</div>
          <div className="booking-summary-value">
            {bookingData?.tableNumbers.join(", ")}
          </div>
          <div className="booking-summary-value">
            {bookingData?.specialRequest || "N/A"}
          </div>
          <div className="booking-summary-value">
            {bookingData?.customerName || "N/A"}
          </div>
          <div className="booking-summary-value">
            {bookingData?.contact || "N/A"}
          </div>
        </div>
      </div>
      <div className="booking-summary-footer">
        <Button className="booking-summary-close" onClick={onClose}>
          Close
        </Button>
      </div>
    </Modal>
  );
};

export default BookingSummaryPopup;
