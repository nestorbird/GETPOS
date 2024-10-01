import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { fetchCustomers, updateCustomer } from "../modules/LandingPage";
import SearchIcon from "../assets/images/icon-search.png";
import EditIcon from "../assets/images/icon-edit.png";
import { Button, Input, Modal, Spin, notification } from "antd";

const CustomerPage = () => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [newMobile, setNewMobile] = useState("");
  const [newEmailID, setNewEmailID] = useState("");
  const [errors, setErrors] = useState({});

  useEffect(() => {
    const loadCustomers = async () => {
      try {
        const customerData = await fetchCustomers();
        setCustomers(customerData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadCustomers();
  }, []);

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const filteredCustomers = customers.filter(
    (customer) =>
      customer.customer_name
        ?.toLowerCase()
        .includes(searchTerm.toLowerCase()) ||
      customer.mobile_no?.toString()?.includes(searchTerm)
  );

  const handleUpdateCustomerClick = (customer) => {
    setSelectedCustomer(customer);
    setNewName(customer.customer_name);
    setNewMobile(customer.mobile_no);
    setNewEmailID(customer.email_id);
    setIsModalOpen(true);
  };

  const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
  };

  const validateMobile = (mobile) => {
    const re = /^\d{10}$/;
    return re.test(String(mobile));
  };

  const handleUpdateCustomer = async () => {
    let validationErrors = {};

    // Name validation: Ensure the name field is not empty
    if (!newName.trim()) {
      validationErrors.name = "Please enter Name";
    }

    // Email validation
    if (newEmailID && !validateEmail(newEmailID)) {
      validationErrors.email = "Please enter valid email address";
    }

    // Mobile validation
    if (!validateMobile(newMobile)) {
      validationErrors.mobile = "Please enter valid 10-digit mobile number";
    }

    // If there are any validation errors, display the error messages
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      notification.error({
        message: "Validation Error",
        description: "Please fix the validation errors before updating.",
      });
      return;
    }

    try {
      const updatedCustomer = await updateCustomer({
        name: selectedCustomer.name,
        customer_name: newName,
        mobile_no: newMobile,
        email_id: newEmailID,
      });

      setCustomers((prevCustomers) =>
        prevCustomers.map((cust) =>
          cust.name === updatedCustomer.name
            ? { ...updatedCustomer, email_id: newEmailID }
            : cust
        )
      );
      setIsModalOpen(false);
      setErrors({});
    } catch (error) {
      console.error("Error updating customer:", error);
    }
  };

  const handleEmailChange = (e) => {
    setNewEmailID(e.target.value.toLowerCase());
  };

  return (
    <Layout>
      <div className="main-cont customer-page">
        <div className="heading-cont">
          <h1>Customer</h1>
          <div className="searchField">
            <input
              type="text"
              placeholder="Search customer name / number"
              value={searchTerm}
              onChange={handleSearchChange}
              className="customer-search"
            />
            <button>
              <img src={SearchIcon} alt="Search" />
            </button>
          </div>
        </div>
        {loading ? (
          <div className="loading-spin">
            <Spin tip="Loading..."></Spin>
          </div>
        ) : error ? (
          <p>Error loading customers: {error}</p>
        ) : filteredCustomers.length === 0 ? (
          <div className="no-customer-found">No customer found</div>
        ) : (
          <ul className="customer-list">
            {filteredCustomers.map((customer) => (
              <li key={customer.name}>
                <p>
                  <span className="cus-name">{customer.customer_name}</span>
                  <span className="cus-mobile">{customer.mobile_no}</span>
                </p>
                <p>
                  <span className="cus-email">{customer.email_id}</span>
                  <button
                    className="cus-edit"
                    onClick={() => handleUpdateCustomerClick(customer)}
                  >
                    <img src={EditIcon} alt="Edit" />
                  </button>
                </p>
              </li>
            ))}
          </ul>
        )}
      </div>

      <Modal
        title="Edit Customer"
        visible={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={[
          <Button key="submit" type="primary" onClick={handleUpdateCustomer}>
            Update
          </Button>,
        ]}
        className="edit-customer-modal"
      >
        <div className="edit-cus-row">
          <Input
            type="text"
            placeholder="Name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
          />
          {errors.name && <p style={{ color: "red" }}>{errors.name}</p>}
        </div>
        <div className="edit-cus-row">
          <Input
            type="text"
            placeholder="Mobile Number"
            value={newMobile}
            onChange={(e) => setNewMobile(e.target.value)}
          />
          {errors.mobile && <p style={{ color: "red" }}>{errors.mobile}</p>}
        </div>
        <div className="edit-cus-row">
          <Input
            type="email"
            placeholder="Email Address"
            value={newEmailID}
            onChange={handleEmailChange}
          />
          {errors.email && <p style={{ color: "red" }}>{errors.email}</p>}
        </div>
      </Modal>
    </Layout>
  );
};

export default CustomerPage;
