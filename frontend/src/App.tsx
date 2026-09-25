/** Root component: wires global auth state and client-side routing. */

import { BrowserRouter } from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";
import AppRouter from "./router";
import CustomCursor from "./components/common/CustomCursor";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <CustomCursor />
        <AppRouter />
      </BrowserRouter>
    </AuthProvider>
  );
}