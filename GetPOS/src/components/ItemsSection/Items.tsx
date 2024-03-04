import React, { useContext, useState } from "react";
import ModalBox from "../../common/popup";
import UserItemsContext from "../../common/cartContext";
import GetCustomer from "./Customer";

const AllItems = (props) => {
  const { items } = props;
  const cartListItems = useContext(UserItemsContext);
  const [visibility, setVisibility] = useState(false);
  const [selectedItem, setSelectedItem] = useState({});

  // const [cartItems, setCartItems] = useState(cartListItems);

  const handleItem = (event, item) => {
    event.preventDefault();
    if (item.stock_qty > 0) {
      setVisibility(true);
      setSelectedItem({ ...item });
    }
  };

  const PopupItemHtml = ({ item }) => {
    return (
      <div className="column">
        <div className="row" style={{ justifyContent: "space-between" }}>
          <div className="row">
            <img
              src={
                item.image ? item.image : "/assets/getpos/images/Group 796.png"
              }
              style={{ height: "4rem", maxWidth: "4rem" }}
            />
            <div className="column" style={{ alignItems: "baseline" }}>
              <h4
                style={{
                  marginLeft: "1rem",
                  marginTop: "auto",
                  marginBottom: "10px",
                }}
              >
                {item.name}
              </h4>
              <p className="item-price">
                ₹ {item.product_price ? item.product_price : 0}
              </p>
              <p className="item-stock">
                Stock - {item.stock_qty ? item.stock_qty : 0}
              </p>
            </div>
          </div>
          <div>
            <div className="row qty-cart-section">
              <button className="qty-btn" onClick={(e) => handleCartItem(e, 1)}>
                +
              </button>
              <p className="qty-cart">{item.qty ? item.qty : 1}</p>
              <button
                className="qty-btn"
                onClick={(e) => handleCartItem(e, -1)}
              >
                -
              </button>
            </div>
          </div>
        </div>
        <div className="add-to-cart">
          <button className="add-cart-total" onClick={addToCart}>
            <div
              className="row"
              style={{
                justifyContent: "space-between",
              }}
            >
              <div className="column" style={{ marginTop: "-5px" }}>
                <p>Item Total</p>
                <p
                  style={{
                    marginTop: "-5px",
                    fontWeight: "bold",
                    fontSize: "18px",
                    alignSelf: "flex-start",
                  }}
                >
                  ₹
                  {(item.product_price ? item.product_price : 0) *
                    (item.qty ? item.qty : 1)}
                </p>
              </div>

              <p
                style={{
                  alignSelf: "center",
                  fontWeight: "bold",
                  fontSize: "20px",
                  marginTop: "-1px",
                }}
              >
                Add Item
              </p>
            </div>
          </button>
        </div>
      </div>
    );
  };

  const PopupCustomerHtml = (event) => {
    return (
      <>
        <GetCustomer />
      </>
    );
  };

  const handleCartItem = (event, qty) => {
    event.preventDefault();
    setSelectedItem({
      ...selectedItem,
      ...{ qty: (selectedItem?.qty ? selectedItem?.qty : 0) + qty },
    });
  };

  const addToCart = (event) => {
    event.preventDefault();

    let finalItems = cartListItems.cartItems;

    let itemExists = 0;

    finalItems?.map((item) => {
      if (item.id === selectedItem.id) {
        itemExists = 1;
        item.qty = selectedItem.qty;
      }
    });

    if (!itemExists) {
      if (!selectedItem.qty) selectedItem.qty = 1;
      if (!selectedItem.product_price) {
        selectedItem.product_price = 0;
      }

      finalItems.push(selectedItem);
    }

    cartListItems.setCartItems([...finalItems]);
  };

  const popupCloseHandler = (e) => {
    setVisibility(e);
  };

  return (
    <>
      <ModalBox
        onClose={popupCloseHandler}
        visibility={visibility}
        title={
          cartListItems?.payloadData?.customer ? "Add Cart" : "Select Customer"
        }
        htmlRender={() =>
          cartListItems?.payloadData?.customer ? (
            <PopupItemHtml item={selectedItem} />
          ) : (
            <PopupCustomerHtml />
          )
        }
      />
      {items?.map((row) => {
        return (
          <div className="column">
            <h3>{row.item_group}</h3>
            <div className="row" style={{ overflowX: "auto" }}>
              {row?.items?.map((item) => {
                return (
                  <a href="" onClick={(e) => handleItem(e, item)}>
                    <div className="item-card">
                      <img
                        src={
                          item.image
                            ? item.image
                            : "/assets/getpos/images/Group 796.png"
                        }
                        alt="Order"
                        style={{
                          width: "4rem",
                          borderRadius: "50%",
                          maxHeight: "2.5rem",
                        }}
                      />

                      <div className="content" style={{}}>
                        <h4 style={{ fontSize: "14px" }}>{item.name}</h4>
                      </div>
                    </div>
                  </a>
                );
              })}
            </div>
          </div>
        );
      })}
    </>
  );
};

export default AllItems;
