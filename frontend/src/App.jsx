import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  NavLink,
} from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Projects from "./pages/Projects";
import ProjectDetails from "./pages/ProjectDetails";
import Notifications from "./pages/Notifications";

function ProtectedRoute({ children }) {
  return localStorage.getItem("token") ? (
    <AppLayout>{children}</AppLayout>
  ) : (
    <Navigate to="/login" replace />
  );
}

function AppLayout({ children }) {
  const logout = () => {
    localStorage.removeItem("token");
    window.location.assign("/login");
  };

  const links = [
    ["/dashboard", "▦", "Overview"],
    ["/projects", "◇", "Projects"],
    ["/notifications", "●", "Notifications"],
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">A</span> AgileFlow</div>
        <nav>{links.map(([to, icon, label]) => (
          <NavLink key={to} to={to} className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
            <span className="nav-icon">{icon}</span><span>{label}</span>
          </NavLink>
        ))}</nav>
        <div className="sidebar-foot">WORKSPACE<br /><button onClick={logout}>Sign out</button></div>
      </aside>
      <main className="app-main">{children}</main>
    </div>
  );
}

function RootRedirect() {
  return (
    <Navigate
      to={localStorage.getItem("token") ? "/dashboard" : "/login"}
      replace
    />
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={<Login />}
        />
        <Route path="/register" element={<Register />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/projects"
          element={
            <ProtectedRoute>
              <Projects />
            </ProtectedRoute>
          }
        />

        <Route
          path="/projects/:projectId"
          element={
            <ProtectedRoute>
              <ProjectDetails />
            </ProtectedRoute>
          }
        />

        <Route
          path="/notifications"
          element={
            <ProtectedRoute>
              <Notifications />
            </ProtectedRoute>
          }
        />

        <Route
          path="*"
          element={<RootRedirect />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
