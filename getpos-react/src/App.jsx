import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";
import AppRoutes from "./routes";
import "./App.css";
import { FrappeProvider } from "frappe-react-sdk";
function App() {
  return (
	<div className="App">
	  <FrappeProvider>
    <AppRoutes />
	  </FrappeProvider>
	</div>
  )
}

export default App
