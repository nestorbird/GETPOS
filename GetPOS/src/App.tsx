import "./App.css";
import { FrappeProvider } from "frappe-react-sdk";
import SideBar from "./components/SideNavigation";
import ItemsSection from "./components/ItemsSection";
import ItemCart from "./components/ItemCart";
import { useState } from "react";
import UserItemsContext from "./common/cartContext";

function App() {
  const [cartItems, setCartItems] = useState([]);
  const [payloadData, setPayloadData] = useState({ customer: "" });

  return (
    <div className="App">
      <FrappeProvider url={import.meta.env.VITE_FRAPPE_PATH ?? ""}>
        <div className="row">
          <SideBar />

          <UserItemsContext.Provider
            value={{ cartItems, setCartItems, payloadData, setPayloadData }}
          >
            <div className="main-content">
              <div className="items-section">
                {/* Category & Product Search */}
                <div
                  className="row"
                  style={{
                    justifyContent: "space-between",
                  }}
                >
                  <h1 style={{ marginLeft: "2rem" }}>Choose Category</h1>
                  <div className="input-search-box">
                    <button
                      style={{
                        width: "2rem",
                        height: "38px",
                        borderRadius: "8px",
                        backgroundColor: "#dc1e44",
                        border: "1px #d3d3d3",
                      }}
                    >
                      <i className="fa fa-search"></i>
                    </button>
                    <input
                      type="text"
                      style={{
                        marginRight: "2rem",
                        height: "2rem",
                        marginTop: "1rem",
                        borderRadius: "8px",
                        border: "1px #d3d3d3",
                      }}
                      placeholder="Search Product / Category"
                    ></input>
                  </div>
                </div>
                {/* Cart Items Provider */}

                {/* Items Section */}
                <ItemsSection />
              </div>

              {/* Item Cart Section */}
              <div className="cart-section">
                <ItemCart />
              </div>
            </div>
          </UserItemsContext.Provider>
        </div>
      </FrappeProvider>
    </div>
  );
}

export default App;
