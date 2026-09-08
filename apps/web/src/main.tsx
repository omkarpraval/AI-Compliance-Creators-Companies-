import React from "react";
import ReactDOM from "react-dom/client";
import { AuthProvider } from "./lib/auth";
import { AppRouter } from "./router";
import "./styles/tokens.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  </React.StrictMode>
);
