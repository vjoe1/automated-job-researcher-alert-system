/* ============ RADAR / HERO ANIMATION ============ */
function playRadarLoop() {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduced) return;
  gsap.to("#sweepWrap", { rotation: 360, duration: 8, repeat: -1, ease: "none", transformOrigin: "450px 450px" });
  ["ping1", "ping2", "ping3", "ping4"].forEach((id, i) => {
    gsap.timeline({ repeat: -1, delay: i * 1.8 })
      .set(`#${id}`, { opacity: 0, scale: 0.4, transformOrigin: "center" })
      .to(`#${id}`, { opacity: 0.9, scale: 1.6, duration: 0.5, ease: "power2.out" })
      .to(`#${id}`, { opacity: 0, duration: 1.1, ease: "power1.in" }, "-=0.1")
      .to({}, { duration: 4 });
  });
}

function playBootSequence() {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reduced) {
    gsap.set(["#eyebrow", "#headline", "#heroSub", "#heroStats", "#heroCtas"], { opacity: 1 });
    return;
  }

  gsap.set(["#eyebrow", "#headline", "#heroSub", "#heroStats", "#heroCtas"], { opacity: 0, y: 14 });

  gsap.timeline()
    .to("#eyebrow", { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }, 0.1)
    .to("#headline", { opacity: 1, y: 0, duration: 0.8, ease: "power3.out" }, "-=0.3")
    .to("#heroSub", { opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }, "-=0.4")
    .to("#heroStats", { opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }, "-=0.3")
    .to("#heroCtas", { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }, "-=0.3");
}

/* ============ MODE TABS ============ */
const modeTabs = document.querySelectorAll(".mode-tab");
const modeTabBg = document.getElementById("modeTabBg");

function moveTabBg(tab) {
  gsap.to(modeTabBg, {
    x: tab.offsetLeft - 5,
    width: tab.offsetWidth,
    duration: 0.4,
    ease: "power3.out",
  });
}

function switchMode(mode) {
  if (mode === currentMode) return;
  currentMode = mode;

  modeTabs.forEach(t => t.classList.toggle("active", t.dataset.mode === mode));
  moveTabBg(document.querySelector(`.mode-tab[data-mode="${mode}"]`));

  const current = document.querySelector(".mode-panel.visible");
  const next = document.querySelector(`.mode-panel[data-panel="${mode}"]`);

  //  Stoping any animation 
  if (current) gsap.killTweensOf(current);
  if (next) gsap.killTweensOf(next);

  const tl = gsap.timeline();

  if (current) {
    tl.to(current, {
      opacity: 0,
      y: -8,
      duration: 0.18,
      ease: "power1.in",
      onComplete: () => {
        current.classList.remove("visible");
        current.style.display = "none"; 
      }
    });
  }

  tl.set(next, { opacity: 0, y: 8, display: "block" })
    .add(() => {
      next.classList.add("visible");
      if (mode === "analytics") renderAnalytics();
    })
    .to(next, { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" });
}
modeTabs.forEach(tab => {
  tab.addEventListener("click", () => switchMode(tab.dataset.mode));
});

window.addEventListener("load", () => moveTabBg(document.querySelector(".mode-tab.active")));
window.addEventListener("resize", () => moveTabBg(document.querySelector(".mode-tab.active")));

/* ============ STATS ============ */
function animateStat(el, target) {
  const obj = { val: 0 };
  gsap.to(obj, {
    val: target,
    duration: 1.1,
    ease: "power2.out",
    onUpdate: () => el.textContent = Math.round(obj.val).toLocaleString(),
  });
}

/* ============ RESULTS / PAGINATION ============ */
function renderPage() {
  const grid = document.getElementById("jobsGrid");
  const resultsCount = document.getElementById("resultsCount");
  const resultsRange = document.getElementById("resultsRange");
  const pagination = document.getElementById("pagination");

  grid.innerHTML = "";

  if (allJobs.length === 0) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1;">
        <div class="big">No listings match these filters</div>
        Try widening your search or clearing a filter.
      </div>`;
    resultsCount.textContent = "0 listings found";
    resultsRange.textContent = "";
    pagination.style.display = "none";
    return;
  }

  const totalPages = Math.max(1, Math.ceil(allJobs.length / PAGE_SIZE));
  state.page = Math.min(Math.max(1, state.page), totalPages);

  const start = (state.page - 1) * PAGE_SIZE;
  const pageJobs = allJobs.slice(start, start + PAGE_SIZE);

  const frag = document.createDocumentFragment();
  pageJobs.forEach(job => frag.appendChild(renderJobCard(job)));
  grid.appendChild(frag);

  const cards = grid.querySelectorAll(".job-card");
  gsap.fromTo(cards, { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.05, ease: "power2.out" });

  resultsCount.innerHTML = `<strong>${allJobs.length}</strong> listings found`;
  resultsRange.textContent = `Showing ${start + 1}–${start + pageJobs.length}`;

  renderPagination(totalPages);
}

function renderPagination(totalPages) {
  const pagination = document.getElementById("pagination");
  pagination.innerHTML = "";

  if (totalPages <= 1) {
    pagination.style.display = "none";
    return;
  }
  pagination.style.display = "flex";

  const goTo = p => { state.page = p; renderPage(); document.getElementById("console").scrollIntoView({ behavior: "smooth", block: "start" }); };

  const prev = document.createElement("button");
  prev.className = "page-btn";
  prev.textContent = "←";
  prev.disabled = state.page === 1;
  prev.addEventListener("click", () => goTo(state.page - 1));
  pagination.appendChild(prev);

  const pages = new Set([1, totalPages, state.page, state.page - 1, state.page + 1]);
  let lastRendered = 0;
  [...pages].filter(p => p >= 1 && p <= totalPages).sort((a, b) => a - b).forEach(p => {
    if (p - lastRendered > 1) {
      const dots = document.createElement("span");
      dots.className = "page-ellipsis";
      dots.textContent = "…";
      pagination.appendChild(dots);
    }
    const btn = document.createElement("button");
    btn.className = "page-btn" + (p === state.page ? " active" : "");
    btn.textContent = p;
    btn.addEventListener("click", () => goTo(p));
    pagination.appendChild(btn);
    lastRendered = p;
  });

  const next = document.createElement("button");
  next.className = "page-btn";
  next.textContent = "→";
  next.disabled = state.page === totalPages;
  next.addEventListener("click", () => goTo(state.page + 1));
  pagination.appendChild(next);
}

/* ============ JOB CARDS ============ */
function renderJobCard(job) {
  const card = document.createElement("article");
  card.className = "job-card";

  const salary = formatSalary(job.min_salary, job.max_salary, job.currency);
  const yearsTag = (job.min_years != null || job.max_years != null)
    ? `${job.min_years ?? 0}–${job.max_years ?? "+"} yrs`
    : null;
  const hiringBadge = (job.hiring && /actively/i.test(job.hiring)) ? `<span class="job-hiring">Actively hiring</span>` : "";

  card.innerHTML = `
    <div class="job-card-top">
      <div>
        <div class="job-title">${escapeHtml(job.title || "Untitled role")}</div>
        <div class="job-company">${escapeHtml(job.company || "Unknown company")}</div>
      </div>
      ${hiringBadge}
    </div>
    <div class="job-meta">
      ${job.location ? `<span class="job-tag">${escapeHtml(job.location)}</span>` : ""}
      ${job.job_type ? `<span class="job-tag">${escapeHtml(job.job_type)}</span>` : ""}
      ${job.experience ? `<span class="job-tag">${escapeHtml(job.experience)}</span>` : ""}
      ${yearsTag ? `<span class="job-tag">${yearsTag}</span>` : ""}
    </div>
    <div class="job-card-bottom">
      <div>
        <div class="job-salary">${salary}</div>
        <div class="job-posted">${escapeHtml(job.posted || "")}</div>
      </div>
      <div style="display:flex; align-items:center; gap:8px;">
        <a class="telegram-link mini" href="${TELEGRAM_BOT_URL}" target="_blank" rel="noopener" title="Save this job & get alerts on Telegram">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M9.78 18.65l.28-4.23 7.68-6.92c.34-.31-.07-.46-.52-.19L7.74 13.3 3.64 12c-.88-.25-.89-.86.2-1.3l15.97-6.16c.73-.33 1.43.18 1.15 1.3l-2.72 12.81c-.19.91-.74 1.13-1.5.71l-4.14-3.05-2 1.93c-.23.23-.42.42-.82.42z"/></svg>
          <span>Save</span>
        </a>
        <a class="job-link-btn" href="${safeUrl(job.job_link)}" target="_blank" rel="noopener">View ↗</a>
      </div>
    </div>
  `;
  return card;
}

function formatSalary(min, max, currency) {
  if (min == null && max == null) return "Salary not listed";
  const c = currency || "";
  const fmt = n => n >= 1000 ? `${Math.round(n / 1000)}k` : n;
  if (min != null && max != null) return `${c} ${fmt(min)} – ${fmt(max)}`;
  return `${c} ${fmt(min ?? max)}`;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
function safeUrl(url) {
  if (!url) return "#";
  try {
    const u = new URL(url, window.location.href);
    if (u.protocol !== "http:" && u.protocol !== "https:") return "#";
    return escapeHtml(u.href);
  } catch (e) {
    return "#";
  }
}

/* ============ ACTIVE PILLS ============ */
function renderActivePills() {
  const wrap = document.getElementById("activePills");
  const keys = ["job_type", "remote", "posted", "experience_level", "actively_hiring", "min_salary", "max_salary"];
  const active = keys.filter(k => state[k]);

  wrap.innerHTML = "";
  if (state.q) {
    wrap.appendChild(makePill(`Search: "${state.q}"`, () => {
      state.q = "";
      document.getElementById("searchInput").value = "";
      state.page = 1;
      fetchJobs();
      renderActivePills();
    }));
  }
  active.forEach(k => {
    wrap.appendChild(makePill(FILTER_LABELS[k](state[k]), () => {
      state[k] = null;
      if (k === "min_salary") document.getElementById("minSalary").value = "";
      if (k === "max_salary") document.getElementById("maxSalary").value = "";
      document.querySelectorAll(`.chip-row[data-group="${k}"] .chip`).forEach(c => c.classList.remove("active"));
      state.page = 1;
      updateFilterCount();
      fetchJobs();
      renderActivePills();
    }));
  });

  if (wrap.children.length) {
    gsap.fromTo(wrap.children, { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.25, stagger: 0.03, ease: "power2.out" });
  }
}

function makePill(label, onRemove) {
  const pill = document.createElement("span");
  pill.className = "pill";
  pill.innerHTML = `<span>${escapeHtml(label)}</span>`;
  const btn = document.createElement("button");
  btn.setAttribute("aria-label", "Remove filter");
  btn.textContent = "✕";
  btn.addEventListener("click", onRemove);
  pill.appendChild(btn);
  return pill;
}

/* ============ FILTERS UI ============ */
function updateFilterCount() {
  const active = ["job_type", "remote", "posted", "experience_level", "actively_hiring", "min_salary", "max_salary"]
    .filter(k => state[k]).length;
  document.getElementById("filterCount").textContent = active > 0 ? `(${active})` : "";
}

document.querySelectorAll(".chip-row").forEach(row => {
  const group = row.dataset.group;
  row.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const val = chip.dataset.value;
      const isActive = chip.classList.contains("active");
      row.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
      if (!isActive) {
        chip.classList.add("active");
        state[group] = group === "actively_hiring" ? true : val;
      } else {
        state[group] = null;
      }
      state.page = 1;
      updateFilterCount();
      fetchJobs();
      renderActivePills();
    });
  });
});

document.querySelectorAll(".sort-option").forEach(opt => {
  opt.addEventListener("click", () => {
    document.querySelectorAll(".sort-option").forEach(o => o.classList.remove("active"));
    opt.classList.add("active");
    state.sort_by = opt.dataset.value;
    state.page = 1;
    fetchJobs();
  });
});

document.getElementById("minSalary").addEventListener("input", debounce(e => {
  state.min_salary = e.target.value ? Number(e.target.value) : null;
  state.page = 1;
  updateFilterCount();
  fetchJobs();
  renderActivePills();
}, 500));

document.getElementById("maxSalary").addEventListener("input", debounce(e => {
  state.max_salary = e.target.value ? Number(e.target.value) : null;
  state.page = 1;
  updateFilterCount();
  fetchJobs();
  renderActivePills();
}, 500));

document.getElementById("clearFilters").addEventListener("click", () => {
  Object.keys(state).forEach(k => { if (k !== "sort_by" && k !== "page" && k !== "q") state[k] = null; });
  document.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
  document.getElementById("minSalary").value = "";
  document.getElementById("maxSalary").value = "";
  state.page = 1;
  updateFilterCount();
  fetchJobs();
  renderActivePills();
});

document.getElementById("searchInput").addEventListener("input", debounce(e => {
  state.q = e.target.value.trim();
  state.page = 1;
  fetchJobs();
  renderActivePills();
}, 450));

function debounce(fn, wait) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), wait); };
}
