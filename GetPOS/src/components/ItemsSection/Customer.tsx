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
      <div className="search-customer-input">
        <input
          type="text"
          className="search-customer-input"
          value={customerMobile}
          onChange={(e) => setCustomerMobile(e.target.value)}
        />
        <button
          style={{
            marginTop: "6px",
            height: "38px",
            width: "7%",
            borderRadius: "10px",
          }}
        >
          <i className="fa fa-search"></i>
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
