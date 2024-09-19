import React, { useState, useContext, useEffect } from "react";
import NoImage from "../assets/images/no-img.png";
import Close from "../assets/images/cross.png";
import { CartContext } from "../common/CartContext";
import { Modal } from "antd";
import { useThemeSettings } from "./ThemeSettingContext";

// import { getImageUrl } from "../utils/imageUtils";

const ProductPopup = ({ product, onClose, selectedCustomer }) => {
  const [quantity, setQuantity] = useState(1);
  const { addItemToCart } = useContext(CartContext);
  const themeSettings = useThemeSettings();

  useEffect(() => {
    if (!selectedCustomer) {
      const storedCustomer = localStorage.getItem("selectedCustomer");
      if (storedCustomer) {
        selectedCustomer = JSON.parse(storedCustomer);
      }
    }
  }, [selectedCustomer]);

  const handleAddItem = () => {
    const selectedCustomer = getSelectedCustomer();

    if (!selectedCustomer) {
      Modal.error({
        title: "Attention!",
        content: "Please select a customer before adding items to the cart.",
      });
      return;
    }

    const updatedProduct = { ...product, quantity };
    addItemToCart(updatedProduct);
    console.log(updatedProduct, "Product manually");
    onClose();
  };

  const getSelectedCustomer = () => {
    const customer = localStorage.getItem("selectedCustomer");
    return customer ? JSON.parse(customer) : null;
  };

  const handleQuantityChange = (e) => {
    setQuantity(parseInt(e.target.value, 10));
  };

  const stockQtyMap = product?.stock.reduce((map, stockItem) => {
    map[stockItem.product_id] = stockItem.stock_qty;
    return map;
  }, {});

  const stockQty = stockQtyMap[product.product_id];

  const incrementQuantity = () => {
    if (quantity < stockQty) {
      setQuantity(quantity + 1);
    } else {
      Modal.warning({
        title: "Stock Limit Reached",
        content: `You cannot add more than ${stockQty} items to the cart.`,
      });
    }
  };

  const decrementQuantity = () => {
    if (quantity > 1) {
      setQuantity(quantity - 1);
    }
  };

  return (
    <>
      <div className="overlay"></div>
      <div className="product-popup">
        <div className="popup-head">
          <button className="popup-close" onClick={onClose}>
            <img src={Close} alt="close" />
          </button>
        </div>
        <div className="popup-body">
          <div className="heading-img">
            <span>
              <img src={product.image || NoImage} alt={product.name} />
            </span>
            <h2>{product.name}</h2>
          </div>
          <div className="popup-qty">
            <label>
              <div className="quantity-control">
                <button onClick={decrementQuantity}>-</button>
                <input
                  type="text"
                  value={quantity}
                  onChange={handleQuantityChange}
                  min="1"
                  disabled
                />
                <button onClick={incrementQuantity}>+</button>
              </div>
            </label>
          </div>
          <div className="popup-footer">
            <div className="btn-total">
              Item Total <br />
              <span>
                {themeSettings.currency_symbol || "$"}
                {(product.product_price * quantity).toFixed(2)}
              </span>
            </div>
            <button onClick={handleAddItem}>Add to Cart</button>
          </div>
        </div>
      </div>
    </>
  );
};

export default ProductPopup;
