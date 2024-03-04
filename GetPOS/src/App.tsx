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
                  <div className="input-search-box row">
                    <button
                      style={{
                        width: "3rem",
                        height: "3rem",
                        borderRadius: "8px",
                        backgroundColor: "#dc1e44",
                        border: "1px #d3d3d3",
                      }}
                    >
                      <span className="material-symbols-outlined">search</span>
                    </button>
                    <input
                      className="search-product-category"
                      type="text"
                      style={{
                        
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
