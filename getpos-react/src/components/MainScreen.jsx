import React, { useState, useEffect, useContext, useRef } from "react";
import Sidebar from "./Sidebar";
import ProductCatalog from "./ProductCatalog";
import Cart from "./Cart";
import Header from "./Header";
import Footer from "./Footer";
import { fetchCategoriesAndProducts, getGuestCustomer, getItemByScan } from "../modules/LandingPage";
import { Button, Spin, Modal, notification } from "antd";
import { ShoppingCartOutlined, DoubleRightOutlined } from "@ant-design/icons";
import useIsSmallScreen from "../hooks/useIsSmallScreen";
import { CartContext } from "../common/CartContext";
import ProductPopup from './ProductPopup';

const MainScreen = () => {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [popupProduct, setPopupProduct] = useState(null);
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isCartVisible, setIsCartVisible] = useState(false);
  const [isSidebarVisible, setIsSidebarVisible] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [barcode, setBarcode] = useState("");
  const lastKeyPressTime = useRef(0);
  const [ currencySymbol, setCurrenySymbol ] = useState("")

  const isSmallScreen = useIsSmallScreen();
  const costCenter = localStorage.getItem("costCenter");

  const { addItemToCart } = useContext(CartContext);
  const searchInputRef = useRef(null);
  const scanTimeout = useRef(null);
  const [NotFound,setNotFound]=useState(false);

  const getSelectedCustomer = () => {
    const customer = localStorage.getItem("selectedCustomer");
    return customer ? JSON.parse(customer) : null;
  };

  const handleGetGuestCustomer = async () => {
    try {
      const res = await getGuestCustomer();
      if (res.status === 200) {
        console.log(res.data.message.data.currency_symbol)
        setCurrenySymbol(res.data.message.data.currency_symbol)
      } else {
        console.log("Error in getting the Guest Customer");
      }
    } catch (error) {
      console.log("Error in fetching guest customer:", error.message);
    }
  };

  useEffect(() => {
    handleGetGuestCustomer();
  }, []);

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

    if(!query){
      setNotFound(false)
    }
    
    setSearchQuery(query);
    if (query) {
      const results = products.filter(
        (product) =>
          product.name.toLowerCase().includes(query.toLowerCase()) ||
          product.category.toLowerCase().includes(query.toLowerCase())
      );
      setSearchResults(results);
      if(results.length===0){
        setNotFound(true)
      }else{
        setNotFound(false)
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
    return barcode.replace(/\D/g, '');
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
        const items = res.data.message[0].items;
        items.forEach((item) => {
          if (item.stock_qty > 0) {
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
      if(error instanceof TypeError){
        Modal.warning({
          title: "Item Not Found",
        });
      } else{
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
      : NotFound ? [] : products.filter((product) => product.category === selectedCategory);

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
              currency={currencySymbol}
            />
          </div>
          <Footer />
        </div>
        <div className={`cart-container ${isCartVisible ? "cart-visible" : ""}`}>
          <Cart />
        </div>
        <Button
          className="cart-button"
          onClick={() => setIsCartVisible(!isCartVisible)}
          icon={<ShoppingCartOutlined />}
        />
        {popupProduct && (
          <ProductPopup
            product={popupProduct}
            currency={currencySymbol}
            onAddItem={(item) => {
              addItemToCart(item);
              setPopupProduct(null);
            }}
            onClose={() => setPopupProduct(null)}
          />
        )}
      </div>
    </>
  );
};

export default MainScreen;
