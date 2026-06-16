// Vanilla, no build step. Badge from /api/me, accordion + client-side search from /api/skills.
(() => {
  const $ = (id) => document.getElementById(id);
  const esc = (s) =>
    String(s ?? "").replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );

  let all = [];

  // First letter of first + last word (or first 2 letters of a single word).
  function initials(s) {
    const w = String(s).trim().split(/\s+/).filter(Boolean);
    if (!w.length) return "";
    if (w.length === 1) return w[0].slice(0, 2);
    return w[0][0] + w[w.length - 1][0];
  }

  async function loadBadge() {
    try {
      const me = await (await fetch("/api/me")).json();
      const label = (me && (me.name || me.username)) || "";
      if (label) {
        const b = $("badge");
        b.textContent = initials(label);
        b.title = label;
        b.hidden = false;
      }
    } catch (_) {
      /* anonymous / no forward-auth headers */
    }
  }

  function rowHtml(s) {
    const wtu = s.when_to_use ? `<span class="wtu">${esc(s.when_to_use)}</span>` : "";
    const type = s.type === "agent" ? "agent" : "skill";
    return `<details class="row">
      <summary>
        <span class="tag ${type}">${esc(s.type)}</span>
        <span class="name">${esc(s.name)}</span>${wtu}
      </summary>
      <p class="desc">${esc(s.description)}</p>
    </details>`;
  }

  function render(list) {
    $("rows").innerHTML = list.map(rowHtml).join("");
    $("empty").hidden = list.length !== 0;
    $("count").textContent = `${list.length} von ${all.length} Skills`;
  }

  function filter(q) {
    q = q.trim().toLowerCase();
    if (!q) return all;
    const toks = q.split(/\s+/);
    return all.filter((s) => {
      const hay = `${s.name} ${s.when_to_use} ${s.description}`.toLowerCase();
      return toks.every((t) => hay.includes(t));
    });
  }

  async function init() {
    loadBadge();
    try {
      all = await (await fetch("/api/skills")).json();
    } catch (_) {
      all = [];
    }
    render(all);
    $("q").addEventListener("input", (e) => render(filter(e.target.value)));

    document.querySelectorAll(".copy-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const el = $(btn.dataset.copy);
        if (!el) return;
        try {
          await navigator.clipboard.writeText(el.textContent.trim());
          const old = btn.textContent;
          btn.textContent = "Kopiert!";
          btn.classList.add("copied");
          setTimeout(() => {
            btn.textContent = old;
            btn.classList.remove("copied");
          }, 1500);
        } catch (_) {
          /* clipboard unavailable */
        }
      });
    });
  }

  init();
})();
