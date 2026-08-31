import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function Projects() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState("ACTIVE");

  const loadProjects = useCallback(async () => {
    try {
      const params = {};
      if (search.trim()) params.search = search.trim();
      if (statusFilter) params.status_filter = statusFilter;
      const response = await api.get("/projects", { params });
      setProjects(response.data);
      setError("");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load projects");
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter]);

  useEffect(() => {
    const request = window.setTimeout(() => { void loadProjects(); }, 0);
    return () => window.clearTimeout(request);
  }, [loadProjects]);

  const reset = () => { setName(""); setDescription(""); setStatus("ACTIVE"); setEditingProject(null); setShowForm(false); };
  const save = async (event) => {
    event.preventDefault(); setSaving(true); setError("");
    try {
      if (editingProject) await api.put(`/projects/${editingProject.id}`, { name, description, status });
      else await api.post("/projects", { name, description, status });
      reset(); setLoading(true); await loadProjects();
    } catch (err) { setError(err.response?.data?.detail || "Failed to save project"); }
    finally { setSaving(false); }
  };
  const edit = (project) => { setEditingProject(project); setName(project.name); setDescription(project.description || ""); setStatus(project.status); setShowForm(true); };
  const remove = async (id) => {
    if (!window.confirm("Are you sure you want to delete this project?")) return;
    setSaving(true);
    try { await api.delete(`/projects/${id}`); setLoading(true); await loadProjects(); }
    catch (err) { setError(err.response?.data?.detail || "Failed to delete project"); }
    finally { setSaving(false); }
  };

  return <div className="page"><header className="page-header"><div><p className="eyebrow">Delivery workspace</p><h1>Projects</h1><p className="page-subtitle">Organize the initiatives where your team’s best work happens.</p></div><button className="btn btn-primary" onClick={() => setShowForm((visible) => !visible)}>{showForm ? "Close editor" : "+ New project"}</button></header>{error && <p className="notice">{error}</p>}{showForm && <form className="card panel form-grid" onSubmit={save}><h2>{editingProject ? "Edit project" : "Create a project"}</h2><input placeholder="Project name" value={name} onChange={(event) => setName(event.target.value)} required /><textarea placeholder="Give your team useful context…" value={description} onChange={(event) => setDescription(event.target.value)} />{editingProject && <select value={status} onChange={(event) => setStatus(event.target.value)}><option value="ACTIVE">ACTIVE</option><option value="COMPLETED">COMPLETED</option><option value="ARCHIVED">ARCHIVED</option></select>}<div className="form-actions"><button className="btn btn-primary" disabled={saving}>{saving ? "Saving…" : editingProject ? "Save changes" : "Create project"}</button><button type="button" className="btn btn-quiet" onClick={reset}>Cancel</button></div></form>}<section className="projects-toolbar"><input placeholder="Search projects…" value={search} onChange={(event) => { setLoading(true); setSearch(event.target.value); }} /><select value={statusFilter} onChange={(event) => { setLoading(true); setStatusFilter(event.target.value); }}><option value="">All statuses</option><option value="ACTIVE">Active</option><option value="COMPLETED">Completed</option><option value="ARCHIVED">Archived</option></select></section>{loading ? <div className="loading-state">Loading projects…</div> : projects.length === 0 ? <div className="empty-state">No projects match your filters.</div> : <section className="project-grid">{projects.map((project) => <article className="card project-card" key={project.id}><div className="project-card-top"><span className={`badge status-${project.status.toLowerCase()}`}>{project.status}</span><span className="muted">#{project.id}</span></div><h2>{project.name}</h2><p>{project.description || "No project description yet."}</p><div className="project-card-footer"><button className="btn btn-primary" onClick={() => navigate(`/projects/${project.id}`)}>Open project</button><div className="project-card-actions"><button className="icon-btn" onClick={() => edit(project)} disabled={saving}>Edit</button><button className="icon-btn" onClick={() => remove(project.id)} disabled={saving}>Delete</button></div></div></article>)}</section>}</div>;
}

export default Projects;
