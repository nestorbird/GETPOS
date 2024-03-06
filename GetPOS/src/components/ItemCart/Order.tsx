import React, { useContext, useState } from "react";
import UserItemsContext from "../../common/cartContext";
import ModalBox from "../../common/popup";

const OrderSuccess = ({ orderData }) => {
  const cartListItems: any = useContext(UserItemsContext);
  const [visibility, setVisibility] = useState(false);

  const popupCloseHandler = (e) => {
    setVisibility(e);
  };

  const RenderOrderSuccess = () => {
    return (
      <div className="column">
        <div></div>
      </div>
    );
  };

  return (
    <ModalBox
      onClose={popupCloseHandler}
      visibility={visibility}
      title={
        cartListItems?.payloadData?.customer ? "Add Cart" : "Select Customer"
      }
      htmlRender={() => <RenderOrderSuccess />}
    />
  );
};

export default OrderSuccess;
