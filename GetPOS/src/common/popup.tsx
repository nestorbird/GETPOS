import React, { useEffect, useState } from "react";

const ModalBox = (props) => {
  const { title, htmlRender } = props;

  const [showPopup, setShowPopup] = useState(false);

  useEffect(() => {
    setShowPopup(props.visibility);
  }, [props.visibility]);

  const handleCloseModal = (e) => {
    e.preventDefault();
    setShowPopup(false);
    props.onClose(false);
  };
  return (
    <div
      className="modal-box"
      style={{
        visibility: showPopup ? "visible" : "hidden",
        opacity: showPopup ? "1" : "0",
        backdropFilter: "blur(1px)",
      }}
    >
      <div className="popup">
        <h2>{title}</h2>
        {title && (
          <a className="close" href="" onClick={handleCloseModal}>
            &times;
          </a>
        )}
        <div className="modal-content">{htmlRender()}</div>
      </div>
    </div>
  );
};

export default ModalBox;
