import React, { useState, useEffect, useContext } from "react";
import { Modal, Spin, Tabs } from "antd";
import Layout from "../components/Layout";
import OrderBox from "../components/OrderBox";
import SearchIcon from "../assets/images/icon-search.png";
import {
  fetchCategoriesAndProducts,
  fetchSalesOrderList,
  fetchSearchSalesOrderList,
} from "../modules/LandingPage";
import OrderDetailModal from "../components/OrderDetailModal";
import { CartContext } from "../common/CartContext";
import Pagination from "../components/pagination";
import { useNavigate } from "react-router-dom";
const { TabPane } = Tabs;
const OrderPage = ({ hubManagerEmail }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [currentPageParked, setCurrentPageParked] = useState(1);
  const [currentPageComplete, setCurrentPageComplete] = useState(1);
  const navigate = useNavigate();
  const itemsPerPage = 6;
  const { cartItems, setCartItems } = useContext(CartContext);
  const [PageCount, setPageCount] = useState(1);
  const [Data, setData] = useState([]);
  const GetSalesOrderList = async (PageCount) => {
    try {
      const { email } = JSON.parse(localStorage.getItem("user"));
      const orderList = await fetchSalesOrderList(email, PageCount);
      setData(orderList);
      setLoading(false);
    } catch (error) {
      console.log("Error occur", error);
      setLoading(false);
    }
  };
  useEffect(() => {
    GetSalesOrderList(PageCount);
  }, [PageCount, hubManagerEmail]);
  // const handleCompletePageChange = (pageNumber) => {
  //   setCurrentPageComplete(pageNumber);
  // };
  const handleParkedPageChange = (pageNumber) => {
    setCurrentPageParked(pageNumber);
  };

  useEffect(() => {
    const { email } = JSON.parse(localStorage.getItem("user"));
    fetchSearchSalesOrderList(email, searchTerm).then((res) => {
      setData(res);
    });
  }, [searchTerm]);

  const fetchParkedOrders = () => {
    const parkedOrders = JSON.parse(localStorage.getItem("parkedOrders")) || [];
    return parkedOrders.map((order) => ({
      ...order,
      customer_name: order.customer_name || "Guest",
      contact_mobile: order.contact_mobile || "N/A",
    }));
  };
  const fetchOrders = async (pageNoParked = 1, pageNoComplete = 1) => {
    try {
      // const { email } = JSON.parse(localStorage.getItem("user"));
      // const orderList = await fetchSalesOrderList(email, pageNoComplete);
      const parkedOrders = fetchParkedOrders();
      setOrders([...parkedOrders]);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching orders:", error);
      setLoading(false);
    }
  };
  useEffect(() => {
    fetchOrders();
  }, [hubManagerEmail, currentPageParked]);
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
    setCurrentPageParked(1); // Reset to the first page when searching
    setCurrentPageComplete(1); // Reset to the first page when searching
  };
  const handleOrderClick = (order) => {
    setSelectedOrder(order);
    setIsModalVisible(true);
  };
  const handleModalClose = () => {
    setIsModalVisible(false);
    setSelectedOrder(null);
  };
  const ProductAPICall = async () => {
    try {
      const data = await fetchCategoriesAndProducts();      
      return data;
    } catch (error) {
      console.error("Error fetching data in OrderPage", error);
    }
  };
  const SearchItem = (APIData, ParkData) => {
    let OutofStockItem = {};
    const apiItems = {};
    APIData.forEach((group) => {
      group.items.forEach((item) => {
        apiItems[item.id] = item;
      });
    });
    ParkData.items.forEach((parkItem) => {
      const apiItem = apiItems[parkItem.id];
      if (apiItem) {
        if (apiItem.stock_qty < parkItem.quantity) {
          OutofStockItem[parkItem.name] = apiItem.stock_qty;
        }
      }
    });
    return OutofStockItem;
  };
  const showAlert = (obj) => {
    let message = "Out of Stock ";
    for (let key in obj) {
      if (obj.hasOwnProperty(key)) {
        message += `${key} : ${obj[key]}\n`;
      }
    }
    return message;
  };
  const isEmpty = (object) => {
    return Object.entries(object).length === 0;
  };
  const moveOrderToCart = async (order) => {
    try {
      const data = await ProductAPICall();
      const found = SearchItem(data, order);
      if (isEmpty(found)) {
        // Remove the order from parked orders
        const updatedParkedOrders = fetchParkedOrders().filter(
          (o) => o.name !== order.name
        );
        localStorage.setItem(
          "parkedOrders",
          JSON.stringify(updatedParkedOrders)
        );
        // Update the orders state to remove the moved order
        const updatedOrders = orders.filter((o) => o.name !== order.name);
        setOrders(updatedOrders);
        // Add the order items to cart items
        const newCartItems = [...cartItems, ...order.items];
        setCartItems(newCartItems);
        // Save cart items and selected customer to local storage
        navigate("/main");
        localStorage.setItem("cartItems", JSON.stringify(newCartItems));
        localStorage.setItem(
          "selectedCustomer",
          JSON.stringify(order.customer)
        );
      } else {
        const msg = showAlert(found);
        Modal.warning({
          title: msg,
        });
      }
    } catch (error) {
      console.log("error occur on OrderPage", error);
    }
  };
  const updateOrderStatus = (orderId, status) => {
    setOrders((prevOrders) =>
      prevOrders.map((order) =>
        order.name === orderId
          ? { ...order, return_order_status: status }
          : order
      )
    );
  };
  const handleDeleteOrder = (orderId) => {
    const updatedOrders = orders.filter((order) => order.name !== orderId);
    setOrders(updatedOrders);
    const parkedOrders = fetchParkedOrders().filter(
      (order) => order.name !== orderId
    );
    localStorage.setItem("parkedOrders", JSON.stringify(parkedOrders));
  };

  const filteredOrders = orders.filter((order) => {
    console.log(order);
    return (
      (order.customer_name &&
        order.customer_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (order.contact_mobile && order.contact_mobile.includes(searchTerm)) ||
      (order.contact_name &&
        order.contact_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (order.name && order.name.toString().includes(searchTerm))
    );
  });
  const categorizedOrders = {
    parked: filteredOrders.filter((order) => order.status === "cartItems"),
    complete: filteredOrders.filter((order) => order.status !== "cartItems"),
    failed: filteredOrders.filter(
      (order) => order.return_order_status === "Failed"
    ),
  };
  const startIndexParked = (currentPageParked - 1) * itemsPerPage;
  const currentParkedOrders = categorizedOrders.parked.slice(
    startIndexParked,
    startIndexParked + itemsPerPage
  );
  // const startIndexComplete = (currentPageComplete - 1) * itemsPerPage;
  // const currentCompleteOrders = categorizedOrders.complete.slice(
  //   startIndexComplete,
  //   startIndexComplete + itemsPerPage
  // );
  if (loading) {
    return (
      <div className="loading-spin">
        <Spin tip="Loading..."></Spin>
      </div>
    );
  }
  const handlePrevBtn = async () => {
    setPageCount((prev) => prev - 1);
  };
  const handleNextBtn = async () => {
    setPageCount((prev) => prev + 1);
  };
  // console.log("Data",Data);
  return (
    <Layout>
      <div className="main-cont order-page">
        <div className="heading-cont">
          <h1>Orders</h1>
          <div className="searchField">
            <input
              type="text"
              placeholder="Search customer name"
              value={searchTerm}
              onChange={handleSearchChange}
              className="order-search"
            />
            <button>
              <img src={SearchIcon} alt="Search" />
            </button>
          </div>
        </div>
        <Tabs defaultActiveKey="1">
          <TabPane tab={<span className="tab-parked">Parked</span>} key="1">
            <div className="tab-inner-cont content-parked">
              {console.log("currentParkedOrders",currentParkedOrders)}
              {categorizedOrders.parked.length === 0 ? (
                <div className="no-data">No Parked order</div>
              ) : (
                
                currentParkedOrders.map((order, index) => (
                <>
                  <OrderBox
                    key={index}
                    order={order}
                    showPayNow={false}
                    showDelete={true}
                    showMoveToCart={false}
                    onClick={() => moveOrderToCart(order)}
                    onDelete={() => handleDeleteOrder(order.name)}
                    indicator={false}
                  />
                </>
                ))
              )}
            </div>
            {categorizedOrders.parked.length > 0  ?
            <Pagination
            totalItems={categorizedOrders.parked.length}
            itemsPerPage={itemsPerPage}
            currentPage={currentPageParked}
            onPageChange={handleParkedPageChange}

          />  
          :""
          
          }
            
          </TabPane>
          <TabPane tab={<span className="tab-failed">Failed</span>} key="2">
            <div className="tab-inner-cont content-failed">
              {categorizedOrders.failed.length === 0 ? (
                <div className="no-data">No Failed order</div>
              ) : (
                categorizedOrders.failed.map((order, index) => (
                  <OrderBox
                    key={index}
                    order={order}
                    showPayNow={false}
                    showDelete={true}
                    showMoveToCart={false}
                    onClick={handleOrderClick}
                    indicator={false}
                  />
                ))
              )}
            </div>
          </TabPane>
          <TabPane tab={<span className="tab-complete">Complete</span>} key="3">
            <div className="tab-inner-cont content-complete">
            {console.log("Data",Data)}
              {!Data || Data?.length === 0 ? (
                <div className="no-data">No Complete order</div>
              ) : (
                Data?.map((order, index) => (
                  <OrderBox
                    key={index}
                    order={order}
                    showPayNow={false}
                    showDelete={false}
                    showMoveToCart={false}
                    onClick={handleOrderClick}
                    indicator={true}
                  />
                ))
              )}
            </div>
            <div className="pagination">
              <button
                className="prev"
                onClick={handlePrevBtn}
                disabled={PageCount === 1}
              >
                Previous
              </button>
              <div className="page-number">{PageCount}</div>
              <button
                className="next"
                onClick={handleNextBtn}
                disabled={Data?.length === 0||Math.ceil(Data[0].total_order/Data[0].items_perpage)===PageCount}
              >
                Next
              </button>
            </div>
          </TabPane>
        </Tabs>
      </div>
      <OrderDetailModal
        visible={isModalVisible}
        onClose={handleModalClose}
        order={selectedOrder}
        onUpdateOrder={updateOrderStatus}
      />
    </Layout>
  );
};
export default OrderPage;
