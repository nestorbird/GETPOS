import React, { useState, useEffect, useContext, useRef } from "react";
import Sidebar from "./Sidebar";
import ProductCatalog from "./ProductCatalog";
import Cart from "./Cart";
import Header from "./Header";
import Footer from "./Footer";
import {
  fetchCategoriesAndProducts,
  getItemByScan,
} from "../modules/LandingPage";
import { Button, Spin, Modal, notification } from "antd";
import { ShoppingCartOutlined, DoubleRightOutlined } from "@ant-design/icons";
import useIsSmallScreen from "../hooks/useIsSmallScreen";
import { CartContext } from "../common/CartContext";
import ProductPopup from "./ProductPopup";
import ReservationPopup from "./ReservationPopup";
import DynamicTableAvailabilityPopup from "./TableAvailability";
import BookingSummaryPopup from "./BookingSummary";

const MainScreen = () => {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [popupProduct, setPopupProduct] = useState(null);
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isCartVisible, setIsCartVisible] = useState(false);
  const [isSidebarVisible, setIsSidebarVisible] = useState(false);
  const [isReservaionPopupVisible, setIsReservaionPopupVisible] =
    useState(false);
  const [isTableAvailabilityPopupVisible, setIsTableAvailabilityPopupVisible] =
    useState(false);
  const [isBookingSummaryPopupVisible, setIsBookingSummaryPopupVisible] =
    useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [barcode, setBarcode] = useState("");
  const [bookingData, setBookingData] = useState({});
  const lastKeyPressTime = useRef(0);

  const isSmallScreen = useIsSmallScreen();
  const costCenter = localStorage.getItem("costCenter");

  const { addItemToCart } = useContext(CartContext);
  const searchInputRef = useRef(null);
  const scanTimeout = useRef(null);
  const [NotFound, setNotFound] = useState(false);

  const getSelectedCustomer = () => {
    const customer = localStorage.getItem("selectedCustomer");
    return customer ? JSON.parse(customer) : null;
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await fetchCategoriesAndProducts(costCenter);
        setCategories(data);
        if (data.length > 0) {
          setSelectedCategory(data[0].item_group);
          const allProducts = data.flatMap((category) =>
            category.items.map((item) => ({
              ...item,
              category: category.item_group,
            }))
          );
          setProducts(allProducts);
        }
        setLoading(false);
      } catch (error) {
        console.error("Error fetching data", error);
        setLoading(false);
      }
    };

    fetchData();
  }, [costCenter]);

  const handleSearch = (query) => {
    if (!query) {
      setNotFound(false);
    }

    setSearchQuery(query);
    if (query) {
      const results = products.filter(
        (product) =>
          product.name.toLowerCase().includes(query.toLowerCase()) ||
          product.category.toLowerCase() === query.toLowerCase()
      );
      setSearchResults(results);
      if (results.length === 0) {
        setNotFound(true);
      } else {
        setNotFound(false);
      }
    } else {
      setSearchResults([]);
    }
  };

  const handleKeyDown = (e) => {
    const activeElement = document.activeElement;
    const currentTime = new Date().getTime();

    if (activeElement !== searchInputRef.current) {
      const isScan = currentTime - lastKeyPressTime.current < 50;
      lastKeyPressTime.current = currentTime;

      if (e.keyCode >= 48 && e.keyCode <= 90) {
        setBarcode((prev) => prev + e.key);
      }

      if (e.keyCode === 13 && barcode.length > 3 && isScan) {
        clearTimeout(scanTimeout.current);
        scanTimeout.current = setTimeout(() => {
          console.log("Scanned Barcode:", barcode);
          handleScan(barcode);
          setBarcode("");
        }, 500);
      }
    }
  };

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);

    return function cleanup() {
      document.removeEventListener("keydown", handleKeyDown);
      clearTimeout(scanTimeout.current);
    };
  }, [barcode]);

  const sanitizeBarcode = (barcode) => {
    return barcode.replace(/\D/g, "");
  };

  const handleScan = async (barCodeString) => {
    const sanitizedBarcode = sanitizeBarcode(barCodeString);
    const selectedCustomer = getSelectedCustomer();

    if (!selectedCustomer) {
      Modal.error({
        title: "Attention!",
        content: "Please select a customer before adding items to the cart.",
      });
      return;
    }

    try {
      const res = await getItemByScan(sanitizedBarcode, costCenter);
      if (res.status === 200) {
        console.log(res.data.message, "check");
        const items = res.data.message[0].items;

        items.forEach((item) => {
          const totalStockQty =
            item.stock?.reduce(
              (total, stock) => total + (stock.stock_qty || 0),
              0
            ) || 0;

          if (totalStockQty > 0) {
            addItemToCart({
              ...item,
              quantity: 1,
              isScanned: true,
            });
          } else {
            Modal.warning({
              title: "Item Out of Stock",
              content: `The item "${item.name}" is out of stock.`,
            });
          }
        });
      } else {
        Modal.warning({
          title: "Item Not Found",
          content: "The scanned item was not found.",
        });
      }
    } catch (error) {
      if (error instanceof TypeError) {
        Modal.warning({
          title: "Item Not Found",
          content: "There was an issue while processing the scanned item.",
        });
      } else {
        Modal.error({
          title: "Scan Error",
          content: "There was an error scanning the item. Please try again.",
        });
      }
    }
  };

  if (loading) {
    return (
      <div className="loading-spin">
        <Spin tip="Loading..."></Spin>
      </div>
    );
  }

  const handleAddToCart = (product) => {
    setPopupProduct(product);
  };

  const displayedProducts =
    searchResults.length > 0
      ? searchResults
      : NotFound
      ? []
      : products.filter((product) => product.category === selectedCategory);

  const highlightedCategory =
    searchResults.length > 0 ? searchResults[0]?.category : selectedCategory;

  return (
    <>
      <div className="cart-page-layout">
        <div className="main-screen">
          <Header onSearch={handleSearch} searchQuery={searchQuery} />
          {isSmallScreen && (
            <Button
              className="menu-button"
              onClick={() => setIsSidebarVisible(true)}
              icon={<DoubleRightOutlined />}
            />
          )}
          <div className="left-cont">
            <Sidebar
              categories={categories}
              onSelectCategory={setSelectedCategory}
              selectedCategory={highlightedCategory}
              isVisible={isSidebarVisible}
              onClose={() => setIsSidebarVisible(false)}
              isSmallScreen={isSmallScreen}
            />
            <ProductCatalog
              categoryName={highlightedCategory}
              products={displayedProducts}
              onAddToCart={handleAddToCart}
            />
          </div>
          <Footer />
        </div>
        <div
          className={`cart-container ${isCartVisible ? "cart-visible" : ""}`}
        >
          <Cart
            onReservationClick={() => {
              setIsReservaionPopupVisible(true);
            }}
          />
        </div>
        <Button
          className="cart-button"
          onClick={() => setIsCartVisible(!isCartVisible)}
          icon={<ShoppingCartOutlined />}
        />
        {popupProduct && (
          <ProductPopup
            product={popupProduct}
            onAddItem={(item) => {
              addItemToCart(item);
              setPopupProduct(null);
            }}
            onClose={() => setPopupProduct(null)}
          />
        )}
        {isReservaionPopupVisible && (
          <ReservationPopup
            visible={isReservaionPopupVisible}
            onSubmit={(
              selectedDate,
              selectedTime,
              numGuests,
              specialRequest
            ) => {
              setIsReservaionPopupVisible(false);
              setIsTableAvailabilityPopupVisible(true);
              setBookingData({
                selectedDate,
                selectedTime,
                numGuests,
                specialRequest,
              });
              console.log("1st submitted", bookingData);
            }}
            onClose={() => {
              setIsReservaionPopupVisible(false);
            }}
          />
        )}
        {isTableAvailabilityPopupVisible && (
          <DynamicTableAvailabilityPopup
            visible={isTableAvailabilityPopupVisible}
            onClose={() => {
              setIsTableAvailabilityPopupVisible(false);
            }}
            onSubmit={(SelectedTables) => {
              setIsTableAvailabilityPopupVisible(false);
              setIsBookingSummaryPopupVisible(true);
              setBookingData((prevData) => ({
                ...prevData,
                tableNumbers: SelectedTables,
              }));
              console.log("2nd submitted");
            }}
          />
        )}
        {isBookingSummaryPopupVisible && (
          <BookingSummaryPopup
            bookingData={bookingData}
            visible={isBookingSummaryPopupVisible}
            onClose={() => {
              setIsBookingSummaryPopupVisible(false);
            }}
          />
        )}
      </div>
    </>
  );
};

export default MainScreen;
