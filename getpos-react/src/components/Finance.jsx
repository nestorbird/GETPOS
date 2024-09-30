// src/components/Finance.js
import React, { useEffect, useState } from "react";
import { fetchBasicInfo } from "../modules/LandingPage";
import { Spin } from "antd";

const Finance = ({ balance }) => {
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [profileInfo, setProfileInfo] = useState({});
  const user = JSON.parse(
    localStorage.getItem("user")
  );
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
      <h3>Finance</h3>
      <div className="content">
        {loading ? (
          <Spin tip="Loading..."></Spin>
        ) : error ? (
          <p>{error}</p>
        ) : (
          <div className="profile-cont">
            <h5>CASH BALANCE</h5>
            <p>{profileInfo.balance}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Finance;
