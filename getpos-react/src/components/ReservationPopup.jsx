import React, { useState } from "react";
import { Modal, Button, Input, message } from "antd";
import moment from "moment";

const ReservationPopup = ({ visible, onClose, onSubmit }) => {
  const [selectedDate, setSelectedDate] = useState(moment());
  const [selectedTime, setSelectedTime] = useState(null);
  const [numGuests, setNumGuests] = useState("");
  const [specialRequest, setSpecialRequest] = useState("");

  const timeOptions = Array.from(
    { length: 24 },
    (_, i) => `${i.toString().padStart(2, "0")}:00`
  );

  const handleMonthChange = (direction) => {
    const newDate =
      direction === "prev"
        ? selectedDate.clone().subtract(1, "months")
        : selectedDate.clone().add(1, "months");
    setSelectedDate(newDate);
  };

  const handleSubmit = () => {
    if (!selectedDate || !selectedTime || !numGuests) {
      message.error("Please fill in the date, time, and number of guests.");
      return;
    }
    console.log({
      selectedDate: selectedDate.format("YYYY-MM-DD"),
      selectedTime,
      numGuests,
      specialRequest,
    });
    onSubmit(selectedDate, selectedTime, numGuests, specialRequest);
  };

  const renderDaysOfMonth = () => {
    const startOfMonth = selectedDate.clone().startOf("month");
    const endOfMonth = selectedDate.clone().endOf("month");

    // Start the calendar from the Monday of the first week that includes the 1st
    const startOfCalendar = startOfMonth.clone().startOf("isoWeek"); // Monday start
    const endOfCalendar = endOfMonth.clone().endOf("isoWeek"); // Ends on Sunday

    const days = [];
    for (
      let day = startOfCalendar;
      day.isBefore(endOfCalendar) || day.isSame(endOfCalendar);
      day.add(1, "days")
    ) {
      days.push(day.clone());
    }
    return days;
  };

  const weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]; // Weekdays starting from Monday

  return (
    <Modal
      visible={visible}
      footer={null}
      onCancel={onClose}
      className="reservation-popup"
      centered
    >
      <h2 className="reservation-popup-title">Reservation</h2>
      <div className="reservation-popup-content">
        <div className="reservation-date-time-container">
          {/* Custom Calendar */}
          <div className="calendar-container">
            <div className="calendar-header">
              <Button onClick={() => handleMonthChange("prev")}>&lt;</Button>
              <h3>{selectedDate.format("MMMM YYYY")}</h3>
              <Button onClick={() => handleMonthChange("next")}>&gt;</Button>
            </div>
            <hr />
            {/* Weekday labels */}
            <div className="calendar-weekdays">
              {weekdays.map((weekday) => (
                <div key={weekday} className="calendar-weekday">
                  {weekday}
                </div>
              ))}
            </div>
            {/* Dates grid */}
            <div className="calendar-grid">
              {renderDaysOfMonth().map((day) => (
                <div
                  key={day.format("DD-MM-YYYY")}
                  className={`calendar-day ${
                    day.isSame(selectedDate, "day") ? "selected-day" : ""
                  } ${
                    day.isSame(selectedDate, "month") ? "" : "outside-month"
                  }`} // Different styling for dates outside current month
                  onClick={() => setSelectedDate(day)}
                >
                  {day.format("D")}
                </div>
              ))}
            </div>
          </div>

          {/* Scrollable Time Selection */}
          <div className="time-container">
            <h3>Time</h3>
            <hr />
            <div className="time-list-container">
              {timeOptions.map((time) => (
                <div
                  key={time}
                  onClick={() => setSelectedTime(time)}
                  className={`time-item ${
                    time === selectedTime ? "selected-time" : ""
                  }`}
                >
                  {time}
                </div>
              ))}
            </div>
          </div>
        </div>

        <Input
          placeholder="No Of Guests"
          value={numGuests}
          onChange={(e) => setNumGuests(e.target.value)}
          className="guests-input"
        />
        <Input
          placeholder="Special Request (Optional)"
          value={specialRequest}
          onChange={(e) => setSpecialRequest(e.target.value)}
          className="special-request-input"
        />

        <div className="reservation-popup-footer">
          <Button className="reservation-back-btn" onClick={onClose}>
            Back
          </Button>
          <Button
            className="reservation-continue-btn"
            type="primary"
            onClick={handleSubmit}
          >
            Continue
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default ReservationPopup;
