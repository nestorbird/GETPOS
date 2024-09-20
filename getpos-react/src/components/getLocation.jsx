import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Layout from "./Layout";
import { fetchstore, getLocation } from "../modules/LandingPage";

const Location = () => {
  const [location, setLocation] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState("");
  const [customLocationData, setCustomLocationData] = useState([]);
  const [selectedCostCenter, setSelectedCostCenter] = useState("");
  const navigate = useNavigate();
  const locationState = useLocation();
  const loginResponse = locationState.state?.loginResponse;

  // Fetch locations from API
  const fetchLocations = async () => {
    try {
      const data = await getLocation();
      if (data.status === 200) {
        setLocation(data.data.message || []);
      } else {
        alert("Failed to fetch locations. Please try again.");
      }
    } catch (error) {
      console.error("Error fetching locations:", error);
      alert("An error occurred while fetching locations. Please try again.");
    }
  };

  useEffect(() => {
    fetchLocations();
  }, []);

  // Fetch stores based on selected location
  const fetchStores = async (selected) => {
    try {
      const res = await fetchstore(selected);
      if (res.status === 200) {
        setCustomLocationData(res.data.message || []);
      } else {
        console.log("Failed to fetch stores. Please check the API.");
      }
    } catch (error) {
      console.error("Error fetching stores:", error);
      // Optional: alert the user about the error
    }
  };

  const handleLocationChange = (e) => {
    const selected = e.target.value;
    setSelectedLocation(selected);
    fetchStores(selected);
  };

  const handleCostCenterChange = (e) => {
    const selected = e.target.value;
    setSelectedCostCenter(selected);
    localStorage.setItem("costCenter", selected);
  };

  const handleProceed = (e) => {
    e.preventDefault(); // Prevent default form submission behavior
    if (selectedLocation && selectedCostCenter) {
      navigate("/openshift", { state: { loginResponse } });
    } else {
      alert("Please select both location and store before proceeding.");
    }
  };

  // Handle Enter key press
  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault(); // Prevent default form submission
      handleProceed(e);
    }
  };

  return (
    <div className="login-page">
      <Layout showFooter={false} showDropdown={false}>
        <div className="login-screen">
          <form
            className="login-form"
            onSubmit={handleProceed}
            onKeyDown={handleKeyDown}
          >
            <div className="form-group">
              <select
                id="location"
                value={selectedLocation}
                onChange={handleLocationChange}
                required
              >
                <option value="">Select Location</option>
                {location.map((loc, index) => (
                  <option key={index} value={loc.custom_location}>
                    {loc.custom_location}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <select
                id="costCenter"
                value={selectedCostCenter}
                onChange={handleCostCenterChange}
                required
              >
                <option value="">Select Store</option>
                {customLocationData.map((loc, index) => (
                  <option key={index} value={loc.name}>
                    {loc.name}
                  </option>
                ))}
              </select>
            </div>
            <button className="button-location-submit" type="submit">
              Submit
            </button>
          </form>
        </div>
      </Layout>
    </div>
  );
};

export default Location;
