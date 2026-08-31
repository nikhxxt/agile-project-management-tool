import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function Notifications() {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = () => {
    setLoading(true);
    api.get("/notifications")
      .then(({ data }) => setNotifications(data))
      .catch(err => setError(err.response?.data?.detail || "Failed to load notifications"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const openNotification = async (taskId) => {
    try {
      setError("");
      const task = (await api.get(`/tasks/${taskId}`)).data;
      const story = (await api.get(`/stories/${task.user_story_id}`)).data;
      navigate(`/projects/${story.project_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to open the related project");
    }
  };

  const deleteNotification = async (e, id) => {
    e.stopPropagation();
    try {
      await api.delete(`/notifications/${id}`);
      setNotifications(prev => prev.filter(n => n.id !== id));
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete notification");
    }
  };

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Inbox</p>
          <h1>Notifications</h1>
          <p className="page-subtitle">The updates that need your attention, all in one calm place.</p>
        </div>
      </header>

      {error && <p className="notice">{error}</p>}

      {loading ? (
        <div className="loading-state">Loading notifications…</div>
      ) : notifications.length === 0 ? (
        <div className="empty-state">You're all caught up. No notifications yet.</div>
      ) : (
        <section className="notifications-list">
          {notifications.map(n => (
            <div className="card notification-card" key={n.id}>
              <div className="notification-body" onClick={() => openNotification(n.task_id)} style={{ cursor: "pointer", flex: 1 }}>
                <span className="notification-dot" />
                <div>
                  <h3>{n.message}</h3>
                  <p>Task #{n.task_id} · Open related project</p>
                  <div className="meta">
                    <span className="badge">{n.status}</span>
                    <span className="badge">{n.retry_count} retries</span>
                    <small>{new Date(n.created_at).toLocaleString()}</small>
                  </div>
                </div>
              </div>
              <button
                className="icon-btn"
                onClick={e => deleteNotification(e, n.id)}
                title="Delete notification"
              >
                Delete
              </button>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}

export default Notifications;
