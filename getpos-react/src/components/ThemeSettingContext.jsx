import React, { createContext, useState, useEffect, useContext } from 'react';
import { getGuestCustomer } from '../modules/LandingPage'; // Adjust the import based on your API file location

const ThemeSettingsContext = createContext();

export const useThemeSettings = () => {
  return useContext(ThemeSettingsContext);
};

export const ThemeSettingsProvider = ({ children }) => {
  const [themeSettings, setThemeSettings] = useState(null);

  const handleGetGuestCustomer = async () => {
    try {
      const res = await getGuestCustomer();
      if (res.status === 200) {
        console.log(res.data.message.data);
        setThemeSettings(res.data.message.data);
      } else {
        console.log('Error in getting the Guest Customer');
      }
    } catch (error) {
      console.log('Error in fetching guest customer:', error.message);
    }
  };

  useEffect(() => {
    handleGetGuestCustomer();
  }, []);

  return (
    <ThemeSettingsContext.Provider value={themeSettings}>
      {children}
    </ThemeSettingsContext.Provider>
  );
};
