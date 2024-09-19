import React, { useEffect, useState } from "react";
import { changePassword, fetchBasicInfo } from "../modules/LandingPage";
import { useOpenShift } from "./OpenShiftContext";
import { Spin } from "antd";

const BasicInfo = () => {
  const [email, setEmail] = useState("");
  // const [user, setUser] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);
  const [profileInfo, setProfileInfo] = useState({});
  const [loading, setLoading] = useState(true);
  const { openShiftData } = useOpenShift();
  const { cashBalance, digitalBalance, selectedProfile } = openShiftData;
  const [selectedTab, setSelectedTab] = useState("Basic Info");

  const handleChangePassword = async () => {
    try {
      const response = await changePassword(email, password);
      if (response.message.success_key === 1) {
        setMessage("Password changed successfully");
        setError(null);
      } else {
        setMessage(null);
        setError("Failed to change password");
      }
    } catch (error) {
      setMessage(null);
      setError("Error changing password");
    }
  };

  const userString = localStorage.getItem("user");
  const user = userString ? JSON.parse(userString) : null;

  useEffect(() => {
    const loadProfileInfo = async () => {
      try {
        const data = await fetchBasicInfo(user.email);
        setProfileInfo(data);
      } catch (error) {
        setError("Error fetching profile information");
      } finally {
        setLoading(false);
      }
    };

    loadProfileInfo();
  }, []);

  return (
    <div>
      <h3>Basic Info</h3>
      <div className="content">
        {loading ? (
          <Spin tip="Loading..."></Spin>
        ) : error ? (
          <p>{error}</p>
        ) : (
          <div>
            <h4>{profileInfo.full_name} </h4>
            <p className="profile-manager">Hub Manager</p>
            {/* <p className="profile-manager">{profileInfo.hub_manager}</p> 
            <p className="profile-mobile">{profileInfo.mobile_no || "N/A"}</p>*/}
            <p className="profile-email">{profileInfo.email}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BasicInfo;
