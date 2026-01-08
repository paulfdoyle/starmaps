(() => {
  const cfg = window.BUGMGMT_CONFIG || {};
  const JSON_PATH = cfg.jsonPath || "";
  const FALLBACK = Array.isArray(window.BUGMGMT_FALLBACK) ? window.BUGMGMT_FALLBACK : [];

  const els = {
    project: document.getElementById("project"),
    phase: document.getElementById("phase"),
    stage: document.getElementById("stage"),
    status: document.getElementById("status"),
    severity: document.getElementById("severity"),
    search: document.getElementById("search"),
    reset: document.getElementById("resetFilters"),
    tbody: document.getElementById("issues-body"),
    total: document.getElementById("totalCount"),
    summary: document.getElementById("summaryRow"),
    detailTitle: document.getElementById("detailTitle"),
    detailMeta: document.getElementById("detailMeta"),
    detailBadges: document.getElementById("detailBadges"),
    detailBody: document.getElementById("detailBody"),
  };

  const statusOrder = ["open", "in_progress", "closed"];
  const severityOrder = ["critical", "major", "minor", "nit"];
  let issues = [];
  let selectedId = "";

  const norm = (v) => (v === null || v === undefined ? "" : String(v).trim());
  const normLower = (v) => norm(v).toLowerCase();
  const statusWeight = (v) => {
    const k = normLower(v);
    const idx = statusOrder.indexOf(k);
    return idx === -1 ? statusOrder.length : idx;
  };
  const severityWeight = (v) => {
    const k = normLower(v);
    const idx = severityOrder.indexOf(k);
    return idx === -1 ? severityOrder.length : idx;
  };

  function sortIssues(list) {
    return [...list].sort((a, b) => {
      const as = statusWeight(a.status);
      const bs = statusWeight(b.status);
      if (as !== bs) return as - bs;
      const ap = normLower(a.project);
      const bp = normLower(b.project);
      if (ap !== bp) return ap.localeCompare(bp);
      const av = severityWeight(a.severity);
      const bv = severityWeight(b.severity);
      if (av !== bv) return av - bv;
      return normLower(a.id).localeCompare(normLower(b.id));
    });
  }

  function uniqValues(key) {
    const vals = new Set();
    issues.forEach(i => {
      const v = norm(i[key]);
      if (v) vals.add(v);
    });
    return Array.from(vals).sort();
  }

  function setOptions(select, values) {
    if (!select) return;
    const opts = ['<option value="">All</option>'].concat(values.map(v => `<option value="${v}">${v}</option>`));
    select.innerHTML = opts.join("\n");
    select.value = "";
  }

  function badge(text, cls) {
    return `<span class="badge ${cls}">${text || "-"}</span>`;
  }

  function detailField(label, value) {
    if (!value) return "";
    return `<div class="detail-item"><div class="muted small">${label}</div><div>${value}</div></div>`;
  }

  function closureNote(issue) {
    if (normLower(issue.status) !== "closed") return "";
    if (issue.close_note) return norm(issue.close_note);
    if (Array.isArray(issue.events)) {
      const lastWithNote = [...issue.events].reverse().find(e => e && e.notes);
      if (lastWithNote && lastWithNote.notes) return norm(lastWithNote.notes);
    }
    return "";
  }

  function filterIssues() {
    const search = normLower(els.search && els.search.value);
    return issues.filter(i => {
      if (els.project && els.project.value && normLower(i.project) !== normLower(els.project.value)) return false;
      if (els.phase && els.phase.value && normLower(i.phase) !== normLower(els.phase.value)) return false;
      if (els.stage && els.stage.value && normLower(i.stage) !== normLower(els.stage.value)) return false;
      if (els.status && els.status.value && normLower(i.status) !== normLower(els.status.value)) return false;
      if (els.severity && els.severity.value && normLower(i.severity) !== normLower(els.severity.value)) return false;
      if (search) {
        const blob = JSON.stringify(i).toLowerCase();
        if (!blob.includes(search)) return false;
      }
      return true;
    });
  }

  function renderSummary(list) {
    if (!els.total || !els.summary) return;
    const total = issues.length;
    const open = list.filter(i => normLower(i.status) === "open").length;
    const inProgress = list.filter(i => normLower(i.status) === "in_progress").length;
    const closed = list.filter(i => normLower(i.status) === "closed").length;
    els.total.textContent = `${list.length} shown / ${total} total`;
    els.summary.innerHTML = `
      <div class="summary-card"><div class="muted small">Open</div><div class="h6">${open}</div></div>
      <div class="summary-card"><div class="muted small">In Progress</div><div class="h6">${inProgress}</div></div>
      <div class="summary-card"><div class="muted small">Closed</div><div class="h6">${closed}</div></div>
    `;
  }

  function renderTable(list) {
    if (!els.tbody) return;
    els.tbody.innerHTML = list.map(i => {
      const statusCls = `status-${normLower(i.status) || "open"}`;
      const sevCls = `sev-${normLower(i.severity) || "minor"}`;
      const summary = norm(i.summary || i.details || i.description);
      const openedAt = norm(i.opened_at || i.date);
      const rowId = norm(i.id);
      const selectedClass = rowId && rowId === selectedId ? "is-selected" : "";
      const rowLabel = summary ? `View details for ${summary}` : (rowId ? `View details for ${rowId}` : "View details");
      const detailsHtml = [
        summary ? `<div><strong>Summary:</strong> ${summary}</div>` : "",
        openedAt ? `<div class="muted small">Opened: ${openedAt}</div>` : "",
      ].filter(Boolean).join("");
      return `<tr class="${selectedClass}" data-id="${rowId}" tabindex="0" role="button" aria-label="${rowLabel}">
        <td class="id">${rowId}</td>
        <td>${badge(norm(i.status) || "open", `badge ${statusCls}`)}</td>
        <td>${badge(norm(i.severity) || "minor", `badge ${sevCls}`)}</td>
        <td>${norm(i.project)}</td>
        <td>${norm(i.phase)}</td>
        <td>${norm(i.stage)}</td>
        <td><div class="fw">${norm(i.area)}</div><div class="muted small">${norm(i.symptom)}</div></td>
        <td>
          ${detailsHtml || `<div class="muted small">No details provided.</div>`}
        </td>
      </tr>`;
    }).join("");
  }

  function renderDetail(issue) {
    if (!els.detailTitle || !els.detailMeta || !els.detailBadges || !els.detailBody) return;
    if (!issue) {
      els.detailTitle.textContent = "Issue Details";
      els.detailMeta.textContent = "Select a bug to view details.";
      els.detailBadges.innerHTML = "";
      els.detailBody.innerHTML = `<div class="muted small">No issue selected.</div>`;
      return;
    }
    const statusCls = `status-${normLower(issue.status) || "open"}`;
    const sevCls = `sev-${normLower(issue.severity) || "minor"}`;
    const summary = norm(issue.summary || issue.details || issue.description);
    const rootCause = norm(issue.root_cause);
    const proposedFix = norm(issue.proposed_fix);
    const qaRepro = norm(issue.qa_reproduction || issue.qa_repro);
    const close = closureNote(issue);
    const openedAt = norm(issue.opened_at || issue.date);
    const closedAt = norm(issue.date_closed || issue.closed_at || issue.closed_date);
    const owner = norm(issue.owner);
    const metaBits = [
      norm(issue.project) && `Project: ${norm(issue.project)}`,
      norm(issue.phase) && `Phase: ${norm(issue.phase)}`,
      norm(issue.stage) && `Stage: ${norm(issue.stage)}`,
      norm(issue.area) && `Area: ${norm(issue.area)}`,
    ].filter(Boolean);
    els.detailTitle.textContent = norm(issue.id) || "Issue Details";
    els.detailMeta.textContent = metaBits.join(" · ") || "Issue metadata";
    els.detailBadges.innerHTML = [
      badge(norm(issue.status) || "open", `badge ${statusCls}`),
      badge(norm(issue.severity) || "minor", `badge ${sevCls}`),
    ].join(" ");
    const bodyBits = [
      detailField("Summary", summary),
      detailField("Root cause", rootCause),
      detailField("Proposed fix", proposedFix),
      detailField("QA reproduction", qaRepro),
      detailField("Owner", owner),
      detailField("Opened", openedAt),
      detailField("Closed", closedAt),
      close ? detailField("Closure note", close) : "",
    ].filter(Boolean);
    els.detailBody.innerHTML = bodyBits.length ? bodyBits.join("") : `<div class="muted small">No details provided.</div>`;
  }

  function selectIssueById(issueId) {
    selectedId = issueId;
    render();
  }

  function render() {
    const list = filterIssues();
    renderSummary(list);
    renderTable(list);
    const selected = selectedId ? list.find(i => norm(i.id) === selectedId) : null;
    renderDetail(selected || null);
  }

  async function loadIssues() {
    if (JSON_PATH) {
      try {
        const res = await fetch(JSON_PATH, { cache: "no-store" });
        if (!res.ok) throw new Error(`fetch failed: ${res.status}`);
        const parsed = await res.json();
        if (!Array.isArray(parsed)) throw new Error("Unexpected payload");
        issues = sortIssues(parsed);
        return;
      } catch (err) {
        console.warn("Using fallback issues due to fetch error", err);
      }
    }
    issues = sortIssues(FALLBACK);
  }

  async function init() {
    await loadIssues();
    setOptions(els.project, uniqValues("project"));
    setOptions(els.phase, uniqValues("phase"));
    setOptions(els.stage, uniqValues("stage"));
    setOptions(els.status, uniqValues("status"));
    setOptions(els.severity, uniqValues("severity"));
    [els.project, els.phase, els.stage, els.status, els.severity].forEach(el => {
      if (!el) return;
      el.addEventListener("change", render);
      el.addEventListener("input", render);
    });
    if (els.search) els.search.addEventListener("input", render);
    if (els.reset) {
      els.reset.addEventListener("click", (evt) => {
        evt.preventDefault();
        [els.project, els.phase, els.stage, els.status, els.severity, els.search].forEach(el => { if (el) el.value = ""; });
        render();
      });
    }
    if (els.tbody) {
      els.tbody.addEventListener("click", (evt) => {
        const row = evt.target.closest("tr");
        if (!row) return;
        const rowId = norm(row.dataset.id);
        if (!rowId) return;
        selectIssueById(rowId);
      });
      els.tbody.addEventListener("keydown", (evt) => {
        if (evt.key !== "Enter" && evt.key !== " ") return;
        const row = evt.target.closest("tr");
        if (!row) return;
        const rowId = norm(row.dataset.id);
        if (!rowId) return;
        evt.preventDefault();
        selectIssueById(rowId);
      });
    }
    render();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
