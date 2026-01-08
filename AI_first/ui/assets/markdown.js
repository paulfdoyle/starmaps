(() => {
  const escapeHtml = (text) => text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");

  const renderInline = (text) => {
    const escaped = escapeHtml(text);
    const withCode = escaped.replace(/`([^`]+)`/g, "<code>$1</code>");
    return withCode.replace(/\[([^\]]+)\]\(([^)]+)\)/g, "<a href=\"$2\">$1</a>");
  };

  const renderMarkdown = (md) => {
    const lines = md.replace(/\r\n/g, "\n").split("\n");
    const out = [];
    let inCode = false;
    let listType = null;

    const closeList = () => {
      if (listType) {
        out.push(`</${listType}>`);
        listType = null;
      }
    };

    for (const rawLine of lines) {
      const line = rawLine.replace(/\t/g, "  ");
      if (line.trim().startsWith("```")) {
        if (inCode) {
          out.push("</code></pre>");
          inCode = false;
        } else {
          closeList();
          out.push("<pre><code>");
          inCode = true;
        }
        continue;
      }

      if (inCode) {
        out.push(escapeHtml(line));
        continue;
      }

      const heading = line.match(/^(#{1,3})\s+(.*)$/);
      if (heading) {
        closeList();
        const level = heading[1].length;
        out.push(`<h${level}>${renderInline(heading[2])}</h${level}>`);
        continue;
      }

      const ulItem = line.match(/^\s*[-*]\s+(.*)$/);
      if (ulItem) {
        if (listType !== "ul") {
          closeList();
          out.push("<ul>");
          listType = "ul";
        }
        out.push(`<li>${renderInline(ulItem[1])}</li>`);
        continue;
      }

      const olItem = line.match(/^\s*\d+\.\s+(.*)$/);
      if (olItem) {
        if (listType !== "ol") {
          closeList();
          out.push("<ol>");
          listType = "ol";
        }
        out.push(`<li>${renderInline(olItem[1])}</li>`);
        continue;
      }

      if (!line.trim()) {
        closeList();
        continue;
      }

      closeList();
      out.push(`<p>${renderInline(line)}</p>`);
    }

    closeList();
    if (inCode) out.push("</code></pre>");
    return out.join("\n");
  };

  const load = (el, path) => {
    const resolved = new URL(path, window.location.href).href;
    fetch(resolved, { cache: "no-store" })
      .then((res) => {
        if (!res.ok) throw new Error("fetch failed");
        return res.text();
      })
      .then((text) => {
        el.innerHTML = renderMarkdown(text);
      })
      .catch(() => {
        const hint = window.location.protocol === "file:"
          ? "Local file fetch blocked by the browser. Open this UI via a local server (example: python3 -m http.server from the repo root)."
          : "Unable to load markdown.";
        el.innerHTML = `<p class=\"muted small\">${hint}</p>`;
      });
  };

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-md]").forEach((el) => {
      const path = el.getAttribute("data-md");
      if (path) load(el, path);
    });
  });

  window.Markdown = { render: renderMarkdown, load };
})();
