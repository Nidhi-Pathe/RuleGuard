const EXAMPLES = [
  "What attendance is required to appear for semester examinations?",
  "When is Odd Semester undergraduate tuition due?",
  "What is the weekday hostel curfew for resident students?",
  "Can I pay my fees using cryptocurrency?",
  "What is the library borrowing limit for undergraduate students?",
];

const questionEl = document.getElementById("question");
const askBtn = document.getElementById("ask-btn");
const loading = document.getElementById("loading");
const result = document.getElementById("result");
const badge = document.getElementById("badge");
const answer = document.getElementById("answer");
const sources = document.getElementById("sources");
const conflictPanel = document.getElementById("conflict-panel");
const conflictList = document.getElementById("conflict-list");
const errorBox = document.getElementById("error");
const chips = document.getElementById("chips");

EXAMPLES.forEach((text) => {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.textContent = text;
  btn.addEventListener("click", () => {
    questionEl.value = text;
  });
  chips.appendChild(btn);
});

askBtn.addEventListener("click", submit);
questionEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    submit();
  }
});

async function submit() {
  const question = questionEl.value.trim();
  errorBox.classList.add("hidden");
  result.classList.add("hidden");
  if (question.length < 3) {
    showError("Please enter a question.");
    return;
  }
  askBtn.disabled = true;
  loading.classList.remove("hidden");
  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json") ? await response.json() : { detail: await response.text() };
    if (!response.ok) {
      throw new Error(data.detail || "Request failed.");
    }
    render(data);
  } catch (err) {
    showError(err.message || "Could not reach RuleGuard.");
  } finally {
    askBtn.disabled = false;
    loading.classList.add("hidden");
  }
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function render(data) {
  result.classList.remove("hidden");
  badge.className = `badge ${data.status}`;
  badge.textContent = data.status.replace("_", " ");
  answer.textContent = data.answer;

  if (data.conflicts && data.conflicts.length) {
    conflictPanel.classList.remove("hidden");
    conflictList.innerHTML = data.conflicts.map(conflictCard).join("");
  } else {
    conflictPanel.classList.add("hidden");
    conflictList.innerHTML = "";
  }

  sources.innerHTML = (data.sources || []).map(sourceCard).join("") || "<p class='hint'>No passages retrieved.</p>";
}

function conflictCard(item) {
  return `
    <div class="conflict-item">
      <p class="meta">${escapeHtml(item.category)} — ${escapeHtml(item.explanation)}</p>
      <div class="conflict-grid">
        <div>
          <strong>Section ${escapeHtml(item.section_a)}</strong>
          <p class="meta">${escapeHtml(item.title_a)} · ${escapeHtml(item.source_a)}</p>
          <div class="passage">${escapeHtml(item.rule_a)}</div>
        </div>
        <div>
          <strong>Section ${escapeHtml(item.section_b)}</strong>
          <p class="meta">${escapeHtml(item.title_b)} · ${escapeHtml(item.source_b)}</p>
          <div class="passage">${escapeHtml(item.rule_b)}</div>
        </div>
      </div>
    </div>`;
}

function sourceCard(item) {
  const score = Number(item.similarity).toFixed(2);
  return `
    <article class="source-card">
      <p class="meta"><strong>Section:</strong> ${escapeHtml(item.section)}</p>
      <p class="meta"><strong>Title:</strong> ${escapeHtml(item.title)}</p>
      <p class="meta"><strong>Similarity:</strong> ${score}</p>
      <p class="meta"><strong>Source:</strong> ${escapeHtml(item.source)}</p>
      <p class="meta"><strong>Passage:</strong></p>
      <div class="passage">${escapeHtml(item.text)}</div>
    </article>`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}



