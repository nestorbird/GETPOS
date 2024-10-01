import React, { useContext, useEffect, useState } from "react";
import "./style.css";
import Logo from "../assets/images/logo.png";
import SearchIcon from "../assets/images/Search-icon.png";
import { useLocation } from "react-router-dom";
import { NavLink } from "react-router-dom";
const Header = ({ onSearch }) => {
  const [user, setUser] = useState(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    const userData = localStorage.getItem("user");

    if (userData) {
      setUser(JSON.parse(userData));
    } else {
      console.log("No user data found in localStorage");
    }
  }, []);

  const costCenter = localStorage.getItem("costCenter");
  const Openshift = localStorage.getItem("openingShiftResponse");

  const handleSearch = (e) => {
    setSearchQuery(e.target.value);
    onSearch(e.target.value);
  };

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  return (
    <header className="header">
      <div className="header-logo">
        {user && costCenter && Openshift ? (
          <NavLink to="/main">
            <img src={Logo} alt="Logo" />
          </NavLink>
        ) : (
          <img src={Logo} alt="Logo" />
        )}
      </div>
      <div className="header-right">
        {user && location.pathname === "/main" ? (
          <>
            <div className="search-container">
              <input
                type="text"
                placeholder="Search"
                value={searchQuery}
                onChange={handleSearch}
              />
              <img src={SearchIcon} alt="" />
            </div>
            {/* <div className="header-user-profile">
            <img
              src={user.profileImage || PlaceholderProfile}
              alt="Profile"
              className="profile-image"
            />
            <span className="header-user-name">
              {user.name} <br /> {user.role}
            </span>
            <div className="header-user-dropdown">
              <button className="dropdown-button">
                <img src={Arrow} alt="" />
              </button>
              <div className="dropdown-content">
                <a to="/profile">Profile</a>
                <a to="/closeshift">Logout</a>
              </div>
            </div>
          </div> */}
          </>
        ) : (
          []
        )}
        <div
          className={`burger-menu ${menuOpen ? "open" : ""}`}
          onClick={toggleMenu}
        >
          <div className="burger-bar"></div>
          <div className="burger-bar"></div>
          <div className="burger-bar"></div>
        </div>
        <div className={`mobile-menu ${menuOpen ? "open" : ""}`}>
          {user ? (
            <>
              <NavLink to="/profile">Profile</NavLink>
              <NavLink to="/logout">Logout</NavLink>
            </>
          ) : (
            <NavLink to="/">Login</NavLink>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
