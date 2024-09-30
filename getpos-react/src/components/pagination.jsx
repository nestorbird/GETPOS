import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

const Pagination = ({ totalItems, currentPage, onPageChange, itemsPerPage }) => {
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const [currPage, setCurrPage] = useState(currentPage);

  useEffect(() => {
    setCurrPage(currentPage); // Sync with parent if `currentPage` prop changes
  }, [currentPage]);

  const handlePagesDecrement = () => {
    if (currPage === 1) return;
    const newPage = currPage - 1;
    setCurrPage(newPage);
    onPageChange(newPage);
  };

  const handlePagesIncrement = () => {
    if (currPage === totalPages) return;
    const newPage = currPage + 1;
    setCurrPage(newPage);
    onPageChange(newPage);
  };

  return (
    <>
    {console.log("totalPages",totalPages)}
    <div className="pagination">
      <button
        className="prev"
        onClick={handlePagesDecrement}
        disabled={currPage === 1}
      >
        Previous
      </button>
      <div className="page-number">{currPage}</div>
      <button
        className="next"
        onClick={handlePagesIncrement}
        disabled={currPage === totalPages || totalPages===0}
      >
        Next
      </button>
    </div>
    </>
  );
};

Pagination.propTypes = {
  totalItems: PropTypes.number.isRequired,
  currentPage: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
  itemsPerPage: PropTypes.number.isRequired,
};

export default Pagination;
