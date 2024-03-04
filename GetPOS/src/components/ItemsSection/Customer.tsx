import React, { useContext, useEffect, useState } from "react";
import { useFrappeGetCall } from "frappe-react-sdk";
import UserItemsContext from "../../common/cartContext";

const GetCustomer = () => {
  const cartListItems: any = useContext(UserItemsContext);
  const [customerMobile, setCustomerMobile] = useState("");

  const { data, error, isLoading } = useFrappeGetCall(
    "getpos.getpos.api.get_customer",
    { mobile_no: customerMobile }
  );

  const handleCustomerSelection = (event) => {
    event.preventDefault();
    if (data?.message?.success_key === 1) {
      cartListItems.setPayloadData({ customer: data?.message?.customer[0] });
    }
  };

  return (
    <div className="column" style={{ alignItems: "center" }}>
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
          {customerMobile.length > 6 &&
            data?.message?.success_key === 1 &&
            data?.message?.customer?.map((cust) => {
              return (
                <div className="card customer-dropdown">
                  <h4 style={{ color: "#dc1e44" }}>
                    {String(cust.customer_name).toUpperCase()}
                  </h4>
                  <h4 style={{ fontWeight: "bolder" }}>{cust.mobile_no}</h4>
                </div>
              );
            })}
        </div>
      </div>
      <div className="" style={{ marginTop: "1rem" }}>
        <button className="select-customer" onClick={handleCustomerSelection}>
          Continue
        </button>
      </div>
    </div>
  );
};

export default GetCustomer;
