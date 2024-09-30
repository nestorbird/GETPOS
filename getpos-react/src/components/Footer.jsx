import React from "react";
import { NavLink } from "react-router-dom";
import Home from "../assets/images/icon-home.svg";
import Order from "../assets/images/icon-order.svg";
import Customer from "../assets/images/icon-customer.svg";
import Profile from "../assets/images/icon-profile.svg";
import Logout from "../assets/images/logout.png";
import BookingIcon from "../assets/images/Booking.png"; // Add a booking icon

const Footer = () => {
  return (
    <footer className="footer">
      <nav>
        <ul className="footer-nav">
          <li>
            <NavLink
              to="/main"
              className="footer-nav-item"
              activeClassName="active"
              exact
            >
              <img src={Home} alt="Home" />
              <span className="footer-label">Home</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/order"
              className="footer-nav-item"
              activeClassName="active"
            >
              <img src={Order} alt="Order" />
              <span className="footer-label">Order</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/customer"
              className="footer-nav-item"
              activeClassName="active"
            >
              <img src={Customer} alt="Customer" />
              <span className="footer-label">Customer</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/profile"
              className="footer-nav-item"
              activeClassName="active"
            >
              <img src={Profile} alt="Profile" />
              <span className="footer-label">My Profile</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/closeshift"
              className="footer-nav-item"
              activeClassName="active"
            >
              <img src={Logout} alt="Logout" />
              <span className="footer-label">Logout</span>
            </NavLink>
          </li>
          {/* <li>
            <NavLink
              to="/booking"
              className="footer-nav-item"
              activeClassName="active"
            >
              <img src={BookingIcon} alt="Booking" />
              <span className="footer-label">Booking</span>
            </NavLink>
          </li> */}
        </ul>
        <></>
      </nav>
    </footer>
  );
};

export default Footer;
