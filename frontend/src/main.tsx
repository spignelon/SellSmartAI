import React from "react";
import ReactDOM from "react-dom/client";
import { ClerkProvider } from "@clerk/clerk-react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"; 
import HomePage from "./pages/HomePage.tsx";
import Dashboard from "./pages/Dashboard.tsx";
import LinkSocialMedia from "./pages/LinkSocialMedia.tsx";
import PrivateRoute from "./PrivateRoute"; 
import "./index.css";

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!PUBLISHABLE_KEY) {
  throw new Error("Missing Publishable Key");
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} /> 
          <Route path="/dashboard" element={<PrivateRoute element={<Dashboard />} />} />  
          <Route path="/linksocialmedia" element={<PrivateRoute element={<LinkSocialMedia />} />} />
        </Routes>
      </Router>
    </ClerkProvider>
  </React.StrictMode>
);
