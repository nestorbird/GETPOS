import React, { useState } from "react";
import { useOpenShift } from "../components/OpenShiftContext";
import Layout from "../components/Layout";
import ChangePassword from "../components/ChangePassword";
import BasicInfo from "../components/BasicInfo";
import Finance from "../components/Finance";
import IconPassword from "../assets/images/icon-changePwd.svg";
import IconFinance from "../assets/images/icon-finance.svg";
import IconLogout from "../assets/images/icon-logout.svg";
import { Drawer, Button } from "antd";
import { DoubleRightOutlined } from "@ant-design/icons"; 
import useIsSmallScreen from "../hooks/useIsSmallScreen";
import { NavLink } from "react-router-dom";
const MyAccount = () => {
  const { openShiftData } = useOpenShift();
  const { cashBalance, digitalBalance, selectedProfile } = openShiftData;
  const [selectedTab, setSelectedTab] = useState("Change Password");
  const [isSidebarVisible, setIsSidebarVisible] = useState(false);

  const isSmallScreen = useIsSmallScreen();  

  const renderContent = () => {
    switch (selectedTab) {
      // case "Basic Info":
      //   return <BasicInfo />;
      case "Change Password":
        return <ChangePassword />;
      case "Finance":
        return <Finance />;
      default:
        return null;
    }
  };

  const sidebarContent = (
    <ul>
      {/* <li
        className={selectedTab === "Basic Info" ? "active" : ""}
        onClick={() => setSelectedTab("Basic Info")}
      >
        <span>
          <img src={IconPassword} alt="Basic Info" />
          Basic Info
        </span>
      </li> */}
      <li
        className={selectedTab === "Change Password" ? "active" : ""}
        onClick={() => setSelectedTab("Change Password")}
      >
        <span>
          <img src={IconPassword} alt="Change Password" />
          Change Password
        </span>
      </li>
      {/* <li
        className={selectedTab === "Finance" ? "active" : ""}
        onClick={() => setSelectedTab("Finance")}
      >
        <span>
          <img src={IconFinance} alt="Finance" />
          Finance
        </span>
      </li> */}
      <li>
        <NavLink to="/closeshift">
          <img src={IconLogout} alt="Close Shift" />
          Close Shift 
        </NavLink>
      </li>
    </ul>
  );

  return (
    <Layout>
      {isSmallScreen && (
        <Button
          className="menu-button"
          onClick={() => setIsSidebarVisible(true)}
          icon={<DoubleRightOutlined />}
        />
      )}
      <div className="account-page">
        {isSmallScreen ? (
          <Drawer
            title="Profile"
            placement="left"
            closable={true}
            onClose={() => setIsSidebarVisible(false)}
            visible={isSidebarVisible}
            bodyStyle={{ padding: 0 }}
          >
            <div className="profile-sidebar" onClick={() => setIsSidebarVisible(false)}>
              {sidebarContent}
            </div>
          </Drawer>
        ) : (
          <div className="profile-sidebar">
            {sidebarContent}
          </div>
        )}
        <div className="content-right">{renderContent()}</div>
      </div>
    </Layout>
  );
};

export default MyAccount;
