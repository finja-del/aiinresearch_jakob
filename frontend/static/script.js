console.log("📦 script.js loaded");

// ===================================================
// 📦 Initialisierung & Globale Variablen
// ===================================================

let publicationData = [];
let yearChart;
let selectedYear = "";
let yearRange = { from: "", to: "" };

// ===================================================
// 🚀 Initialisierung
// ===================================================

init();

async function init() {
  try {
    const response = await axios.get("/api/search?q=");
    publicationData = response.data;
    renderYearChart(publicationData);
    performSearch();
  } catch (err) {
    console.error("Initial load failed:", err);
  }
}

// ===================================================
// 📈 Jahr-Chart: Darstellung & Interaktivität
// ===================================================

function renderYearChart(data) {
  const yearCounts = {};

  data.forEach(item => {
    const year = item.date?.split("-")[0];
    if (year) {
      yearCounts[year] = (yearCounts[year] || 0) + 1;
    }
  });

  const years = Object.keys(yearCounts);
  const counts = Object.values(yearCounts);

  const ctx = document.getElementById("yearChart")?.getContext("2d");
  if (!ctx) {
    console.error("yearChart Canvas not found");
    return;
  }

  if (yearChart) yearChart.destroy();

  yearChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: years,
      datasets: [{
        label: "Papers per Year",
        data: counts,
        backgroundColor: "#60a5fa",
        borderColor: "#2563eb",
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}

// ===================================================
// 🔍 Hauptsuche: Filter sammeln, API aufrufen, anzeigen
// ===================================================

async function performSearch() {
  const searchInput = document.getElementById("searchInput")?.value?.trim() || "";
  const yearFrom = parseInt(document.getElementById("yearFrom")?.value) || 0;
  const yearTo = parseInt(document.getElementById("yearTo")?.value) || 9999;

  const payload = {
    q: searchInput,
    range: { start: yearFrom, end: yearTo },
    source: Array.from(document.querySelectorAll(".sourceCheckbox"))
      .filter(cb => cb.checked)
      .map(cb => cb.value),
    ranking: [],
    rating: []
  };

  const container = document.getElementById("resultsContainer");
  if (!container) {
    console.error("Results container not found");
    return;
  }

  container.innerHTML = "<p class='text-gray-600'>Loading...</p>";

  try {
    const response = await axios.post("/api/search", payload);
    const data = response.data;

    if (!Array.isArray(data) || data.length === 0) {
      container.innerHTML = "<p class='text-gray-500 text-center'>No results found.</p>";
      return;
    }

    const sortOption = document.getElementById("sortOption")?.value;

    if (sortOption === "newest") {
      data.sort((a, b) => new Date(b.date) - new Date(a.date));
    } else if (sortOption === "oldest") {
      data.sort((a, b) => new Date(a.date) - new Date(b.date));
    }

    container.innerHTML = "";
    data.forEach((result, index) => {
      const extraId = `extra-info-${index}`;
      container.innerHTML += `
        <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-5 mb-6">
          <div class="flex justify-between items-start">
            <div>
              <h2 class="text-lg font-semibold text-gray-900">${result.title}</h2>
              <p class="text-sm text-gray-500 mt-1">
                ${result.date?.split("-")[0] || "—"} |
                ${Array.isArray(result.authors) ? result.authors.join(", ") : result.authors || "Unknown"}
              </p>
            </div>
            <div>
              <span class="inline-block px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                ${result.relevance_label || "high relevance"}
              </span>
              <span class="ml-2 inline-block px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                ${result.quality_quartile || "Q1"}
              </span>
            </div>
          </div>
          <p class="text-sm text-gray-700 mt-4 mb-4 line-clamp-3">
            ${(result.abstract && result.abstract !== "N/A") 
              ? result.abstract 
              : '<em>No abstract available.</em>'}
          </p>
          <div class="text-sm text-gray-600 space-y-1 mb-4">
            <p>
              <strong>📖</strong> ${result.citations ?? "N/A"} |
              ${result.journal_name || '<em>Unknown journal</em>'} |
              <strong>found on</strong> ${result.source || "<em>Unknown source</em>"}
            </p>
          </div>
          <div class="flex flex-wrap gap-2 mt-2 mb-4">
            <span class="inline-block px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800">
              VHB: ${result.journal_quartile || "N/A"}
            </span>
            <span class="inline-block px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800">
              ABDC: ${result.journal_quartile || "N/A"}
            </span>
            <span class="inline-block px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">
              Ranking: ${result.ranking ?? "N/A"}
            </span>
          </div>
          <div class="flex flex-wrap gap-2 mb-4">
            ${(result.tags || []).map(tag => `
              <span class="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full">${tag}</span>
            `).join("")}
          </div>
          <div id="${extraId}" class="hidden text-sm text-gray-700 mb-4">
            <p>
              <strong>URL:</strong> ${result.url ? `<a href="${result.url}" target="_blank" class="text-blue-600 underline">${result.url}</a>` : "N/A"}<br>
              <strong>ISSN:</strong> ${result.issn || "N/A"}<br>
              <strong>eISSN:</strong> ${result.eISSN || "N/A"}<br>
              <strong>DOI:</strong> ${result.doi ? `<a href="${result.doi}" target="_blank" class="text-blue-600 underline">${result.doi}</a>` : "N/A"}<br>
              <strong>Date:</strong> ${result.date || "N/A"}
            </p>
          </div>
          <div class="flex justify-between items-center pt-2 border-t border-gray-200 mt-2">
            <div class="flex gap-2">
              <button class="text-sm text-gray-600 hover:text-blue-600">💾 Save</button>
              <button class="text-sm text-gray-600 hover:text-blue-600">▶️ Export</button>
              <button class="text-sm text-gray-600 hover:text-blue-600">🏷️ Tag</button>
              <button 
                onclick="document.getElementById('${extraId}').classList.toggle('hidden')" 
                class="text-sm text-gray-600 hover:text-blue-600"
              >
                🔍 More Info
              </button>
            </div>
            <button 
              class="text-sm text-blue-600 hover:underline" 
              onclick="window.open('${result.url}', '_blank')" 
              ${!result.url ? 'disabled title="No link available"' : ''}
            >
              🔗 View
            </button>
          </div>
        </div>
      `;
    });

    publicationData = data;
    renderYearChart(publicationData);
  } catch (err) {
    console.error("Search error:", err);
    container.innerHTML = "<p class='text-red-500'>Search failed. Please try again later.</p>";
  }
}
