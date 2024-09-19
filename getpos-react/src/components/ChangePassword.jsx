import React, { useContext, useState } from "react";
import { changePassword } from "../modules/LandingPage";
import { useNavigate } from "react-router-dom";
import { notification } from "antd";
import { CartContext } from "../common/CartContext";

const ChangePassword = () => {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [renewPassword, reSetNewPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const userString = localStorage.getItem("user");
  const user = userString ? JSON.parse(userString) : null;
  const { cartItems, setCartItems } = useContext(CartContext);


  const clearCookies = () => {
    document.cookie.split(";").forEach((c) => {
      document.cookie = c
        .replace(/^ +/, "")
        .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (newPassword !== renewPassword) {
      notification.error({
        message: "Error",
        description: "New password and re-entered password do not match.",
      });
      setError("New password and re-entered password do not match.");
      setMessage(null);
      return;
    }
    try {
      const response = await changePassword(user.email, oldPassword, newPassword);
      if (response.status === 200) {
        notification.success({
          message: "Success",
          description: "Password changed successfully",
        });
        setError(null);

        // Clear cookies and navigate to login
        clearCookies();
        setTimeout(() => {
          navigate("/");

        }, 1000);
        setCartItems([]);
        localStorage.clear();
      } else {
        setMessage(null);
        setError("Failed to change password");
      }
    } catch (error) {
      setMessage(null);
      setError("Error changing password");
    }
  };

  return (
    <div className="change-password">
      <h3>Change Password</h3>
      <div className="content">
        <form onSubmit={handleChangePassword}>
          <div>
            <input
              type="password"
              placeholder="Enter Old Password"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
            />
          </div>
          <div>
            <input
              type="password"
              placeholder="Enter New Password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
          </div>
          <div>
            <input
              type="password"
              placeholder="Re-Enter New Password"
              value={renewPassword}
              onChange={(e) => reSetNewPassword(e.target.value)}
            />
            {error && <p style={{color:'red'}}>{error}</p>}
          </div>
          <button type="submit">Change Password</button>
          {message && <p>{message}</p>}
          {/* {error && <p>{error}</p>} */}
        </form>
      </div>
    </div>
  );
};

export default ChangePassword;
