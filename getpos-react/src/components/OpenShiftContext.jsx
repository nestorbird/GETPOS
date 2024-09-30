// OpenShiftContext.js
import React, { createContext, useContext, useState, useEffect } from "react";

const OpenShiftContext = createContext();

export const OpenShiftProvider = ({ children }) => {
  const [openShiftData, setOpenShiftData] = useState(() => {
    const savedData = localStorage.getItem("openShiftData");
    return savedData ? JSON.parse(savedData) : { selectedProfile: '' }; // Initialize with an object that includes selectedProfile
  });

  useEffect(() => {
    if (openShiftData) {
      console.log("Saving openShiftData to localStorage:", openShiftData);
      localStorage.setItem("openShiftData", JSON.stringify(openShiftData));
    }
  }, [openShiftData]);

  return (
    <OpenShiftContext.Provider value={{ openShiftData, setOpenShiftData }}>
      {children}
    </OpenShiftContext.Provider>
  );
};

export const useOpenShift = () => useContext(OpenShiftContext);
