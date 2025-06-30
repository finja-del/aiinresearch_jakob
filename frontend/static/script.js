// ===================================================
// 📦 Initialisierung & Globale Variablen
// ===================================================

console.log("📦 script.js loaded"); // Zum Testen, ob eingebunden

let publicationData = []; // Speichert alle geladenen Paper
let yearChart;            // Chart.js-Instanz
let selectedYear = "";    // Geklicktes Jahr im Chart
let yearRange = { from: "", to: "" }; // Jahrfilterzustand

init(); // Initialer Aufruf beim Laden

// ===================================================
// 🚀 Initialisierung & CSV-Helferfunktionen
// ===================================================

async function init() {
  const response = await axios.get("/api/search?q=");
  publicationData = response.data;
  renderYearChart(publicationData);
  performSearch(); // gleich anzeigen
}

// 🔄 CSV-Datei laden und parsen (optional, z. B. für Testzwecke)
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
    headers.forEach((h, i) => entry[h] = values[i]);
    return entry;
  });
}

// ===================================================
// 📈 Jahr-Chart: Darstellung & Interaktivität
// ===================================================

function renderYearChart(data) {
  const yearCounts = {};

  data.forEach(item => {
    const year = item.Date?.split("-")[0]; // Achtung: Schlüssel muss ggf. "date" heißen
    if (year) yearCounts[year] = (yearCounts[year] || 0) + 1;
  });

  const allYears = Object.keys(yearCounts).map(Number).sort((a, b) => a - b);
  const minYear = allYears.length > 0 ? Math.min(...allYears) : 1950;
  const maxYear = 2025;

  const yearFromInput = document.getElementById("yearFrom");
  const yearToInput = document.getElementById("yearTo");

  if (!yearFromInput.value) yearFromInput.value = minYear;
  if (!yearToInput.value) yearToInput.value = maxYear;

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
          renderYearChart(publicationData); // Visuelles Update
          performSearch();                  // Filter anwenden
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

// ===================================================
// 🔁 Jahr-Filtersteuerung (Buttons anzeigen/zurücksetzen)
// ===================================================

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

// ===================================================
// 🔍 Hauptsuche: Filter sammeln, API aufrufen, anzeigen
// ===================================================

async function performSearch() {
  const payload = {
  q: document.getElementById("searchInput").value.trim(),
  range: {
    start: parseInt(document.getElementById("yearFrom").value),
    end: parseInt(document.getElementById("yearTo").value)
  },
  source: Array.from(document.querySelectorAll(".sourceCheckbox"))
               .filter(cb => cb.checked)
               .map(cb => cb.value),
  ranking: [],  // optional: wenn du es noch nicht brauchst, weglassen oder leer
  rating: []    // optional ebenso
  };

  const response = await axios.post("/api/search", payload);
  const data = response.data;

  // const query = document.getElementById("searchInput").value.trim();
  const sortOption = document.getElementById("sortOption").value;

  // const selectedGroups = [
  //   ...document.querySelectorAll(".vhbCheckbox"),
  //   ...document.querySelectorAll(".abdcCheckbox")
  // ]
  //   .filter(cb => cb.checked)
  //   .map(cb => cb.value);

  // const selectedSources = Array.from(document.querySelectorAll(".sourceCheckbox"))
  //   .filter(cb => cb.checked)
  //   .map(cb => cb.value);

  // const yearFrom = document.getElementById("yearFrom").value;
  // const yearTo = document.getElementById("yearTo").value;

  const container = document.getElementById("resultsContainer");
  container.innerHTML = "<p class='text-gray-600'>Suche läuft...</p>";

  // try {
  //   const params = new URLSearchParams({
  //     q: query,
  //     year_from: yearFrom,
  //     year_to: yearTo,
  //     source: selectedSources.join(","),
  //     group: selectedGroups.join(",")
  //   });

  //   const response = await axios.get(`/api/search?${params.toString()}`);
  //   const data = response.data;

    if (data.length === 0) {
      container.innerHTML = "<p class='text-gray-500 text-center'>Keine Ergebnisse gefunden.</p>";
      return;
    }

    // 🧮 Optional: Sortierung im Frontend (falls Backend nicht sortiert)
    if (sortOption === "newest") {
      data.sort((a, b) => new Date(b.date) - new Date(a.date));
    } else if (sortOption === "oldest") {
      data.sort((a, b) => new Date(a.date) - new Date(b.date));
    }

    // 🖥️ Anzeige der Ergebnisse
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

    // 📊 Chart aktualisieren
    publicationData = data;
    renderYearChart(publicationData);

  // } catch (err) {
  //   console.error("Fehler bei der Suche:", err);
  //   container.innerHTML = "<p class='text-red-500'>Fehler bei der Suche. Bitte später erneut versuchen.</p>";
  // }
}
