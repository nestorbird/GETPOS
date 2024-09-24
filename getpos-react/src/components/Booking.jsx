import React, { useState } from "react";
import { Table, Tabs } from "antd";
import Layout from "../components/Layout";

const { TabPane } = Tabs;

const upcomingBookingsData = [
  {
    key: "1",
    customerName: "John Doe",
    contactNo: "9876543210",
    tableNo: "5",
    guests: 3,
    dateTime: "2024-09-20 18:30",
    action: "Check in",
  },
  {
    key: "2",
    customerName: "Jane Smith",
    contactNo: "9876543211",
    tableNo: "3",
    guests: 2,
    dateTime: "2024-09-21 19:00",
    action: "Check in",
  },
  {
    key: "3",
    customerName: "Emily White",
    contactNo: "9876543214",
    tableNo: "6",
    guests: 4,
    dateTime: "2024-09-22 20:00",
    action: "Check in",
  },
  {
    key: "4",
    customerName: "Michael Black",
    contactNo: "9876543215",
    tableNo: "2",
    guests: 1,
    dateTime: "2024-09-23 21:00",
    action: "Check in",
  },
  {
    key: "5",
    customerName: "Sophia Johnson",
    contactNo: "9876543216",
    tableNo: "4",
    guests: 2,
    dateTime: "2024-09-24 19:30",
    action: "Check in",
  },
  {
    key: "6",
    customerName: "David Wilson",
    contactNo: "9876543217",
    tableNo: "8",
    guests: 3,
    dateTime: "2024-09-25 18:45",
    action: "Check in",
  },
];

const pastBookingsData = [
  {
    key: "1",
    customerName: "Alice Brown",
    contactNo: "9876543212",
    tableNo: "7",
    guests: 4,
    dateTime: "2024-08-20 18:00",
    action: "Check Out",
  },
  {
    key: "2",
    customerName: "Bob Green",
    contactNo: "9876543213",
    tableNo: "8",
    guests: 2,
    dateTime: "2024-08-22 20:00",
    action: "Check Out",
  },
  {
    key: "3",
    customerName: "Charlie Black",
    contactNo: "9876543218",
    tableNo: "9",
    guests: 5,
    dateTime: "2024-08-23 19:30",
    action: "Check Out",
  },
  {
    key: "4",
    customerName: "Diana Grey",
    contactNo: "9876543219",
    tableNo: "10",
    guests: 2,
    dateTime: "2024-08-24 21:00",
    action: "Check Out",
  },
  {
    key: "5",
    customerName: "Evelyn Blue",
    contactNo: "9876543220",
    tableNo: "11",
    guests: 3,
    dateTime: "2024-08-25 20:15",
    action: "Check Out",
  },
  {
    key: "6",
    customerName: "Frank Red",
    contactNo: "9876543221",
    tableNo: "12",
    guests: 1,
    dateTime: "2024-08-26 18:45",
    action: "Check Out",
  },
];

const Booking = () => {
  const [activeTab, setActiveTab] = useState("upcoming");

  const columns = [
    {
      title: "Customer Name",
      dataIndex: "customerName",
      key: "customerName",
      className: "booking-column",
    },
    {
      title: "Contact No.",
      dataIndex: "contactNo",
      key: "contactNo",
      className: "booking-column",
    },
    {
      title: "Table No.",
      dataIndex: "tableNo",
      key: "tableNo",
      className: "booking-column",
    },
    {
      title: "No. of Guests",
      dataIndex: "guests",
      key: "guests",
      className: "booking-column",
    },
    {
      title: "Date & Time",
      dataIndex: "dateTime",
      key: "dateTime",
      className: "booking-column",
    },
    {
      title: "Action",
      dataIndex: "action",
      key: "action",
      className: "booking-column",
      render: (text) => (
        <span
          className={
            text === "Check in" ? "booking-checkin" : "booking-checkout"
          }
        >
          {text}
        </span>
      ),
    },
  ];

  return (
    <Layout>
      <div className="booking-page">
        <h1 className="booking-title">ORDERS</h1>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          className="booking-tabs"
        >
          <TabPane tab="UPCOMING BOOKINGS" key="upcoming">
            <Table
              columns={columns}
              dataSource={upcomingBookingsData}
              pagination={false}
              className="booking-table"
            />
          </TabPane>
          <TabPane tab="PAST BOOKINGS" key="past">
            <Table
              columns={columns}
              dataSource={pastBookingsData}
              pagination={false}
              className="booking-table"
            />
          </TabPane>
        </Tabs>
      </div>
    </Layout>
  );
};

export default Booking;
