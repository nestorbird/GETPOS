import React, { useEffect, useState } from "react";
import Header from "./Header";
import Footer from "./Footer";

const Layout = ({ children, showFooter = true, showDropdown = true }) => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Retrieve user information from local storage
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  return (
    <div className="layout">
      <Header showDropdown={user && showDropdown} />
      <main>{children}</main>
      {showFooter && <Footer />}
    </div>
  );
};

export default Layout;
