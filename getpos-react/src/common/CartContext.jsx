import React, { createContext, useState, useEffect } from "react";

const CartContext = createContext();

const CartProvider = ({ children }) => {
  const [cartItems, setCartItems] = useState(() => {
    const storedCartItems = localStorage.getItem("cartItems");
    return storedCartItems ? JSON.parse(storedCartItems) : [];
  });

  const [originalPrices, setOriginalPrices] = useState(() => {
    const storedOriginalPrices = localStorage.getItem("originalPrices");
    return storedOriginalPrices ? JSON.parse(storedOriginalPrices) : {};
  });

  const [editedPrices, setEditedPrices] = useState({});
  const [lastAuthorizedPrices, setLastAuthorizedPrices] = useState({});
  const [storedPassword, setStoredPassword] = useState("");

  useEffect(() => {
    localStorage.setItem("cartItems", JSON.stringify(cartItems));
  }, [cartItems]);

  useEffect(() => {
    localStorage.setItem("originalPrices", JSON.stringify(originalPrices));
  }, [originalPrices]);

  const addItemToCart = (item) => {
    setCartItems((prevItems) => {
      const itemIndex = prevItems.findIndex((prevItem) => prevItem.id === item.id);

      if (itemIndex >= 0) {
        const updatedItems = [...prevItems];
        updatedItems[itemIndex].quantity += item.quantity;
        if (item.isScanned && !updatedItems[itemIndex].price) {
          updatedItems[itemIndex].price = item.price;
        }
        return updatedItems;
      } else {
        const newItem = {
          ...item,
          price: item.isScanned ? item.price : (item.price || 0),
        };

        setOriginalPrices((prevPrices) => {
          if (!prevPrices[item.id]) {
            return { ...prevPrices, [item.id]: item.product_price };
          }
          return prevPrices;
        });

        return [...prevItems, newItem];
      }
    });
  };

  const removeItemFromCart = (itemId) => {
    setCartItems((prevItems) => {
      const updatedItems = prevItems.filter((item) => item.id !== itemId);
      
      setOriginalPrices((prevPrices) => {
        const { [itemId]: _, ...rest } = prevPrices;
        return rest;
      });

      setEditedPrices((prevPrices) => {
        const { [itemId]: _, ...rest } = prevPrices;
        return rest;
      });

      setLastAuthorizedPrices((prevPrices) => {
        const { [itemId]: _, ...rest } = prevPrices;
        return rest;
      });

      return updatedItems;
    });
  };

  const resetCart = () => {
    setCartItems([]);
    setOriginalPrices({});
    setEditedPrices({});
    setLastAuthorizedPrices({});
  };

  const completeOrder = () => {
    setCartItems([]);
    setOriginalPrices({});
    setEditedPrices({});
    setLastAuthorizedPrices({});
  };

  return (
    <CartContext.Provider
      value={{
        cartItems,
        addItemToCart,
        removeItemFromCart,
        resetCart,
        completeOrder,
        setCartItems,
        setEditedPrices,
        setLastAuthorizedPrices,
        setStoredPassword,
      }}
    >
      {children}
    </CartContext.Provider>
  );
};

export { CartProvider, CartContext };
