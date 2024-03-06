import React, { useContext, useEffect, useState } from "react";
import "./index.css";
import APIs from "../../constants/APIs";
import { useFrappeGetCall, useFrappePostCall } from "frappe-react-sdk";
import UserItemsContext from "../../common/cartContext";
import OrderSuccess from "./Order";

const ItemCart = (props) => {
  const [orderTaxes, setOrderTaxes] = useState([]);
  const [orderData, setOrderData] = useState({ success: false });

  const cartListItems: any = useContext(UserItemsContext);

  const { data, error, isLoading } = useFrappeGetCall(APIs.getSalesTaxes);

  let itemTotal = 0;
  let taxes: Array<Object> = [];

  const finalCartItems = cartListItems.cartItems;
  finalCartItems.map((item) => {
    itemTotal += item.qty * item.product_price;
    if (item.tax.length > 0) {
      item?.tax?.map((tax) => {
        tax.tax_amount = (item.qty * item.product_price * tax.tax_rate) / 100;

        if (
          taxes.filter((tax_temp) => tax_temp.tax_type === tax.tax_type)
            .length > 0
        ) {
          taxes.map((tax_temp) => {
            if (tax_temp.tax_type === tax.tax_type) {
              tax_temp.tax_amount = tax_temp.tax_amount + tax.tax_amount;
            }
          });
        } else {
          taxes.push(tax);
        }
      });
    }
  });

  const totalTax = (taxes) => {
    if (taxes?.length > 0) {
      const finalTaxes = taxes.map((tax_temp) =>
        parseFloat(tax_temp.tax_amount)
      );
      return finalTaxes?.reduce(
        (accumulator, currentValue) => accumulator + currentValue,
        0
      );
    } else {
      const finalTaxes = orderTaxes.map((tax_temp) => {
        tax_temp.tax_amount = (itemTotal * tax_temp.tax_rate) / 100;
        return parseFloat((itemTotal * tax_temp.tax_rate) / 100);
      });
      return finalTaxes?.reduce(
        (accumulator, currentValue) => accumulator + currentValue,
        0
      );
    }
  };

  cartListItems.setCartItems(finalCartItems);

  const RenderTaxItem = ({ taxes }) => {
    return (
      <>
        {taxes.length > 0
          ? taxes?.map((tax) => {
              return (
                <div
                  className="row"
                  style={{ justifyContent: "space-between" }}
                >
                  <h4>{tax.tax_type}</h4>
                  <h4>₹ {tax.tax_amount}</h4>
                </div>
              );
            })
          : orderTaxes.map((tax) => {
              return (
                <div
                  className="row"
                  style={{ justifyContent: "space-between" }}
                >
                  <h4>{tax.tax_type}</h4>
                  <h4>₹ {tax.tax_amount}</h4>
                </div>
              );
            })}
      </>
    );
  };

  useEffect(() => {
    data?.message?.map((tax) => {
      if (tax.is_default === 1) setOrderTaxes(tax?.tax);
    });
  }, [data]);

  const [taxAccordion, setTaxAccordion] = useState("false");

  const handleCartItem = (event, item, qty) => {
    event.preventDefault();
    const items = cartListItems.cartItems;
    let finalCartItems = [];
    items.map((pro) => {
      if (pro.id === item.id) {
        pro.qty = pro.qty + qty;
      }

      if (pro.qty > 0) {
        finalCartItems.push(pro);
      }
    });

    cartListItems.setCartItems(finalCartItems);
  };

  const handlePayment = (e, paymentMethod) => {
    e.preventDefault();
    cartListItems.setPayloadData({
      ...cartListItems.payloadData,
      ...{ mode_of_payment: paymentMethod },
    });
  };

  const { call, error: post_error } = useFrappePostCall(APIs.createOrder);

  const placeOrder = (event) => {
    event.preventDefault();

    call({
      order_list: {
        hub_manager: "akshay@yopmail.com",
        customer: cartListItems.payloadData.customer.name,
        transaction_date:
          new Date().toLocaleDateString("en-CA") +
          " " +
          new Date().toLocaleTimeString(),
        delivery_date: new Date().toLocaleDateString("en-CA"),
        items: cartListItems?.cartItems?.map((item) => {
          return {
            item_code: item.id,
            item_name: item.name,
            rate: item.product_price,
            qty: item.qty,
            ordered_price: item.qty * item.product_price,
            tax: item.tax,
          };
        }),
        mode_of_payment: cartListItems?.payloadData?.mode_of_payment,
        mpesa_No: "",
        tax: taxes.length > 0 ? null : orderTaxes,
      },
    }).then((result) => {
      if (result?.message?.success_key === 1) {
        console.log(result?.message?.sales_order?.name);
        setOrderData({
          success: true,
          sales_order: result?.message?.sales_order,
        });
        alert("order successful");
      }
    });
  };

  return (
    <>
      {orderData?.success === true && <OrderSuccess orderData={orderData} />}
      <div className="column" style={{ position: "fixed" }}>
        {cartListItems?.payloadData?.customer && (
          <div className="row">
            <div className="card customer-cart-section">
              <h4 style={{ color: "#dc1e44", fontSize: "19px" }}>
                {cartListItems?.payloadData?.customer?.customer_name}
              </h4>
            </div>
          </div>
        )}
        <div className="row cart-section">
          <h3 style={{ margin: "1rem" }}>Cart</h3>
          <h3 style={{ margin: "1rem", color: "green" }}>
            {cartListItems.cartItems?.length
              ? cartListItems.cartItems?.length
              : 0}
            &nbsp;Items
          </h3>
        </div>
        <div className="cart-items">
          {cartListItems.cartItems?.map((item) => {
            return (
              <div
                className="row"
                style={{
                  justifyContent: "space-between",
                  margin: "10px 20px 0 20px",
                }}
              >
                <p style={{ fontSize: "18px" }}>
                  {item.name.length > 11 ? item.name.substr(0, 11) : item.name}
                </p>
                <div className="row qty-item-cart-section">
                  <button
                    className="qty-cart-btn"
                    onClick={(e) => handleCartItem(e, item, 1)}
                  >
                    +
                  </button>
                  <p className="qty-cart-item">{item.qty ? item.qty : 1}</p>
                  <button
                    className="qty-cart-btn"
                    onClick={(e) => handleCartItem(e, item, -1)}
                  >
                    -
                  </button>
                </div>
                <p style={{ fontSize: "18px" }}>
                  ₹ {item.qty * item.product_price}
                </p>
              </div>
            );
          })}
        </div>

        <div className="column">
          <div
            className="row"
            style={{ justifyContent: "space-between", margin: "0 1rem 0 1rem" }}
          >
            <h3>Bill</h3>
          </div>
          <div
            className="row"
            style={{ justifyContent: "space-between", margin: "0 1rem 0 1rem" }}
          >
            <h3>Item Total</h3>
            <h3>₹ {itemTotal}</h3>
          </div>
          <div
            className="row"
            style={{
              justifyContent: "space-between",
              margin: "0 1rem 0 1rem",
              borderBottom: "1px solid black",
            }}
          >
            <h3>Sub Total</h3>
            <h3>₹ {itemTotal}</h3>
          </div>
          <div
            className="column"
            style={{
              justifyContent: "space-between",
              margin: "0 1rem 0 1rem",
            }}
          >
            <button
              className={
                taxAccordion === true
                  ? "row cart-tax-accordion cart-tax-accordion-active"
                  : "row cart-tax-accordion"
              }
              style={{
                justifyContent: "space-between",
                alignItems: "center",
              }}
              onClick={(e) =>
                setTaxAccordion(taxAccordion === true ? false : true)
              }
            >
              <div className="row" style={{ alignItems: "center" }}>
                <h3>Total Tax</h3>
                <span className="material-symbols-outlined">expand_more</span>
              </div>

              <h3>₹{totalTax(taxes)}</h3>
            </button>
            <div
              className="cart-tax-panel"
              style={{ display: taxAccordion === true ? "block" : "none" }}
            >
              {<RenderTaxItem taxes={taxes} />}
            </div>
            <div className="row" style={{ justifyContent: "space-between" }}>
              <h3>Grand Total</h3>
              <h3>₹{itemTotal + totalTax(taxes)}</h3>
            </div>

            <div
              className="row"
              style={{
                justifyContent: "space-between",
              }}
            >
              <a href="" onClick={(e) => handlePayment(e, "Card")}>
                <div
                  className={
                    cartListItems?.payloadData?.mode_of_payment &&
                    cartListItems?.payloadData?.mode_of_payment === "Card"
                      ? "payment-card row payment-card-active"
                      : "payment-card row"
                  }
                >
                  <img
                    src="/assets/getpos/images/Group 282.svg"
                    style={{ width: "4rem", height: "3rem" }}
                  />
                  <p style={{ marginLeft: "1rem", fontWeight: "bold" }}>Card</p>
                </div>
              </a>

              <a href="" onClick={(e) => handlePayment(e, "Cash")}>
                <div
                  className={
                    cartListItems?.payloadData?.mode_of_payment &&
                    cartListItems?.payloadData?.mode_of_payment === "Cash"
                      ? "payment-card row payment-card-active"
                      : "payment-card row"
                  }
                >
                  <img
                    src="/assets/getpos/images/Group%20283.svg"
                    style={{ width: "4rem", height: "3rem" }}
                  />
                  <p style={{ marginLeft: "1rem", fontWeight: "bold" }}>Cash</p>
                </div>
              </a>
            </div>

            <div className="row" style={{ marginTop: "2rem" }}>
              <button className="place-order-btn" onClick={placeOrder}>
                Place Order
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ItemCart;
