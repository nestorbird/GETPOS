import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { FrappeProvider } from "frappe-react-sdk";
import App from "./App";

import { CartProvider } from "./common/CartContext";

createRoot(document.getElementById('root')).render(
  <>
    <FrappeProvider>
  <CartProvider>
      <App />
    </CartProvider>  
    </FrappeProvider> 
  </>,
)
