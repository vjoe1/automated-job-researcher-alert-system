/* ============ API ============ */
function buildQuery() {
  const params = new URLSearchParams();
  if (state.q) params.set("q", state.q);
  if (state.job_type) params.set("job_type", state.job_type);
  if (state.remote) params.set("remote", state.remote);
  if (state.posted) params.set("posted", state.posted);
  if (state.experience_level) params.set("experience_level", state.experience_level);
  if (state.actively_hiring) params.set("actively_hiring", "true");
  if (state.min_salary) params.set("min_salary", state.min_salary);
  if (state.max_salary) params.set("max_salary", state.max_salary);
  params.set("sort_by", state.sort_by);
  return params.toString();
}

async function fetchJobCount() {
  try {
    const res = await fetch(`${API_BASE}/jobs/count`);
    if (!res.ok) throw new Error();
    const data = await res.json();
    animateStat(document.getElementById("statJobs"), data.total ?? 0);
    document.getElementById("statusText").textContent = "connected · live feed";
    document.getElementById("statusDot").classList.remove("off");
  } catch (e) {
    document.getElementById("statJobs").textContent = MOCK_JOBS.length;
    document.getElementById("statusText").textContent = "offline · demo mode";
    document.getElementById("statusDot").classList.add("off");
  }
}
// Controller for the latest fetch request; used to cancel any previous pending request
let fetchJobsController = null;

async function fetchJobs() {
  // Prevent any old pending request from overwriting the new result

  if (fetchJobsController) fetchJobsController.abort();
  fetchJobsController = new AbortController();
  const { signal } = fetchJobsController;

  const grid = document.getElementById("jobsGrid");
  const resultsCount = document.getElementById("resultsCount");

  grid.innerHTML = "";
  for (let i = 0; i < 6; i++) {
    const sk = document.createElement("div");
    sk.className = "skeleton";
    grid.appendChild(sk);
  }
  resultsCount.textContent = "Scanning…";

  try {
    const res = await fetch(`${API_BASE}/jobs?${buildQuery()}`, { signal });
    if (!res.ok) throw new Error("bad response");
    allJobs = await res.json();
    usingDemoData = false;
    document.getElementById("demoBanner").classList.remove("show");
  } catch (e) {
    if (e.name === "AbortError") return; // Request was intentionally aborted; do not render canceled results
    usingDemoData = true;
    allJobs = MOCK_JOBS;
    document.getElementById("demoBanner").classList.add("show");
  }

  state.page = 1;
  renderPage();
  if (currentMode === "analytics") renderAnalytics();
}