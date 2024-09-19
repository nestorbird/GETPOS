import React from "react";
import { Drawer } from "antd";

const Sidebar = ({ categories, onSelectCategory, selectedCategory, isVisible, onClose, isSmallScreen }) => {
  const sidebarContent = (
    <div className="sidebar">
      <ul>
        {categories.length > 0 ? (
          categories.map((category) => (
            <li
              key={category.item_group}
              onClick={() => onSelectCategory(category.item_group)}
              className={selectedCategory === category.item_group ? "active" : ""}
            >
              {category.item_group}
            </li>
          ))
        ) : (
          <li>No categories available</li>
        )}
      </ul>
    </div>
    
  );

  return isSmallScreen ? (
    <Drawer
      title="Categories"
      placement="left"
      closable={true}
      onClose={onClose}
      visible={isVisible}
      bodyStyle={{ padding: 0 }}
    >
      {sidebarContent}
    </Drawer>
  ) : (
    <>{sidebarContent}</>
  );
};

export default Sidebar;
