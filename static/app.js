const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

function toast(message) {
  const el = $("#toast");
  el.textContent = message;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 3500);
}
function showView(name) {
  $$(".view").forEach(v => v.classList.toggle("active", v.id === `view-${name}`));
  $$(".nav-item").forEach(b => b.classList.toggle("active", b.dataset.view === name));
  const titles = {
    chat: ["Good afternoon 👋", "Let's make your next career move clearer."],
    careers: ["Explore your career fit", "Compare possible paths with your current interests and skills."],
    roadmap: ["Your learning roadmap", "Turn your goal into a realistic plan."],
    resume: ["Make your resume stronger", "Get practical suggestions for your target role."],
    interview: ["Prepare with confidence", "Practise explaining what you know and what you have built."],
    jobs: ["Explore opportunities", "Search job and internship portals using your own keywords."]
  };
  $("#page-title").textContent = titles[name][0];
  $("#page-subtitle").textContent = titles[name][1];
  window.scrollTo({top: 0, behavior: "smooth"});
}
$$(".nav-item").forEach(b => b.addEventListener("click", () => showView(b.dataset.view)));
$$("[data-go]").forEach(b => b.addEventListener("click", () => showView(b.dataset.go)));

function addMessage(role, text) {
  const wrap = document.createElement("div");
  wrap.className = `message ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  wrap.appendChild(bubble);
  $("#chat-messages").appendChild(wrap);
  $("#chat-messages").scrollTop = $("#chat-messages").scrollHeight;
}
async function postJSON(url, data) {
  const response = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "Request failed.");
  return result;
}
$("#chat-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = $("#chat-input");
  const message = input.value.trim();
  if (!message) return;
  addMessage("user", message);
  input.value = "";
  const button = $("#chat-form button");
  button.disabled = true;
  addMessage("bot", "Thinking…");
  const thinking = $("#chat-messages").lastElementChild;
  try {
    const result = await postJSON("/api/chat", {message});
    thinking.querySelector(".bubble").textContent = result.reply;
  } catch (error) {
    thinking.querySelector(".bubble").textContent = error.message;
  } finally {
    button.disabled = false;
    $("#chat-messages").scrollTop = $("#chat-messages").scrollHeight;
    input.focus();
  }
});
$$(".suggestion").forEach(button => button.addEventListener("click", () => {
  $("#chat-input").value = button.textContent;
  $("#chat-input").focus();
}));
$("#clear-chat").addEventListener("click", async () => {
  if (!confirm("Clear this chat history?")) return;
  try {
    await fetch("/api/history", {method: "DELETE"});
    $("#chat-messages").innerHTML = "";
    addMessage("bot", "Chat cleared. What career question can I help with?");
  } catch (_) { toast("Could not clear chat."); }
});

$("#career-form").addEventListener("submit", async event => {
  event.preventDefault();
  const container = $("#career-results");
  container.innerHTML = "<p>Finding possible matches…</p>";
  try {
    const result = await postJSON("/api/careers", {
      interests: $("#interests").value,
      skills: $("#skills").value
    });
    container.innerHTML = "";
    result.results.forEach((item, index) => {
      const card = document.createElement("article");
      card.className = "result-card";
      const missing = item.missing.map(x => `<li>${escapeHTML(x)}</li>`).join("");
      const projects = item.projects.map(x => `<li>${escapeHTML(x)}</li>`).join("");
      card.innerHTML = `<span class="tag">Match option ${index + 1}</span><h3>${escapeHTML(item.name)}</h3>
        <p>Interest keyword matches: ${item.score}. This is a simple heuristic, not a validated aptitude test.</p>
        <h4>Skills to consider</h4><ul>${missing || "<li>Review your existing skills and compare them with job descriptions.</li>"}</ul>
        <h4>Project ideas</h4><ul>${projects}</ul>`;
      container.appendChild(card);
    });
  } catch (error) { container.textContent = error.message; }
});

function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
}
async function runTextTool(formId, endpoint, payload, outputId, heading) {
  $(formId).addEventListener("submit", async event => {
    event.preventDefault();
    const out = $(outputId);
    out.classList.remove("hidden");
    out.textContent = "Working on your request…";
    try {
      const result = await postJSON(endpoint, payload());
      out.textContent = result.roadmap || result.questions || result.review || "No result returned.";
    } catch (error) { out.textContent = error.message; }
  });
}
runTextTool("#roadmap-form", "/api/roadmap",
  () => ({role: $("#roadmap-role").value, level: $("#roadmap-level").value}),
  "#roadmap-output", "Learning roadmap");
runTextTool("#interview-form", "/api/interview",
  () => ({role: $("#interview-role").value, level: $("#interview-level").value}),
  "#interview-output", "Interview questions");

$("#resume-form").addEventListener("submit", async event => {
  event.preventDefault();
  const out = $("#resume-output");
  out.classList.remove("hidden");
  out.textContent = "Reading resume and preparing feedback…";
  const form = new FormData(event.currentTarget);
  try {
    const response = await fetch("/api/resume", {method: "POST", body: form});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Resume review failed.");
    out.textContent = result.review;
  } catch (error) { out.textContent = error.message; }
});

$("#jobs-form").addEventListener("submit", async event => {
  event.preventDefault();
  const results = $("#jobs-results");
  results.innerHTML = "<p>Preparing search links…</p>";
  try {
    const response = await fetch(`/api/jobs?role=${encodeURIComponent($("#job-role").value)}`);
    const data = await response.json();
    results.innerHTML = "";
    data.links.forEach(item => {
      const card = document.createElement("article");
      card.className = "job-card";
      card.innerHTML = `<h3>${escapeHTML(item.name)}</h3><p>Search listings for “${escapeHTML(data.role)}”.</p><a href="${item.url}" target="_blank" rel="noopener noreferrer">Open job search ↗</a>`;
      results.appendChild(card);
    });
  } catch (_) { results.textContent = "Could not create search links."; }
});
