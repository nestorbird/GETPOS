import React from "react";
import PropTypes from "prop-types";

const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  return (
    <div className="pagination">
      <button
        className="prev"
        onClick={() => onPageChange("prev")}
        disabled={currentPage === 1}
      >
        Previous
      </button>
      <div className="page-number">{currentPage}</div>
      <button
        className="next"
        onClick={() => onPageChange("next")}
        disabled={currentPage === totalPages}
      >
        Next
      </button>
    </div>
  );
};

Pagination.propTypes = {
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
};

export default Pagination;
