import NoImage from "../assets/images/no-img.png";

export const getImageUrl = (imagePath) => {
  const baseUrl = "https://getposdev.frappe.cloud";
  return imagePath ? `${baseUrl}${imagePath}` : NoImage;
};

