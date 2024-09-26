import { Modal } from "antd";
import axios from "axios";
import { createBrowserHistory } from "history";
import Cookies from "js-cookie";
const CustomIcon = <span style={{ fontSize: '48px' }}>💀</span>;
const axiosInstance = axios.create({
  headers: {
    "Content-Type": "application/json",
    "X-Frappe-CSRF-Token": window.csrf_token || '', // Include CSRF token here
  },
});
const history = createBrowserHistory();
axiosInstance.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.data) {
      const { exc_type, exception } = error.response.data;
      if (exc_type === "PermissionError") {
        handleGuestUser();
      }
      else if (exc_type === "ValidationError") {
        handleGuestUser();
      }else if (exception && exception.includes("User None is disabled. Please contact your System Manager.")) {
        handleGuestUser();
      }
      else if (error.message === "Network Error" || error.message === "Request failed with status code 500") {
        Modal.warning({
          title: "Please check your network connection.",
          icon: CustomIcon,
          onOk: () => {
            window.location.reload();
          }
        });
      }
    }
    return Promise.reject(error);
  }
);
const handleGuestUser = () => {
  const userId = Cookies.get('user_id');
  // if (userId === 'Guest') {
    Cookies.remove('sid');
    Cookies.remove('system_user');
    Cookies.remove('user_id');
    Cookies.remove('user_image');
    localStorage.removeItem("user");
    localStorage.removeItem("sid");
    localStorage.removeItem("api_key");
    localStorage.removeItem("api_secret");
    if (window.location.pathname !== '/') {
      history.push('/');
      window.location.reload();
    } else {
      history.push('/');
    }
  // }
};
export default axiosInstance;