import { useEffect, useState } from "react";
import { Button, Input, Modal, notification } from "antd";
import { createCustomer } from "../modules/LandingPage";

const AddCustomerForm = ({ searchTerm, onAddCustomer }) => {
  const [customerName, setCustomerName] = useState("");
  const [customerNumber, setCustomerNumber] = useState("");
  const [email, setEmail] = useState("");
  const [nameError, setNameError] = useState("");
  const [numberError, setNumberError] = useState("");

  useEffect(() => {
    const isNumeric = /^\d+$/.test(searchTerm);
    if (isNumeric) {
      setCustomerNumber(searchTerm);
      setCustomerName("");
    } else {
      setCustomerNumber("");
      setCustomerName(searchTerm);
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

    if (!customerNumber.trim()) {
      setNumberError("Mobile number is required");
      isValid = false;
    } else if (!/^\d{10}$/.test(customerNumber)) {
      setNumberError("Please enter a valid phone number");
      isValid = false;
    } else {
      setNumberError("");
    }    

    return isValid;
  };

  const handleCustomerNumberChange = (e) => {
    const value = e.target.value;
    if (/^\d*$/.test(value) && value.length <= 10) {
      setCustomerNumber(value);
    }
  };

  // Function to handle adding a new customer
  const handleAddCustomer = async () => {
    if (!validateInputs()) {
      return;
    }

    const newCustomer = {
      mobile_no: customerNumber,
      customer_name: customerName,
      email,
    };

    try {
      const res = await createCustomer(customerName, customerNumber, email);
      if (res.status === 200) {
        Modal.success({
          title: "Success",
          content: "Customer created successfully.",
        });
        onAddCustomer(res.data.message.customer);
        setCustomerName("");
        setCustomerNumber("");
        setEmail("");
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
      <span className="no-data-found">No Data Found - Add New Customer</span>
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
