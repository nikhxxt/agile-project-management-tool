import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const update = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  const submit = async (event) => {
    event.preventDefault(); setLoading(true); setError("");
    try { await api.post("/auth/register", form); navigate("/login", { replace: true, state: { message: "Account created. Please sign in." } }); }
    catch (err) { setError(err.response?.data?.detail || "Unable to create your account"); }
    finally { setLoading(false); }
  };
  return <div className="login-page"><div className="login-card"><p className="eyebrow">Agile project management</p><h1>Create account</h1><p className="login-subtitle">Join AgileFlow and start organizing work.</p><form onSubmit={submit}><label htmlFor="name">Name</label><input id="name" name="name" value={form.name} onChange={update} minLength="2" required /><label htmlFor="email">Email</label><input id="email" name="email" type="email" value={form.email} onChange={update} required /><label htmlFor="password">Password</label><input id="password" name="password" type="password" value={form.password} onChange={update} minLength="6" required />{error && <div className="error-message">{error}</div>}<button type="submit" className="btn btn-primary" disabled={loading}>{loading ? "Creating account..." : "Create account"}</button></form><p className="login-subtitle login-link">Already have an account? <Link to="/login">Sign in</Link></p></div></div>;
}

export default Register;
