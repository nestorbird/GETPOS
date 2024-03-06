import React, { useContext, useEffect, useState } from "react";
import { useFrappeGetCall, useFrappePostCall } from "frappe-react-sdk";
import UserItemsContext from "../../common/cartContext";
import APIs from "../../constants/APIs";

const GetCustomer = () => {
  const cartListItems: any = useContext(UserItemsContext);
  const [customerMobile, setCustomerMobile] = useState("");
  const [newCustomer, setNewCustomer] = useState(false);
  const [newCustomerData, setNewCustomerData] = useState({
    customer_name: "",
    email_id: "",
  });

  const { data, error, isLoading } = useFrappeGetCall(
    "getpos.getpos.api.get_customer",
    { mobile_no: customerMobile }
  );

  const { call, error: post_error } = useFrappePostCall(APIs.createCustomer);

  const handleCustomerSelection = (event) => {
    event.preventDefault();
    if (data?.message?.success_key === 1) {
      cartListItems.setPayloadData({ customer: data?.message?.customer[0] });
    } else {
      setNewCustomer(true);
    }
  };

  const handleCreateCustomer = async (event) => {
    console.log("Handle Create Customer Called");
    event.preventDefault();
    debugger;
    const resp = await call({
      mobile_no: customerMobile,
      customer_name: newCustomerData.customer_name,
      email_id: newCustomerData.email_id,
    });
    if (resp?.message?.success_key === 1) {
      cartListItems.setPayloadData({ customer: resp?.message?.customer });
    }
    console.log(resp, "response123");
  };

  return (
    <div className="column" style={{ alignItems: "center" }}>
      {newCustomer === true ? (
        <>
          <input
            type="text"
            className="new-customer-input"
            value={customerMobile}
            onChange={(e) => setCustomerMobile(e.target.value)}
            placeholder="Enter Mobile No"
          />
          <input
            type="text"
            placeholder="Enter Name"
            className="new-customer-input"
            value={newCustomer.customer_name}
            onChange={(e) =>
              setNewCustomerData({
                ...newCustomerData,
                ...{ customer_name: e.target.value },
              })
            }
          />
          <input
            type="text"
            className="new-customer-input"
            placeholder="Enter Email (Optional)"
            value={newCustomer.email_id}
            onChange={(e) =>
              setNewCustomerData({
                ...newCustomerData,
                ...{ email_id: e.target.value },
              })
            }
          />
          <button
            className="new-customer-submit"
            onClick={handleCreateCustomer}
          >
            Add & Create Order
          </button>
        </>
      ) : (
        <>
          <div className="input-search-box row">
            <input
              className="search-customer-input"
              type="text"
              style={{
                height: "3rem",
                borderRadius: "8px",
                border: "1px #d3d3d3",
                outline: "1px solid black",
              }}
              value={customerMobile}
              onChange={(e) => setCustomerMobile(e.target.value)}
              placeholder="Search Customer"
            ></input>
            <button
              style={{
                width: "3rem",
                height: "54px",
                borderRadius: "8px",
                backgroundColor: "#dc1e44",
                border: "1px #d3d3d3",
              }}
            >
              <span className="material-symbols-outlined">search</span>
            </button>
          </div>

          <div style={{ marginTop: "1rem" }}>
            <div className="card select-customer-section">
              {customerMobile.length > 8 ? (
                data?.message?.success_key === 1 ? (
                  data?.message?.customer?.map((cust) => {
                    return (
                      <div className="card customer-dropdown">
                        <h4 style={{ color: "#dc1e44" }}>
                          {String(cust.customer_name).toUpperCase()}
                        </h4>
                        <h4 style={{ fontWeight: "bolder" }}>
                          {cust.mobile_no}
                        </h4>
                      </div>
                    );
                  })
                ) : (
                  <div className="no-record-customer card">
                    <p className="no-record-text">
                      No records were found, please add the details below in
                      order to continue
                    </p>
                  </div>
                )
              ) : (
                <></>
              )}
            </div>
          </div>
          <div className="" style={{ marginTop: "1rem" }}>
            <button
              className="select-customer"
              onClick={handleCustomerSelection}
            >
              Continue
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default GetCustomer;
