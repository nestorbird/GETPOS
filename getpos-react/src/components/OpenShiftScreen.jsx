import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Layout from "./Layout";
import { useOpenShift } from "./OpenShiftContext";
import {
  fetchOpeningData,
  getGuestCustomer,
  getOpeningShift,
} from "../modules/LandingPage";

const OpenShiftScreen = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const loginResponse = location.state && location.state.loginResponse;
  const [company, setCompany] = useState("");

  const { openShiftData, setOpenShiftData } = useOpenShift();
  const { selectedProfile } = openShiftData;

  const [posProfiles, setPosProfiles] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [paymentBalances, setPaymentBalances] = useState(() => {
    const savedBalances = localStorage.getItem("paymentBalances");
    return savedBalances ? JSON.parse(savedBalances) : {};
  });
  const [formErrors, setFormErrors] = useState({});

  const handleGetGuestCustomer = async () => {
    try {
      const res = await getGuestCustomer();
      if (res.status === 200) {
        setCompany(res.data.message.data.default_company);
        console.log("Guest customer", company);
      } else {
        console.log("Error in getting the Guest Customer");
      }
    } catch (error) {
      console.log("Error in fetching guest customer:", error.message);
    }
  };

  useEffect(() => {
    if (!loginResponse) {
      navigate("/getpos-react"); //debug
    } else {
      fetchData();
      clearFields();
      clearLocalStorage();
    }
    handleGetGuestCustomer();
  }, [loginResponse]);

  const fetchData = async () => {
    try {
      const data = await fetchOpeningData();
      const profiles = data.pos_profiles_data.map((profile) => profile.name);
      setPosProfiles(profiles);
      setPaymentMethods(data.payments_method);
    } catch (error) {
      console.error("Error fetching POS profiles:", error);
    }
  };

  const handleCreateOpeningShift = async () => {
    const balanceDetails = paymentMethods
      .filter((method) => method.parent === selectedProfile)
      .map((method) => ({
        mode_of_payment: method.mode_of_payment,
        amount: parseFloat(paymentBalances[method.mode_of_payment] || 0),
      }));

    const openingShiftData = {
      pos_profile: selectedProfile,
      company: company,
      balance_details: balanceDetails,
    };

    try {
      const openingShiftResponse = await getOpeningShift(openingShiftData);
      console.log("POS opening shift created:", openingShiftResponse);

      localStorage.setItem(
        "openingShiftResponse",
        JSON.stringify(openingShiftResponse)
      );

      return openingShiftResponse;
    } catch (error) {
      console.error("Error creating POS opening shift:", error);
      throw error;
    }
  };

  // const handleLogin = async () => {
  //   console.log("Logging in...");
  //   localStorage.setItem("openShiftData", JSON.stringify(openShiftData));
  //   localStorage.setItem("paymentBalances", JSON.stringify(paymentBalances));

  //   await handleCreateOpeningShift();

  //   navigate("/main");
  // };
  const handleLogin = async () => {
    const errors = {};

    if (!selectedProfile) {
      errors.selectedProfile = "POS Profile is required.";
    }

    filteredPaymentMethods.forEach((method) => {
      if (!paymentBalances[method.mode_of_payment]) {
        errors[
          method.mode_of_payment
        ] = `Opening ${method.mode_of_payment} Balance is required.`;
      }
    });

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    console.log("Logging in...");
    localStorage.setItem("openShiftData", JSON.stringify(openShiftData));
    localStorage.setItem("paymentBalances", JSON.stringify(paymentBalances));

    await handleCreateOpeningShift();

    navigate("/main");
  };

  const storedResponse = localStorage.getItem("openingShiftResponse");
  const parsedResponse = storedResponse ? JSON.parse(storedResponse) : null;

  console.log("Stored Response:", parsedResponse);

  const handleProfileChange = (event) => {
    const value = event.target.value;
    const newOpenShiftData = {
      ...openShiftData,
      selectedProfile: value === "" ? "" : value,
    };
    setOpenShiftData(newOpenShiftData);
    setPaymentBalances({});
    localStorage.setItem("openShiftData", JSON.stringify(newOpenShiftData));
    setFormErrors({}); // Clear errors on profile change
  };

  const handlePaymentBalanceChange = (method, value) => {
    const numericValue = value.replace(/[^\d.]/g, "");

    const parts = numericValue.split(".");
    let formattedValue = parts[0];

    if (parts.length === 2) {
      formattedValue += "." + parts[1].slice(0, 2);
    }

    const newPaymentBalances = {
      ...paymentBalances,
      [method]: formattedValue,
    };

    setPaymentBalances(newPaymentBalances);
    localStorage.setItem("paymentBalances", JSON.stringify(newPaymentBalances));
    setFormErrors((prevErrors) => ({ ...prevErrors, [method]: "" })); // Clear specific field error
  };

  const filteredPaymentMethods = paymentMethods.filter(
    (method) => method.parent === selectedProfile
  );
  const clearFields = () => {
    setPosProfiles([]);
    setPaymentMethods([]);
    setPaymentBalances({});
    setOpenShiftData({ selectedProfile: "" });
  };

  const clearLocalStorage = () => {
    localStorage.removeItem("paymentBalances");
    localStorage.removeItem("openingShiftResponse");
  };

  return (
    <div className="login-page">
      <Layout showFooter={false} showDropdown={false}>
        <div className="login-screen">
          <h1>OPEN SHIFT</h1>
          <form className="login-form">
            <div className="form-group">
              <select
                id="pos-profile"
                value={selectedProfile || ""}
                onChange={handleProfileChange}
              >
                <option value="" disabled>
                  Select POS Profile Name
                </option>
                {posProfiles.map((profile) => (
                  <option key={profile} value={profile}>
                    {profile}
                  </option>
                ))}
              </select>
              {formErrors.selectedProfile && (
                <span className="error">{formErrors.selectedProfile}</span>
              )}
            </div>
            {selectedProfile && (
              <>
                {filteredPaymentMethods.map((method) => (
                  <div key={method.name} className="form-group payment-method">
                    <input
                      type="text"
                      placeholder={`Enter Opening ${method.mode_of_payment} Balance`}
                      value={paymentBalances[method.mode_of_payment] || ""}
                      onChange={(e) =>
                        handlePaymentBalanceChange(
                          method.mode_of_payment,
                          e.target.value
                        )
                      }
                    />
                    {formErrors[method.mode_of_payment] && (
                      <span className="error">
                        {formErrors[method.mode_of_payment]}
                      </span>
                    )}
                  </div>
                ))}
              </>
            )}
            <button
              className="button-open-shift"
              type="button"
              onClick={handleLogin}
            >
              Login
            </button>
          </form>
        </div>
      </Layout>
    </div>
  );
};

export default OpenShiftScreen;
