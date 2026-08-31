import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

const Badge = ({ type, value }) => <span className={`badge ${type}-${String(value).toLowerCase()}`}>{String(value).replaceAll("_", " ")}</span>;
const initials = (name) => name?.split(" ").map((part) => part[0]).slice(0, 2).join("") || "?";
const dateValue = (value) => value || "";

function ProjectDetails() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [stories, setStories] = useState([]);
  const [tasks, setTasks] = useState({});
  const [members, setMembers] = useState([]);
  const [eligibleUsers, setEligibleUsers] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [storyForm, setStoryForm] = useState(null);
  const [taskForm, setTaskForm] = useState(null);
  const [memberId, setMemberId] = useState("");
  const [filters, setFilters] = useState({ status: "", priority: "", assignee: "" });
  const [storyDraft, setStoryDraft] = useState({ title: "", description: "", status: "BACKLOG", priority: "MEDIUM" });
  const [taskDraft, setTaskDraft] = useState({ title: "", description: "", priority: "MEDIUM", due_date: "" });

  const loadProject = useCallback(async () => {
    try {
      const [projectResponse, storyResponse] = await Promise.all([
        api.get(`/projects/${projectId}`), api.get(`/projects/${projectId}/stories`),
      ]);
      const [memberResult, eligibleResult, activityResult] = await Promise.allSettled([
        api.get(`/users/projects/${projectId}/members`),
        api.get(`/projects/${projectId}/eligible-users`),
        api.get(`/activity/projects/${projectId}`),
      ]);
      const taskPairs = await Promise.all(storyResponse.data.map(async (story) => [story.id, (await api.get(`/stories/${story.id}/tasks`)).data]));
      setProject(projectResponse.data); setStories(storyResponse.data);
      setMembers(memberResult.status === "fulfilled" ? memberResult.value.data : []);
      setEligibleUsers(eligibleResult.status === "fulfilled" ? eligibleResult.value.data : []);
      setActivities(activityResult.status === "fulfilled" ? activityResult.value.data : []);
      setTasks(Object.fromEntries(taskPairs)); setError("");
    } catch (err) { setError(err.response?.data?.detail || "Failed to load project"); }
    finally { setLoading(false); }
  }, [projectId]);

  useEffect(() => {
    const request = window.setTimeout(() => { void loadProject(); }, 0);
    return () => window.clearTimeout(request);
  }, [loadProject]);
  const refresh = async () => { setLoading(true); await loadProject(); };
  const resetStory = () => { setStoryForm(null); setStoryDraft({ title: "", description: "", status: "BACKLOG", priority: "MEDIUM" }); };
  const resetTask = () => { setTaskForm(null); setTaskDraft({ title: "", description: "", priority: "MEDIUM", due_date: "" }); };
  const saveStory = async (event) => {
    event.preventDefault(); setSaving(true);
    try { if (storyForm === "new") await api.post(`/projects/${projectId}/stories`, storyDraft); else await api.put(`/stories/${storyForm}`, storyDraft); resetStory(); await refresh(); }
    catch (err) { setError(err.response?.data?.detail || "Failed to save story"); }
    finally { setSaving(false); }
  };
  const saveTask = async (event) => {
    event.preventDefault(); setSaving(true);
    const data = { ...taskDraft, due_date: taskDraft.due_date || null };
    try { if (taskForm?.mode === "new") await api.post(`/stories/${taskForm.storyId}/tasks`, { ...data, status: "TODO", assigned_to: null }); else await api.put(`/tasks/${taskForm.taskId}`, data); resetTask(); await refresh(); }
    catch (err) { setError(err.response?.data?.detail || "Failed to save task"); }
    finally { setSaving(false); }
  };
  const updateTask = async (taskId, field, value) => {
    setSaving(true); try { await api.put(`/tasks/${taskId}`, { [field]: value }); await refresh(); }
    catch (err) { setError(err.response?.data?.detail || "Failed to update task"); }
    finally { setSaving(false); }
  };
  const deleteItem = async (path, text) => {
    if (!window.confirm(text)) return; setSaving(true);
    try { await api.delete(path); await refresh(); } catch (err) { setError(err.response?.data?.detail || "Failed to delete item"); } finally { setSaving(false); }
  };
  const addMember = async (event) => {
    event.preventDefault(); if (!memberId) return; setSaving(true);
    try { await api.post(`/users/${memberId}/projects/${projectId}`); setMemberId(""); await refresh(); }
    catch (err) { setError(err.response?.data?.detail || "Failed to add member"); } finally { setSaving(false); }
  };
  const removeMember = async (id) => {
    if (!window.confirm("Remove this member from the project?")) return; setSaving(true);
    try { await api.delete(`/users/${id}/projects/${projectId}`); await refresh(); }
    catch (err) { setError(err.response?.data?.detail || "Failed to remove member"); } finally { setSaving(false); }
  };
  const visibleTasks = (storyId) => (tasks[storyId] || []).filter((task) => (
    (!filters.status || task.status === filters.status)
    && (!filters.priority || task.priority === filters.priority)
    && (!filters.assignee || (filters.assignee === "unassigned"
      ? task.assigned_to === null
      : task.assigned_to === Number(filters.assignee)))
  ));

  if (loading) return <div className="page loading-state">Loading project workspace…</div>;
  if (!project) return <div className="page"><p className="notice">{error || "Project not found."}</p><button className="btn" onClick={() => navigate("/projects")}>Back to projects</button></div>;
  const availableUsers = eligibleUsers.filter((user) => !members.some((member) => member.id === user.id));
  return <div className="page"><button className="btn btn-quiet" onClick={() => navigate("/projects")}>← All projects</button><header className="card detail-header"><p className="eyebrow">Project #{project.id}</p><div className="section-heading"><div><h1>{project.name}</h1><p className="page-subtitle">{project.description || "No project description yet."}</p></div><Badge type="status" value={project.status} /></div></header>{error && <p className="notice">{error}</p>}<div className="detail-layout"><main className="detail-main"><section className="card section-card"><div className="section-heading"><div><p className="eyebrow">Delivery plan</p><h2>Stories & tasks</h2></div><button className="btn btn-primary" onClick={() => { setStoryForm("new"); setStoryDraft({ title: "", description: "", status: "BACKLOG", priority: "MEDIUM" }); }}>+ New story</button></div>{storyForm && <form className="inline-form form-grid" onSubmit={saveStory}><input placeholder="Story title" value={storyDraft.title} onChange={(event) => setStoryDraft({ ...storyDraft, title: event.target.value })} required /><textarea placeholder="Describe the outcome…" value={storyDraft.description} onChange={(event) => setStoryDraft({ ...storyDraft, description: event.target.value })} /><div className="form-row"><select value={storyDraft.status} onChange={(event) => setStoryDraft({ ...storyDraft, status: event.target.value })}><option value="BACKLOG">BACKLOG</option><option value="IN_PROGRESS">IN PROGRESS</option><option value="DONE">DONE</option></select><select value={storyDraft.priority} onChange={(event) => setStoryDraft({ ...storyDraft, priority: event.target.value })}><option value="LOW">LOW</option><option value="MEDIUM">MEDIUM</option><option value="HIGH">HIGH</option></select></div><div className="form-actions"><button className="btn btn-primary" disabled={saving}>Save story</button><button className="btn btn-quiet" type="button" onClick={resetStory}>Cancel</button></div></form>}<div className="filters"><select value={filters.status} onChange={(event) => setFilters({ ...filters, status: event.target.value })}><option value="">All statuses</option><option value="TODO">To do</option><option value="IN_PROGRESS">In progress</option><option value="DONE">Done</option></select><select value={filters.priority} onChange={(event) => setFilters({ ...filters, priority: event.target.value })}><option value="">All priorities</option><option value="LOW">Low</option><option value="MEDIUM">Medium</option><option value="HIGH">High</option></select><select value={filters.assignee} onChange={(event) => setFilters({ ...filters, assignee: event.target.value })}><option value="">All assignees</option><option value="unassigned">Unassigned</option>{members.map((member) => <option key={member.id} value={member.id}>{member.name}</option>)}</select><button className="btn btn-quiet" onClick={() => setFilters({ status: "", priority: "", assignee: "" })}>Clear</button></div></section>{stories.map((story) => <article className="story-card" key={story.id}><div className="story-head"><div><div className="header-meta"><Badge type="status" value={story.status} /><Badge type="priority" value={story.priority} /></div><h3 className="story-title">{story.title}</h3><p className="story-desc">{story.description || "No story description."}</p></div><div className="story-actions"><button className="icon-btn" onClick={() => { setStoryForm(story.id); setStoryDraft({ title: story.title, description: story.description || "", status: story.status, priority: story.priority }); }}>Edit</button><button className="icon-btn" onClick={() => deleteItem(`/stories/${story.id}`, "Delete this story and its tasks?")}>Delete</button></div></div><div className="task-list"><div className="section-heading"><h4>Tasks · {(tasks[story.id] || []).length}</h4><button className="icon-btn" onClick={() => { setTaskForm({ mode: "new", storyId: story.id }); setTaskDraft({ title: "", description: "", priority: "MEDIUM", due_date: "" }); }}>+ Task</button></div>{taskForm?.mode === "new" && taskForm.storyId === story.id && <TaskForm draft={taskDraft} setDraft={setTaskDraft} saving={saving} onSubmit={saveTask} onCancel={resetTask} />}{visibleTasks(story.id).map((task) => <div className="task-row" key={task.id}>{taskForm?.mode === "edit" && taskForm.taskId === task.id ? <TaskForm draft={taskDraft} setDraft={setTaskDraft} saving={saving} onSubmit={saveTask} onCancel={resetTask} /> : <><div><div className="task-name">{task.title}</div><div className="task-desc">{task.description || "No details"}{task.due_date && ` · Due ${new Date(`${task.due_date}T00:00:00`).toLocaleDateString()}`}</div></div><select className="assignee-select" value={task.status} disabled={saving} onChange={(event) => updateTask(task.id, "status", event.target.value)}><option value="TODO">To do</option><option value="IN_PROGRESS">In progress</option><option value="DONE">Done</option></select><Badge type="priority" value={task.priority} /><select className="assignee-select" value={task.assigned_to ?? ""} disabled={saving} onChange={(event) => updateTask(task.id, "assigned_to", event.target.value === "" ? null : Number(event.target.value))}><option value="">Unassigned</option>{members.map((member) => <option key={member.id} value={member.id}>{member.name}</option>)}</select><div className="story-actions"><button className="icon-btn" onClick={() => { setTaskForm({ mode: "edit", taskId: task.id }); setTaskDraft({ title: task.title, description: task.description || "", priority: task.priority, due_date: dateValue(task.due_date) }); }}>Edit</button><button className="icon-btn" onClick={() => deleteItem(`/tasks/${task.id}`, "Delete this task?")}>Delete</button></div></>}</div>)}</div></article>)}{stories.length === 0 && <div className="empty-state">No stories yet. Create the first outcome for this project.</div>}</main><aside><section className="card section-card"><div className="section-heading"><div><p className="eyebrow">Project team</p><h2>Members</h2></div><span className="badge">{members.length}</span></div><form className="form-actions" onSubmit={addMember}><select value={memberId} onChange={(event) => setMemberId(event.target.value)}><option value="">Add a registered user…</option>{availableUsers.map((user) => <option key={user.id} value={user.id}>{user.name} ({user.email})</option>)}</select><button className="btn" disabled={!memberId || saving}>Add</button></form><div className="team-list">{members.map((member) => <div className="member-chip" key={member.id}><span className="avatar">{initials(member.name)}</span><span>{member.name}</span>{members.length > 1 && <button className="icon-btn" title={`Remove ${member.name}`} onClick={() => removeMember(member.id)}>Remove</button>}</div>)}</div></section><section className="card section-card"><p className="eyebrow">Project history</p><h2>Activity</h2>{activities.length ? <div className="activity-list">{activities.map((activity) => <div className="activity-item" key={activity.id}><strong>{activity.action}</strong><p>{activity.details}</p><small>{new Date(activity.created_at).toLocaleString()}</small></div>)}</div> : <p className="muted">No activity recorded yet.</p>}</section></aside></div></div>;
}

function TaskForm({ draft, setDraft, saving, onSubmit, onCancel }) {
  return <form className="task-create form-grid" onSubmit={onSubmit}><input placeholder="Task title" value={draft.title} onChange={(event) => setDraft({ ...draft, title: event.target.value })} required /><textarea placeholder="Optional task details" value={draft.description} onChange={(event) => setDraft({ ...draft, description: event.target.value })} /><div className="form-row"><select value={draft.priority} onChange={(event) => setDraft({ ...draft, priority: event.target.value })}><option value="LOW">LOW</option><option value="MEDIUM">MEDIUM</option><option value="HIGH">HIGH</option></select><input type="date" value={draft.due_date} onChange={(event) => setDraft({ ...draft, due_date: event.target.value })} /></div><div className="form-actions"><button className="btn btn-primary" disabled={saving}>Save task</button><button type="button" className="btn btn-quiet" onClick={onCancel}>Cancel</button></div></form>;
}

export default ProjectDetails;
