import React from "react";
import { useFrappeGetCall } from "frappe-react-sdk";
import "./index.css";
import AllItems from "./Items";
import APIs from "../../constants/APIs";

const ItemsSection = () => {
  const { data, error, isLoading } = useFrappeGetCall(APIs.getItems);

  return (
    <>
      {isLoading && (
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            flexDirection: "row",
          }}
        >
          <div className="loader"></div>
        </div>
      )}
      <div className="items-category-section row">
        {data?.message?.length > 0 &&
          data?.message?.map((item) => {
            return (
              <div className="item-category-card">
                <img
                  src={
                    item.item_group_image
                      ? item.item_group_image
                      : "/assets/getpos/images/Group 796.png"
                  }
                  alt="Order"
                  style={{
                    width: "4rem",
                    borderRadius: "50%",
                    maxHeight: "2.5rem",
                  }}
                />
                <div className="content">
                  <h4>{item.item_group}</h4>
                </div>
              </div>
            );
          })}
      </div>
      <div className="items-section">
        {data?.message && data?.message?.length > 0 && (
          <AllItems items={data.message} />
        )}
      </div>
    </>
  );
};

export default ItemsSection;
