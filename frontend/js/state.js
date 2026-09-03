/* ============ STATE ============ */
const state = {
  q: "",
  job_type: null,
  remote: null,
  posted: null,
  experience_level: null,
  actively_hiring: null,
  min_salary: null,
  max_salary: null,
  sort_by: "newest",
  page: 1,
};

let allJobs = [];
let currentMode = "search";
let usingDemoData = false;
const chartInstances = {};
