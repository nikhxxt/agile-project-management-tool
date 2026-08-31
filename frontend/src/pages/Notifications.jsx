import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function Notifications() {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const load = useCallback(async () => {
    try { const response = await api.get("/notifications"); setNotifications(response.data); setError(""); }
    catch (err) { setError(err.response?.data?.detail || "Failed to load notifications"); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => {
    const request = window.setTimeout(() => { void load(); }, 0);
    return () => window.clearTimeout(request);
  }, [load]);
  const openNotification = async (taskId) => {
    try { const task = (await api.get(`/tasks/${taskId}`)).data; const story = (await api.get(`/stories/${task.user_story_id}`)).data; navigate(`/projects/${story.project_id}`); }
    catch (err) { setError(err.response?.data?.detail || "Unable to open the related project"); }
  };
  const deleteNotification = async (event, id) => {
    event.stopPropagation();
    try { await api.delete(`/notifications/${id}`); setNotifications((current) => current.filter((notification) => notification.id !== id)); }
    catch (err) { setError(err.response?.data?.detail || "Failed to delete notification"); }
  };
  return <div className="page"><header className="page-header"><div><p className="eyebrow">Inbox</p><h1>Notifications</h1><p className="page-subtitle">Assignment updates available to you in one calm place.</p></div></header>{error && <p className="notice">{error}</p>}{loading ? <div className="loading-state">Loading notifications…</div> : notifications.length === 0 ? <div className="empty-state">You're all caught up. No notifications yet.</div> : <section className="notifications-list">{notifications.map((notification) => <div className="card notification-card" key={notification.id}><div className="notification-body" onClick={() => openNotification(notification.task_id)} style={{ cursor: "pointer", flex: 1 }}><span className="notification-dot" /><div><h3>{notification.message}</h3><p>Task #{notification.task_id} · Open related project</p><div className="meta"><span className="badge">{notification.status}</span><span className="badge">{notification.retry_count} attempts</span><small>{new Date(notification.created_at).toLocaleString()}</small></div></div></div><button className="icon-btn" onClick={(event) => deleteNotification(event, notification.id)} title="Delete notification">Delete</button></div>)}</section>}</div>;
}

export default Notifications;
