/**
 * Text-to-Persons Frontend Application
 *
 * Handles user interactions, calling proxy endpoints, running test suites,
 * and refreshing operational metrics.
 */

/**
 * Fetch and parse JSON from the given URL with comprehensive error formatting.
 *
 * @param {string} url - Target URL.
 * @param {RequestInit} [opts] - Fetch options.
 * @returns {Promise<any>} Parsed JSON or text payload.
 */
async function fetchJson(url, opts) {
  const res = await fetch(url, opts);
  const contentType = res.headers.get("content-type") || "";
  let payload = null;

  if (contentType.includes("application/json")) {
    payload = await res.json();
  } else {
    payload = await res.text();
  }

  if (!res.ok) {
    // Standardize errors from FastAPI (detail field)
    if (payload && typeof payload === "object" && payload.detail) {
      throw new Error(payload.detail);
    }
    throw new Error(typeof payload === "string" ? payload : "Request failed.");
  }

  return payload;
}

/**
 * Set the status message and style class.
 *
 * @param {string} text - Message text.
 * @param {string} [cls] - CSS class ('hint', 'ok', 'warn', 'err').
 */
function setStatus(text, cls) {
  const el = document.getElementById("statusLine");
  if (!el) return;
  el.textContent = text;
  el.className = cls ? cls : "hint";
}

/**
 * Render extracted person entities as badge pills.
 *
 * @param {string[]} persons - List of extracted person names.
 */
function renderPersons(persons) {
  const wrap = document.getElementById("personsPills");
  if (!wrap) return;
  wrap.innerHTML = "";

  if (!persons || persons.length === 0) {
    const p = document.createElement("div");
    p.className = "hint";
    p.textContent = "No persons returned.";
    wrap.appendChild(p);
    return;
  }

  persons.forEach((person) => {
    const pill = document.createElement("span");
    pill.className = "pill";
    pill.textContent = person;
    wrap.appendChild(pill);
  });
}

/**
 * Fetch and display operational metrics from the backend.
 */
async function refreshMetrics() {
  const metricsEl = document.getElementById("metricsOutput");
  if (!metricsEl) return;

  try {
    const m = await fetchJson("/api/metrics", { method: "GET" });
    metricsEl.textContent = JSON.stringify(m, null, 2);
  } catch (e) {
    metricsEl.textContent = String(e);
  }
}

/**
 * Extract persons from the input textarea by calling the backend API.
 */
async function doExtract() {
  const textInput = document.getElementById("textInput");
  const text = (textInput ? textInput.value : "").trim();

  if (!text) {
    setStatus("Please enter some text first.", "warn");
    return;
  }

  const btn = document.getElementById("btnExtract");
  if (btn) btn.disabled = true;

  setStatus("Calling service…", "hint");

  try {
    const payload = await fetchJson("/api/extract-persons", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    renderPersons(payload.persons || []);
    const rawJsonEl = document.getElementById("rawJson");
    if (rawJsonEl) {
      rawJsonEl.textContent = JSON.stringify(payload, null, 2);
    }

    const latency = payload?._meta?.latency_ms;
    const ms = typeof latency === "number" ? latency.toFixed(1) : "?";
    setStatus(`OK • latency ${ms} ms`, "ok");
  } catch (e) {
    renderPersons([]);
    const rawJsonEl = document.getElementById("rawJson");
    if (rawJsonEl) {
      rawJsonEl.textContent = "{}";
    }
    setStatus(String(e), "err");
  } finally {
    if (btn) btn.disabled = false;
    refreshMetrics();
  }
}

/**
 * Execute the automated benchmark test suite against the target service.
 */
async function runTests() {
  const btn = document.getElementById("btnRunTests");
  const outputEl = document.getElementById("testOutput");
  if (btn) btn.disabled = true;
  if (outputEl) outputEl.textContent = "Running tests…";

  try {
    const payload = await fetchJson("/api/run-tests", { method: "POST" });
    if (outputEl) {
      outputEl.textContent = JSON.stringify(payload, null, 2);
    }
  } catch (e) {
    if (outputEl) {
      outputEl.textContent = String(e);
    }
  } finally {
    if (btn) btn.disabled = false;
    refreshMetrics();
  }
}

/**
 * Load a random sample text from the embedded test dataset.
 */
function loadRandomTestText() {
  let examples = [];
  const scriptData = document.getElementById("testDatasetData");
  if (scriptData && scriptData.textContent) {
    try {
      examples = JSON.parse(scriptData.textContent);
    } catch {
      examples = [];
    }
  }

  if (!examples.length) {
    examples = [
      "Ms Mette Frederiksen is in New York today.",
      "Einstein and von Neumann meet each other.",
      "Dr. Jane Goodall spoke with Prof. Brian Cox after the event.",
    ];
  }

  const randomText = examples[Math.floor(Math.random() * examples.length)];
  const inputEl = document.getElementById("textInput");
  if (inputEl) {
    inputEl.value = randomText;
  }
  setStatus("Loaded a random test example into the text box.", "hint");
}

// Attach event listeners once DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  const btnExtract = document.getElementById("btnExtract");
  const btnClear = document.getElementById("btnClear");
  const btnRunTests = document.getElementById("btnRunTests");
  const btnLoadExample = document.getElementById("btnLoadExample");

  if (btnExtract) btnExtract.addEventListener("click", doExtract);

  if (btnClear) {
    btnClear.addEventListener("click", () => {
      const textInput = document.getElementById("textInput");
      if (textInput) textInput.value = "";
      renderPersons([]);
      const rawJsonEl = document.getElementById("rawJson");
      if (rawJsonEl) rawJsonEl.textContent = "{}";
      setStatus("Cleared.", "hint");
    });
  }

  if (btnRunTests) btnRunTests.addEventListener("click", runTests);
  if (btnLoadExample) btnLoadExample.addEventListener("click", loadRandomTestText);

  // Initial metrics fetch and recurring poll
  refreshMetrics();
  setInterval(refreshMetrics, 2500);
});

