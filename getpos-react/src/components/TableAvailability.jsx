import React, { useState } from "react";
import { Modal, Button } from "antd";

const DynamicTableAvailabilityPopup = ({ visible, onClose, onSubmit }) => {
  const [selectedTables, setSelectedTables] = useState([]);

  // Mock API data for tables
  const tableData = {
    tableCategories: [
      {
        category: "6 Seater Tables",
        tables: [
          { id: "01", available: true },
          { id: "02", available: true },
          { id: "03", available: false },
          { id: "04", available: true },
          { id: "05", available: false },
          { id: "06", available: true },
        ],
      },
      {
        category: "4 Seater Tables",
        tables: [
          { id: "13", available: false },
          { id: "14", available: true },
          { id: "15", available: true },
          { id: "16", available: true },
        ],
      },
    ],
  };

  const handleTableSelect = (id) => {
    setSelectedTables((prevSelected) => {
      if (prevSelected.includes(id)) {
        return prevSelected.filter((table) => table !== id);
      } else {
        return [...prevSelected, id];
      }
    });
  };
  const handleBookClick = () => {
    onSubmit(selectedTables);
  };

  const renderTables = (tables) =>
    tables.map((table) => (
      <div
        key={table.id}
        className={`table-item ${
          table.available ? "available" : "unavailable"
        } ${selectedTables.includes(table.id) ? "selected" : ""}`}
        onClick={() => table.available && handleTableSelect(table.id)}
      >
        {table.id}
      </div>
    ));

  return (
    <Modal visible={visible} onCancel={onClose} footer={null} centered>
      <h2>TABLE AVAILABILITY</h2>
      <div className="table-container">
        {tableData.tableCategories.map((category) => (
          <div key={category.category} className="table-category">
            <h3>{category.category}</h3>
            <div className="table-grid">{renderTables(category.tables)}</div>
          </div>
        ))}
      </div>
      <div className="table-availability-popup-footer">
        <Button className="table-availability-back" onClick={onClose}>
          Back
        </Button>
        <Button
          className="table-availability-book"
          onClick={handleBookClick}
          type="primary"
        >
          Book
        </Button>
      </div>
    </Modal>
  );
};

export default DynamicTableAvailabilityPopup;
