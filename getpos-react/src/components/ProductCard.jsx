import React, { useState } from "react";
import NoImage from "../assets/images/no-img.png";
import useScanDetection from "use-scan-detection";
import { getItemByScan } from "../modules/LandingPage";
import { Modal } from "antd";
import { useThemeSettings } from "./ThemeSettingContext";

const ProductCard = ({ product, onAddToCart }) => {
  const formatPrice = (price) => {
    return price ? price.toFixed(2) : "NA";
  };

  const [scannedValue, setScannedValue] = useState("");
  const themeSettings = useThemeSettings();

  return (
    <div
      className={`product-card ${
        product?.stock?.some((qty) => qty?.stock_qty === 0) ? "disabled" : ""
      }`}
    >
      <div className="product-image">
        <img
          src={product?.image ? product?.image : NoImage}
          alt={product?.name}
        />
      </div>
      <div className="product-details">
        <span className="product-type mb-4">{product?.item_type}</span>
        <h4 className="product-name">{product?.name}</h4>
        <span className="product-qty">
          {product?.stock?.map((qty) => qty?.stock_qty)}
        </span>
        <div className="price-addbtn">
          <span className="product-price">
            {themeSettings?.currency_symbol || "$"}
            {formatPrice(product?.product_price) || "NA"}
          </span>
          <button className="add-button" onClick={() => onAddToCart(product)}>
            +Add
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
