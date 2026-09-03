/* ============ CONFIG ============ */
const API_BASE = "http://127.0.0.1:8000"; // ← My API domain
const TELEGRAM_BOT_URL = "https://t.me/thejob_helperbot"; // My bot link once it's ready
const PAGE_SIZE = 12;

const MOCK_JOBS = [
  { rowid: 1, title: "Backend Engineer", company: "Nile Systems", location: "Cairo, Egypt (Remote)", job_type: "Full-time", experience: "Mid", min_years: 3, max_years: 5, min_salary: 2200, max_salary: 3200, currency: "USD", posted: "2 days ago", job_link: "#" },
  { rowid: 2, title: "Frontend Developer", company: "Delta Labs", location: "Alexandria, Egypt", job_type: "Full-time", experience: "Entry", min_years: 0, max_years: 2, min_salary: 1200, max_salary: 1800, currency: "USD", posted: "5 days ago", job_link: "#" },
  { rowid: 3, title: "DevOps Engineer", company: "Vault Cloud", location: "Remote", job_type: "Contract", experience: "Senior", min_years: 6, max_years: 9, min_salary: 3500, max_salary: 5000, currency: "USD", posted: "1 day ago", job_link: "#" },
  { rowid: 4, title: "Data Analyst", company: "Orbit Analytics", location: "Giza, Egypt", job_type: "Full-time", experience: "Mid", min_years: 2, max_years: 4, min_salary: 1800, max_salary: 2600, currency: "USD", posted: "1 week ago", job_link: "#" },
];

const FILTER_LABELS = {
  job_type: v => v,
  remote: v => ({ remote_only: "Remote only", remote_and_onsite: "Remote + onsite", onsite_only: "Onsite only" }[v] || v),
  posted: v => ({ today: "Today", last_3_days: "Last 3 days", last_week: "Last week", last_month: "Last month" }[v] || v),
  experience_level: v => v.charAt(0).toUpperCase() + v.slice(1),
  actively_hiring: () => "Actively hiring",
  min_salary: v => `Min $${v}`,
  max_salary: v => `Max $${v}`,
};

const LOCATION_ALIASES = {
  "new york city": "New York",
  "nyc": "New York",
  "bangalore": "Bengaluru",
  "bangalore urban": "Bengaluru",
  "sf bay area": "San Francisco",
  "san francisco bay area": "San Francisco",
};
