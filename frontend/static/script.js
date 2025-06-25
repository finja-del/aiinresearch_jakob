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
    data.forEach(result => {
      container.innerHTML += `
        <div class="bg-white border border-gray-200 p-4 rounded-lg shadow-sm">
          <h2 class="text-xl font-semibold text-blue-800">${result.title}</h2>
          <p class="text-sm text-gray-700">
            Autoren: ${Array.isArray(result.authors) ? result.authors.join(", ") : result.authors || "unbekannt"}
            Jahr: ${result.date?.split("-")[0] || "—"} |
            VHB: ${result.journal_quartile || "N/A"} |
            Quelle: ${result.source || "—"}
          </p>
          <p class="text-sm mt-2">${result.abstract || "Kein Abstract vorhanden."}</p>
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
