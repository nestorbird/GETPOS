import { useEffect, useState } from "react";
import { Button, Input, Modal, notification } from "antd";
import { createCustomer } from "../modules/LandingPage";

const AddCustomerForm = ({ searchTerm, onAddCustomer, handleCloseForm, loadCustomers }) => {
  const [customerName, setCustomerName] = useState("");
  const [customerNumber, setCustomerNumber] = useState("");
  const [email, setEmail] = useState("");
  const [nameError, setNameError] = useState("");
  const [numberError, setNumberError] = useState("");

  useEffect(() => {
    const trimmedSearchTerm = searchTerm.replace(/\s+/g, "").trim(); // Remove all spaces before checking
    const isNumeric = /^\d+$/.test(trimmedSearchTerm); // Check if the term is numeric
     console.log("trimmedSearchTerm",trimmedSearchTerm)
    if (isNumeric) {
      setCustomerNumber(trimmedSearchTerm); // Set the number after removing spaces
      setCustomerName("");
    } else {
      setCustomerNumber("");
      setCustomerName(searchTerm.trim()); // Set the name if it's not numeric
    }
  }, [searchTerm]);

  const validateInputs = () => {
    let isValid = true;

    if (!customerName.trim()) {
      setNameError("Customer name is required.");
      isValid = false;
    } else {
      setNameError("");
    }

    const trimmedNumber = customerNumber.replace(/\s+/g, ""); // Remove spaces before validation
    if (!trimmedNumber) {
      setNumberError("Mobile number is required.");
      isValid = false;
    } else if (!/^\d{10}$/.test(trimmedNumber)) {
      setNumberError("Please enter a valid 10-digit phone number.");
      isValid = false;
    } else {
      setNumberError("");
    }

    return isValid;
  };

  const handleCustomerNumberChange = (e) => {
    const value = e.target.value; // Allow spaces during input
    setCustomerNumber(value);
  };

  const handleAddCustomer = async () => {
    if (!validateInputs()) {
      return;
    }

    const newCustomer = {
      mobile_no: customerNumber.replace(/\s+/g, ""), // Save number without spaces
      customer_name: customerName,
      email,
    };

    try {
      const res = await createCustomer(customerName, customerNumber.replace(/\s+/g, ""), email); // Send number without spaces
      if (res.status === 200) {
        Modal.success({
          title: "Success",
          content: "Customer created successfully.",
        });
        onAddCustomer(res.data.message.customer);
        setCustomerName("");
        setCustomerNumber("");
        setEmail("");
        loadCustomers();
        handleCloseForm();
      } else {
        notification.error({
          message: "Error",
          description: `Unexpected status code: ${res.status}`,
        });
      }
    } catch (error) {
      notification.error({
        message: "Error",
        description: `Error creating customer: ${error.message}`,
      });
    }
  };

  return (
    <div className="autoCompleteForm">
      <div className="form-header">
        <span className="no-data-found">No Data Found - Add New Customer</span>
        <button className="close-button" onClick={handleCloseForm}>X</button>
      </div>
      <Input
        placeholder="Mobile Number*"
        value={customerNumber}
        onChange={handleCustomerNumberChange}
        required
      />
      {numberError && <span className="error-message">{numberError}</span>}
      <Input
        placeholder="Enter Customer Name *"
        value={customerName}
        onChange={(e) => setCustomerName(e.target.value)}
        required
      />
      {nameError && <span className="error-message">{nameError}</span>}
      <Input
        placeholder="Enter Email (Optional)"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <Button type="primary" onClick={handleAddCustomer}>
        Add & Proceed
      </Button>
    </div>
  );
};

export default AddCustomerForm;
