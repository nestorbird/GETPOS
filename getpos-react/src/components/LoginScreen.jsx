import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Input, Button, Tooltip } from "antd";
import { EyeOutlined, EyeInvisibleOutlined } from "@ant-design/icons";
import Layout from "./Layout";
import { login } from "../modules/LandingPage";

const LoginScreen = () => {
 
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  useEffect(() => {
    const user = localStorage.getItem("user");
    if (user) {
      navigate("/main");
    }
  }, [navigate]);
  const handleLogin = async (e) => {
    e.preventDefault(); // Prevent default form submission behavior
    try {
      const data = await login(email, password);

      if (data.message && data.message.success_key === 1) {
        // Store session information in local storage
        const user = {
          name: data.message.username,
          email: data.message.email,
          role: data.message.role, // Assuming role is included in the response
          profileImage: data.message.profile_image, // Assuming profile_image is included in the response
        };
        localStorage.setItem("user", JSON.stringify(user));
        localStorage.setItem("sid", data.message.sid);
        localStorage.setItem("api_key", data.message.api_key);
        localStorage.setItem("api_secret", data.message.api_secret);
        navigate("/location", { state: { loginResponse: data } });
        // Clean up sensitive info from local storage
        localStorage.removeItem("sid");
        localStorage.removeItem("api_key");
        localStorage.removeItem("api_secret");
      } else {
        alert("Login failed. Please check your credentials.");
      }
    } catch (error) {
      console.error("Login error:", error);
      alert("An error occurred during login. Please try again.");
    }
  };

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
    setTimeout(() => {
      setShowPassword(false);
    }, 3000); // Mask password after 3 seconds
  };

  return (
    <div className="login-page">
    
      <Layout showFooter={false} showDropdown={false}>
        <div className="login-screen">
          <form className="login-form" onSubmit={handleLogin}>
            <div className="form-group">
              <input
                id="email"
                type="text"
                placeholder="Enter Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                suffix={
                  <Tooltip
                    title={showPassword ? "Hide Password" : "Show Password"}
                  >
                    {showPassword ? (
                      <EyeInvisibleOutlined
                        onClick={handleTogglePasswordVisibility}
                      />
                    ) : (
                      <EyeOutlined onClick={handleTogglePasswordVisibility} />
                    )}
                  </Tooltip>
                }
                required
              />
            </div>
            <button className="login-button" type="primary" htmlType="submit">
              Login
            </button>
          </form>
        </div>
      </Layout>
    </div>
  );
};

export default LoginScreen;
