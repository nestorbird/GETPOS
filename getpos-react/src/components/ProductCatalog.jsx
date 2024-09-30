import React, { useState, useEffect } from "react";
import ProductCard from "./ProductCard";
import Pagination from "./pagination"; // Import the Pagination component

const ProductCatalog = ({ categoryName, products, onAddToCart }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [productsPerPage, setProductsPerPage] = useState(10);

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      if (width >= 1720) {
        setProductsPerPage(10);
      } else if (width >= 1430) {
        setProductsPerPage(8);
      } else if (width >= 1230) {
          setProductsPerPage(8);
        }
       else if (width >= 1150) {
        setProductsPerPage(6);
      } else {
        setProductsPerPage(4);
      }
    };

    window.addEventListener("resize", handleResize);
    handleResize(); // Set initial value based on current window size

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  // Calculate the indexes for slicing the products array
  const indexOfLastProduct = currentPage * productsPerPage;
  const indexOfFirstProduct = indexOfLastProduct - productsPerPage;
  const currentProducts = products.slice(indexOfFirstProduct, indexOfLastProduct);

  // Determine total number of pages
  const totalPages = Math.ceil(products.length / productsPerPage);

  // Function to handle page changes
  const handlePageChange = (direction) => {
    setCurrentPage((prevPage) => {
      if (direction === "next" && prevPage < totalPages) {
        return prevPage + 1;
      }
      if (direction === "prev" && prevPage > 1) {
        return prevPage - 1;
      }
      return prevPage;
    });
  };
  
  return (
    <div className="product-catalog">
      <h2>{categoryName}</h2>
      <div className="product-list">
        {currentProducts.length > 0 ? (
          currentProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onAddToCart={onAddToCart}
            />
          ))
        ) : (
          <p>No products available</p>
        )}
      </div>
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={handlePageChange}
      />
    </div>
  );
};

export default ProductCatalog;
