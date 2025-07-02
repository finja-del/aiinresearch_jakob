console.log("📦 script.js loaded"); //To verify it's loading

let publicationData = [];
let yearChart;
let selectedYear = "";
let yearRange = { from: "", to: "" };

async function init() {
  const response = await axios.get("/api/search?q=");
  publicationData = response.data;
  renderYearChart(publicationData);
  performSearch();
}

async function loadCSVData() {
  try {
    const response = await fetch('results.csv');
    const csvText = await response.text();
    return parseCSV(csvText);
  } catch (error) {
    console.error("Fehler beim Laden der CSV:", error);
    return [];
  }
}

function parseCSV(csvText) {
  const lines = csvText.trim().split('\n');
  const headers = lines[0].split(',').map(h => h.trim());

  return lines.slice(1).map(line => {
    const values = line.split(',').map(v => v.trim());
    const entry = {};
    headers.forEach((h, i) => {
      entry[h] = values[i];
    });
    return entry;
  });
}

function renderYearChart(data) {
    const yearCounts = {};
  
    data.forEach(item => {
      const year = item.Date?.split("-")[0];
      if (year) {
        yearCounts[year] = (yearCounts[year] || 0) + 1;
      }
    });
  
    const allYears = Object.keys(yearCounts).map(Number).sort((a, b) => a - b);
    const minYear = allYears.length > 0 ? Math.min(...allYears) : 1950; // Random low year for low range
    const maxYear = 2025;
  
    const yearFromInput = document.getElementById("yearFrom");
    const yearToInput = document.getElementById("yearTo");

    
  
    // Eingabefelder vorbelegen, wenn leer
    if (!yearFromInput.value) yearFromInput.value = minYear;
    if (!yearToInput.value) yearToInput.value = maxYear;
  
    // Bereich für den Chart aus Eingabe lesen
    const from = parseInt(yearFromInput.value);
    const to = parseInt(yearToInput.value);
  
    const rangeYears = [];
    for (let y = from; y <= to; y++) {
      rangeYears.push(String(y));
      if (!yearCounts[y]) yearCounts[y] = 0;
    }
  
    const counts = rangeYears.map(y => yearCounts[y]);
  
    const ctx = document.getElementById("yearChart").getContext("2d");
    if (yearChart) yearChart.destroy();
  
    yearChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: rangeYears,
        datasets: [{
          label: "Paper pro Jahr",
          data: counts,
          fill: false,
          borderColor: "#2563eb",
          backgroundColor: "#60a5fa",
          tension: 0.3,
          pointBackgroundColor: rangeYears.map(y => y === selectedYear ? "#1d4ed8" : "#60a5fa"),
          pointRadius: 5
        }]
      },
      options: {
        onClick: (evt, elements) => {
          if (elements.length > 0) {
            const clickedYear = yearChart.data.labels[elements[0].index];
            selectedYear = selectedYear === clickedYear ? "" : clickedYear;
            renderYearChart(publicationData); // Update Farbpunkte
            performSearch(); // Anwenden
          }
        },
        plugins: { legend: { display: false } },
        scales: {
          x: { title: { display: true, text: "Jahr" } },
          y: { beginAtZero: true, title: { display: true, text: "Paper" } }
        }
      }
    });
  }

function updateYearRange() {
  yearRange.from = document.getElementById("yearFrom").value;
  yearRange.to = document.getElementById("yearTo").value;
  renderYearChart(publicationData);
  performSearch();
}

function resetYearFilter() {
  selectedYear = "";
  yearRange.from = "";
  yearRange.to = "";

  document.getElementById("yearFrom").value = "";
  document.getElementById("yearTo").value = "";

  renderYearChart(publicationData);
  performSearch();
}

async function performSearch() {
  const query = document.getElementById("searchInput").value.trim();
  const sortOption = document.getElementById("sortOption").value;

  const selectedGroups = [
    ...document.querySelectorAll(".vhbCheckbox"),
    ...document.querySelectorAll(".abdcCheckbox")
  ]
    .filter(cb => cb.checked)
    .map(cb => cb.value);

  const selectedSources = Array.from(document.querySelectorAll(".sourceCheckbox"))
    .filter(cb => cb.checked)
    .map(cb => cb.value);

  const yearFrom = document.getElementById("yearFrom").value;
  const yearTo = document.getElementById("yearTo").value;

  const container = document.getElementById("resultsContainer");
  container.innerHTML = "<p class='text-gray-600'>Suche läuft...</p>";

  try {
    // Compose query string
    const params = new URLSearchParams({
      q: query,
      year_from: yearFrom,
      year_to: yearTo,
      source: selectedSources.join(","),
      group: selectedGroups.join(",")
    });

    const response = await axios.get(`/api/search?${params.toString()}`);
    const data = response.data;

    if (data.length === 0) {
      container.innerHTML = "<p class='text-gray-500 text-center'>Keine Ergebnisse gefunden.</p>";
      return;
    }

    // Optional: Sort here if backend doesn't do it
    if (sortOption === "newest") {
      data.sort((a, b) => new Date(b.date) - new Date(a.date));
    } else if (sortOption === "oldest") {
      data.sort((a, b) => new Date(a.date) - new Date(b.date));
    }

    // Render
    container.innerHTML = "";
    data.forEach((result, index) => {
    const extraId = `extra-info-${index}`; // Eindeutige ID für jedes Ergebnis

    container.innerHTML += `
    <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-5 mb-6">
      <div class="flex justify-between items-start">

        <!-- Titel und Autoren -->
        <div>
          <h2 class="text-lg font-semibold text-gray-900">${result.title}</h2>
          <p class="text-sm text-gray-500 mt-1">
            ${result.date?.split("-")[0] || "—"} | 
            ${Array.isArray(result.authors) ? result.authors.join(", ") : result.authors || "unbekannt"}
          </p>
        </div>

        <!-- Relevanz und Qualität -->
        <div>
          <span class="inline-block px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
            ${result.relevance_label || "high relevance"}
          </span>
          <span class="ml-2 inline-block px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
            ${result.quality_quartile || "Q1"}
          </span>
        </div>
      </div>

      <!-- Abstract -->
      <p class="text-sm text-gray-700 mt-4 mb-4 line-clamp-3">
        ${(result.abstract && result.abstract !== "N/A") 
        ? result.abstract 
        : '<em>No abstract available.</em>'}
      </p>

      <!-- Citations und Journalname -->
      <div class="text-sm text-gray-600 space-y-1 mb-4">
          <p>
            <strong>📖</strong> ${result.citations ?? "N/A"} | 
              ${(result.journal_name && result.journal_name !== "N/A") ? result.journal_name : '<em>Unknown journal name</em>'}
            <strong>found on</strong> ${result.source || "<em>Unknown source</em>"}
          </p>
      </div>

      <!-- VHB, ABDC und Ranking -->
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

      <!-- Zusätzliche Informationen (anfangs versteckt) -->
      <div id="${extraId}" class="hidden text-sm text-gray-700 mb-4">
        <p>
          <strong>URL:</strong> ${result.url ? `<a href="${result.url}" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:text-blue-800">${result.url}</a>` : "N/A"}<br> 
          <strong>ISSN:</strong> ${result.issn || "N/A"}<br>
          <strong>eISSN:</strong> ${result.eISSN || "N/A"}<br>
          <strong>DOI:</strong> ${result.doi ? `<a href="${result.doi}" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:text-blue-800">${result.doi}</a>` : "N/A"}<br>
          <strong>Date:</strong> ${result.date || "N/A"}
        </p>
      </div>

      <!-- Button-Leiste -->
      <div class="flex justify-between items-center pt-2 border-t border-gray-200 mt-2">
        <div class="flex gap-2">
          <button class="text-sm text-gray-600 hover:text-blue-600">💾 Save</button>
          <button class="text-sm text-gray-600 hover:text-blue-600">▶️ Export</button>
          <button class="text-sm text-gray-600 hover:text-blue-600">🏷️ Tag</button>
          <button 
            onclick="document.getElementById('${extraId}').classList.toggle('hidden')" 
            class="text-sm text-gray-600 hover:text-blue-600"
          >
            🔍 More Information
          </button>
        </div>
        <button 
          class="text-sm text-blue-600 hover:underline" 
          onclick="window.open('${result.url}', '_blank')" 
          ${!result.url ? 'disabled title="Kein Link verfügbar"' : ''}
        >
          🔗 View
        </button>
      </div>
    </div>
  `;
});


    // Optional: Save for chart rendering
    publicationData = data;
    renderYearChart(publicationData);

  } catch (err) {
    console.error("Fehler bei der Suche:", err);
    container.innerHTML = "<p class='text-red-500'>Fehler bei der Suche. Bitte später erneut versuchen.</p>";
  }
}

function updateYearRange() {
    yearRange.from = document.getElementById("yearFrom").value;
    yearRange.to = document.getElementById("yearTo").value;
    renderYearChart(publicationData);
    performSearch();
  }
  

init();
