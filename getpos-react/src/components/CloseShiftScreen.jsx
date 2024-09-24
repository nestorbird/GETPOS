import React, { useState, useEffect, useContext } from "react";
import Layout from "./Layout";
import { getCloseShiftDetails, getClosingShift } from "../modules/LandingPage";
import { useNavigate } from "react-router-dom";
import { CartContext } from "../common/CartContext";
import { useThemeSettings } from "./ThemeSettingContext";

const CloseShiftScreen = () => {
  const [openShift, setOpenShift] = useState({});
  const [expectedCashBalance, setExpectedCashBalance] = useState("");
  // const [expectedDigitalBalance, setExpectedDigitalBalance] = useState("");
  const [cashBalance, setCashBalance] = useState("");
  const [digitalBalance, setDigitalBalance] = useState("");
  const [showCashInput, setShowCashInput] = useState(false);
  const [showDigitalInput, setShowDigitalInput] = useState(false);
  const [totalSalesOrderAmount, setTotalSalesOrderAmount] = useState(0);
  const navigate = useNavigate();
  const { cartItems, setCartItems } = useContext(CartContext);
  const themeSettings = useThemeSettings();

  // Fetch and update openShift data from local storage
  const fetchOpenShiftData = () => {
    const OpenShiftDetails = JSON.parse(
      localStorage.getItem("openingShiftResponse")
    );

    if (OpenShiftDetails) {
      setOpenShift(OpenShiftDetails.message.pos_opening_shift);
    } else {
      console.error("Opening shift data is not available or is invalid.");
    }
  };

  useEffect(() => {
    fetchOpenShiftData();
  }, []);

  const closeShiftDetails = async () => {
    if (!openShift.name) {
      console.error("OpenShift data is not set properly.");
      return;
    }

    const payload = {
      opening_shift: {
        name: openShift.name,
        period_start_date: openShift.period_start_date,
        status: openShift.status,
        pos_profile: openShift.pos_profile,
        set_posting_date: 0,
        company: openShift.company,
        doctype: openShift.doctype,
        balance_details: openShift.balance_details.map((detail) => ({
          mode_of_payment: detail.mode_of_payment,
          amount: detail.amount,
        })),
        period_end_date: openShift.period_start_date,
      },
    };

    try {
      const res = await getCloseShiftDetails(payload);
      const shiftDetail = res.data.message.Shift_Detail[0] || {};

      const openingBalances = res.data.message.opening_balance;
      const cashOpeningDetail = openingBalances.find(
        (detail) => detail.mode_of_payment === "Cash"
      );
      const creditCardOpeningDetail = openingBalances.find(
        (detail) => detail.mode_of_payment === "Credit Card"
      );

      const totalSalesOrderAmount = shiftDetail.total_sales_order_amount || 0;
      setTotalSalesOrderAmount(totalSalesOrderAmount);

      const expectedCashAmount =
        (cashOpeningDetail ? cashOpeningDetail.amount : 0) +
        totalSalesOrderAmount;

      // const expectedCreditCardAmount =
      //   (creditCardOpeningDetail ? creditCardOpeningDetail.amount : 0) + totalSalesOrderAmount;

      setExpectedCashBalance(expectedCashAmount.toFixed(2));
      // setExpectedDigitalBalance(expectedCreditCardAmount.toFixed(2));

      setCashBalance("");
      setDigitalBalance("");

      setShowCashInput(!!cashOpeningDetail);
      setShowDigitalInput(!!creditCardOpeningDetail);
    } catch (error) {
      console.error("Error fetching close shift details:", error);
    }
  };

  useEffect(() => {
    if (openShift.name) {
      closeShiftDetails();
    }
  }, [openShift]);

  // Handle Close Shift action
  const handleLogout = async () => {
    try {
      const openingShiftResponseStr = localStorage.getItem(
        "openingShiftResponse"
      );

      if (!openingShiftResponseStr) {
        console.error("No opening shift response found in local storage.");
        setTimeout(() => {
          localStorage.clear();
          navigate("/getpos-react");
          setCartItems([]);
        }, 1000);
        return;
      }

      const openingShiftResponse = JSON.parse(openingShiftResponseStr);

      if (
        !openingShiftResponse ||
        !openingShiftResponse.message ||
        !openingShiftResponse.message.pos_opening_shift ||
        openingShiftResponse.message.pos_opening_shift.status !== "Open"
      ) {
        console.error(
          "Invalid opening shift status or response:",
          openingShiftResponse
        );
        alert(
          "The selected POS Opening Shift is not open. Please select an open shift."
        );
        return;
      }

      const periodStartDate =
        openingShiftResponse.message.pos_opening_shift.period_start_date || "";

      const postingDate = new Date().toISOString();
      const periodEndDate = new Date().toISOString();

      // Log expected and entered balances for debugging
      console.log(
        "Expected Cash Balance:",
        expectedCashBalance,
        typeof expectedCashBalance
      );
      console.log("Entered Cash Balance:", cashBalance, typeof cashBalance);

      // console.log("Expected Digital Balance:", expectedDigitalBalance, typeof expectedDigitalBalance);
      console.log(
        "Entered Digital Balance:",
        digitalBalance,
        typeof digitalBalance
      );

      // Validate cash and digital balances
      if (
        parseFloat(cashBalance) !== parseFloat(expectedCashBalance)
        // parseFloat(digitalBalance) !== parseFloat(expectedDigitalBalance)
      ) {
        alert(
          "The entered balance do not match the expected amount. Please enter the exact amount."
        );
        return;
      }

      const paymentReconciliation = [];

      if (showCashInput) {
        paymentReconciliation.push({
          mode_of_payment: "Cash",
          opening_amount: parseFloat(expectedCashBalance) || 0.0,
          closing_amount: parseFloat(cashBalance) || 0.0,
          expected_amount: parseFloat(expectedCashBalance) || 0.0,
          difference: 0.0,
        });
      }

      if (showDigitalInput) {
        paymentReconciliation.push({
          mode_of_payment: "Credit Card",
          // opening_amount: parseFloat(expectedDigitalBalance) || 0.0,
          closing_amount: parseFloat(digitalBalance) || 0.0,
          // expected_amount: parseFloat(expectedDigitalBalance) || 0.0,
          difference: 0.0,
        });
      }

      const closingShiftData = {
        closing_shift: {
          period_start_date: formatDateString(periodStartDate),
          posting_date: formatDateString(postingDate),
          pos_profile: openingShiftResponse.message.pos_profile.name,
          pos_opening_shift:
            openingShiftResponse.message.pos_opening_shift.name,
          doctype: "POS Closing Shift",
          payment_reconciliation: paymentReconciliation,
          period_end_date: formatDateString(periodEndDate),
        },
      };

      const response = await getClosingShift(closingShiftData);

      if (response) {
        console.log("Shift closed successfully");
        navigate("/closeshift");
        setTimeout(() => {
          navigate("/getpos-react");
          setCartItems([]);
        }, 1000);
        localStorage.clear();
      } else {
        console.error("Failed to close shift");
      }
    } catch (error) {
      console.error("Error closing shift:", error);
      alert("Error closing shift: " + error.message);
    }
  };

  // Helper function to format date strings
  const formatDateString = (dateString) => {
    const dateObj = new Date(dateString);
    if (isNaN(dateObj.getTime())) {
      throw new Error("Invalid date");
    }
    const formattedDate = dateObj.toISOString().slice(0, 23).replace("T", " ");
    return formattedDate;
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault(); // Prevent default form submission
      handleLogout();
    }
  };

  const handleCashBalanceChange = (e) => {
    const value = parseFloat(e.target.value);
    const expectedBalance = parseFloat(expectedCashBalance); // Ensure it's a number
    if (value > expectedBalance) {
      alert(
        `The entered amount exceeds the expected cash balance of $${expectedBalance.toFixed(
          2
        )}. Please enter a valid amount.`
      );
      setCashBalance(expectedBalance.toString());
    } else {
      setCashBalance(e.target.value);
    }
  };

  // const handleDigitalBalanceChange = (e) => {
  //   const value = parseFloat(e.target.value);
  //   const expectedBalance = parseFloat(expectedDigitalBalance); // Ensure it's a number
  //   if (value > expectedBalance) {
  //     alert(
  //       `The entered amount exceeds the expected credit balance of $${expectedBalance.toFixed(
  //         2
  //       )}. Please enter a valid amount.`
  //     );
  //     setDigitalBalance(expectedBalance.toString());
  //   } else {
  //     setDigitalBalance(e.target.value);
  //   }
  // };

  console.log(expectedCashBalance, "pppppp");
  console.log(cashBalance);

  return (
    <Layout>
      <div className="login-screen">
        <h1>CLOSE SHIFT</h1>
        <form className="login-form" onKeyDown={handleKeyDown}>
          {showCashInput && (
            <div className="form-group">
              <input
                id="cash-balance"
                type="number"
                placeholder="Enter Closing Cash Balance"
                value={cashBalance}
                onChange={handleCashBalanceChange}
              />
              <span>
                System Closing Cash Balance:{" "}
                {themeSettings?.currency_symbol || "$"}
                {parseFloat(expectedCashBalance).toFixed(2)}
              </span>
            </div>
          )}
          {/* {showDigitalInput && (
            <div className="form-group">
              <input
                id="digital-balance"
                type="number"
                placeholder="Enter Closing Digital Balance"
                value={digitalBalance}
                onChange={handleDigitalBalanceChange}
              />
              <span>
                System Closing Digital Balance: $
                {parseFloat(expectedDigitalBalance).toFixed(2)}
              </span>
            </div>
          )} */}
          <div className="form-group">
            <button
              className="button-close-shift"
              type="button"
              onClick={handleLogout}
            >
              Close Shift
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
};

export default CloseShiftScreen;
