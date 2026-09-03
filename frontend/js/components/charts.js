/* ============ ANALYTICS ============ */
function cleanLocation(loc){
  if(!loc) return null;
  if(/no equity/i.test(loc)) return null;
  let part = loc.includes("•") ? loc.split("•").pop().trim() : loc.trim();
  part = part.replace(/\+\d+$/, "").trim();
  if(!part) return null;
  const alias = LOCATION_ALIASES[part.toLowerCase()];
  return alias || part;
}

function experienceBucket(minYears){
  if(minYears == null) return "Not specified";
  if(minYears <= 2) return "Entry (0-2y)";
  if(minYears <= 5) return "Mid (3-5y)";
  if(minYears <= 9) return "Senior (6-9y)";
  return "Staff (10y+)";
}

function quantile(sortedArr, q){
  if(!sortedArr.length) return 0;
  const pos = (sortedArr.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  return sortedArr[base + 1] !== undefined ? sortedArr[base] + rest * (sortedArr[base+1] - sortedArr[base]) : sortedArr[base];
}

function buildSalaryHistogram(sortedMids){
  if(sortedMids.length < 4) return { buckets: [], outlierCount: 0 };

  const q1 = quantile(sortedMids, 0.25);
  const q3 = quantile(sortedMids, 0.75);
  const iqr = q3 - q1;
  const lower = Math.max(0, q1 - 1.5*iqr);
  const upper = q3 + 1.5*iqr;
  const trimmed = sortedMids.filter(v => v >= lower && v <= upper);
  const outlierCount = sortedMids.length - trimmed.length;

  if(!trimmed.length) return { buckets: [], outlierCount };

  const minV = trimmed[0], maxV = trimmed[trimmed.length - 1];
  const rawWidth = (maxV - minV) / 8 || 5000;
  const width = Math.max(5000, Math.round(rawWidth / 5000) * 5000);

  const bins = [];
  for(let start = Math.floor(minV / width) * width; start <= maxV; start += width){
    bins.push({ from: start, to: start + width, count: 0 });
  }
  trimmed.forEach(v => {
    const bin = bins.find(b => v >= b.from && v < b.to) || bins[bins.length - 1];
    bin.count++;
  });

  const fmtK = n => n >= 1000 ? `${Math.round(n/1000)}k` : n;
  const buckets = bins.map(b => [`$${fmtK(b.from)}–${fmtK(b.to)}`, b.count]);
  return { buckets, outlierCount };
}

function computeInsights(jobs){
  const total = jobs.length;

  const usdSalaries = jobs
    .filter(j => j.currency === "USD" && j.min_salary != null && j.max_salary != null)
    .map(j => (j.min_salary + j.max_salary) / 2)
    .sort((a,b) => a-b);
  let median = null;
  if(usdSalaries.length){
    const mid = Math.floor(usdSalaries.length / 2);
    median = usdSalaries.length % 2 !== 0 ? usdSalaries[mid] : (usdSalaries[mid-1] + usdSalaries[mid]) / 2;
  }
  const { buckets: salaryBuckets, outlierCount } = buildSalaryHistogram(usdSalaries);

  const hiringCount = jobs.filter(j => j.hiring && /actively/i.test(j.hiring)).length;

  const expCounts = {};
  jobs.forEach(j => { const b = experienceBucket(j.min_years); expCounts[b] = (expCounts[b] || 0) + 1; });
  const expOrder = ["Entry (0-2y)", "Mid (3-5y)", "Senior (6-9y)", "Staff (10y+)", "Not specified"];
  const experienceBreakdown = expOrder.filter(k => expCounts[k]).map(k => [k, expCounts[k]]);
  const topExperience = experienceBreakdown.filter(([k]) => k !== "Not specified").sort((a,b) => b[1]-a[1])[0];

  const titleCounts = {};
  jobs.forEach(j => { if(j.title) titleCounts[j.title] = (titleCounts[j.title] || 0) + 1; });
  const topTitles = Object.entries(titleCounts).sort((a,b) => b[1]-a[1]).slice(0, 8);

  const locationCounts = {};
  jobs.forEach(j => { const loc = cleanLocation(j.location); if(loc) locationCounts[loc] = (locationCounts[loc] || 0) + 1; });
  const topLocations = Object.entries(locationCounts).sort((a,b) => b[1]-a[1]).slice(0, 8);

  return {
    total, median, usdCount: usdSalaries.length, outlierCount,
    hiringPct: total ? Math.round((hiringCount/total)*100) : 0,
    topExperience, experienceBreakdown, topTitles, topLocations, salaryBuckets,
  };
}

function fmtMoney(n){
  return `$${Math.round(n).toLocaleString()}`;
}

function renderAnalytics(){
  const insightGrid = document.getElementById("insightGrid");
  if(!insightGrid) return;

  const stats = computeInsights(allJobs);
  insightGrid.innerHTML = "";

  const cards = [
    { label: "Listings in view", value: stats.total.toLocaleString() },
    { label: "Median salary", value: stats.median ? fmtMoney(stats.median) : "—", sub: stats.median ? `across ${stats.usdCount} USD listings` : "no USD salary data" },
    { label: "Top experience level", value: stats.topExperience ? stats.topExperience[0] : "—", sub: stats.topExperience ? `${stats.topExperience[1]} listings` : "" },
    { label: "Actively hiring", value: `${stats.hiringPct}%`, sub: "of listings in view" },
  ];

  cards.forEach(c => {
    const card = document.createElement("div");
    card.className = "insight-card";
    card.innerHTML = `
      <div class="insight-label">${escapeHtml(c.label)}</div>
      <div class="insight-value">${escapeHtml(String(c.value))}</div>
      ${c.sub ? `<div class="insight-sub">${escapeHtml(c.sub)}</div>` : ""}
    `;
    insightGrid.appendChild(card);
  });
  gsap.fromTo(insightGrid.children, { opacity:0, y:10 }, { opacity:1, y:0, duration:0.35, stagger:0.05, ease:"power2.out" });

  drawChart("titlesChart", stats.topTitles, "#4C86FF", { horizontal: true });
  drawChart("locationsChart", stats.topLocations, "#57E8C9", { horizontal: true });
  drawChart("salaryChart", stats.salaryBuckets, "#4C86FF", {
    horizontal: false,
    subtitle: stats.outlierCount ? `${stats.outlierCount} extreme outlier listing(s) excluded` : "",
  });
  drawChart("experienceChart", stats.experienceBreakdown, "#57E8C9", { horizontal: true });
}

function drawChart(canvasId, entries, color, opts = {}){
  const canvas = document.getElementById(canvasId);
  const emptyEl = document.getElementById(canvasId + "Empty");
  const subtitleEl = document.getElementById(canvasId + "Subtitle");

  if(subtitleEl) subtitleEl.textContent = opts.subtitle || "";

  if(typeof Chart === "undefined"){
    canvas.style.display = "none";
    emptyEl.textContent = "Chart library failed to load — check your internet connection.";
    emptyEl.style.display = "block";
    return;
  }

  if(chartInstances[canvasId]){ chartInstances[canvasId].destroy(); chartInstances[canvasId] = null; }

  if(!entries.length){
    canvas.style.display = "none";
    emptyEl.textContent = "Not enough data yet";
    emptyEl.style.display = "block";
    return;
  }
  canvas.style.display = "block";
  emptyEl.style.display = "none";

  const horizontal = opts.horizontal !== false;

  chartInstances[canvasId] = new Chart(canvas, {
    type: "bar",
    data: {
      labels: entries.map(e => e[0]),
      datasets: [{ data: entries.map(e => e[1]), backgroundColor: color, borderRadius: 4, maxBarThickness: horizontal ? 22 : 46 }],
    },
    options: {
      indexAxis: horizontal ? "y" : "x",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          grid: { color: "#1E2A47", display: horizontal },
          ticks: { color: "#8A97B8", font: { family: "JetBrains Mono", size: 10 } },
          beginAtZero: true,
        },
        y: {
          grid: { display: !horizontal, color: "#1E2A47" },
          ticks: { color: "#E9EEFC", font: { family: "Inter", size: 11.5 }, beginAtZero: true },
          beginAtZero: true,
        },
      },
    },
  });
}
