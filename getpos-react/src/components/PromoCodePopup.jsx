import React, { useState, useEffect } from "react";
import { Modal, Button, Input } from "antd";
import { getCouponCodeList } from "../modules/LandingPage";

const PromoCodePopup = ({ open, onClose, onApply, validatedPromoCode  }) => {
  const [promoCode, setPromoCode] = useState("");
  const [couponCodes, setCouponCodes] = useState([]);

  useEffect(() => {
    const fetchCouponCodes = async () => {
      const response = await getCouponCodeList();

      if (response.message && response.message.status === "success") {
        setCouponCodes(response.message.valid_coupons);
      }
    };

    if (open) {
      fetchCouponCodes();
    }
  }, [open]);

  const handleApplyClick = () => {
    onApply(promoCode);
    setPromoCode("");
    onClose();
  };

  const handleCouponCodeClick = (code) => {
    setPromoCode(code);
  };

  const getCouponCodeClass = (text) => {
    if (text.length > 15) return "coupon-code-large";
    if (text.length > 8) return "coupon-code-medium";
    return "coupon-code-small";
  };

  useEffect(() => {
    if (validatedPromoCode) {
      setPromoCode(validatedPromoCode);
    }
  }, [validatedPromoCode]);

  return (
    <Modal
      visible={open}
      onCancel={onClose}
      footer={null}
      className="promo-code-popup"
    >
      <div className="promo-code-box">
        <div className="promo-code-header">
          <div className="promoCodeContainer">
            <Input
              placeholder="Enter your promo code"
              value={promoCode}
              onChange={(e) => setPromoCode(e.target.value)}
              className="promo-input"
            />
            <Button type="default" onClick={handleApplyClick}>
              Apply
            </Button>
          </div>
        </div>
        <div className="couponCodesList">
          {couponCodes.length > 0 ? (
            <ul>
              {couponCodes.map((code, index) => (
                <li key={index} className="coupon-code-box">
                  <div className="coupon-left">
                    <span className={getCouponCodeClass(code.coupon_code)}>{code.coupon_code}</span>
                  </div>
                  <div className="coupon-right">
                    <div className="code-apply">
                      <span>{code.coupon_code}</span>
                      <span className="apply-btn"
                        onClick={() => handleCouponCodeClick(code.coupon_code)}
                      >
                        Apply
                      </span>
                    </div>
                    <div className="code-desc">{code.description}</div>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p>No valid coupons available.</p>
          )}
        </div>
      </div>
    </Modal>
  );
};

export default PromoCodePopup;
