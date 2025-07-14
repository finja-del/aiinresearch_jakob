console.log("📦 script.js loaded");

// ===================================================
// 📦 Initialisierung & Globale Variablen
// ===================================================
let selectedPapers = new Map();
// zugehörige Paper-Keys generieren
function generatePaperKey(paper) {
  return btoa(
    `${paper.title}|${paper.authors}|${paper.date}|${paper.source}`
  ).substring(0, 30); // kürzt den Key etwas, optional
}
let publicationData = [];
let yearChart;
let selectedYear = "";
let yearRange = { from: "", to: "" };
// Min. Quellen Filter
let minSources = 1;    // 1 = alle, 2 = zweifach, 3 = dreifach
let lastResults = [];  // speichert API-Ergebnisse
let searchQuery = "null";
let downloadName = searchQuery;
// ===================================================
// 🚀 Initialisierung
// ===================================================

init();

async function init() {
  try {
    const response = await axios.get("/api/search?q=");
    publicationData = response.data;
    renderYearChart(publicationData);
    //performSearch();
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

//Exportieren der Chart-Daten als CSV
 async function downloadPapers() {
    if (selectedPapers.size === 0) {
        alert("Bitte wählen mindestens ein Paper aus, um es zu exportieren.");
        return;
    }
    try {
        // Annahme: publicationData enthält die PaperDTO-Liste
         const papersToExport = Array.from(selectedPapers.values()).map(paper => ({
          title: paper.title || "N/A",
          authors: paper.authors || "Unknown Author",
          abstract: paper.abstract || "N/A",
          date: paper.date || "",
          source: paper.source || "",
          sources: paper.sources || [],
          source_count: paper.source_count || 0,
          vhbRanking: paper.vhbRanking || "N/A",
          abdcRanking: paper.abdcRanking || "N/A",
          journal_name: paper.journal_name || "N/A",
          issn: paper.issn || "N/A",
          eissn: paper.eISSN || "N/A",
          doi: paper.doi || "N/A",
          url: paper.url || "N/A",
          citations: paper.citations || 0,
          journal_quartile: paper.journal_quartile || ""
      }));
        console.log("Exportiere folgende Daten:", papersToExport);
         const response = await axios.post("/api/download", papersToExport, {
            headers: {
                "Content-Type": "application/json"
            },
            responseType: "blob" // <--- WICHTIG: CSV als Blob empfangen
        });

         // Download im Browser triggern
        const blob = new Blob([response.data], { type: "text/csv" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = downloadName+".csv"; // optional dynamisch
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url); // optional: Speicher freigeben

        console.log("✅ Export erfolgreich heruntergeladen.");

    } catch (error) {
        console.error("❌ Fehler beim Export:", error);
        alert("Fehler beim Export: " + error.message);
    }
}
//toggleSelect-Funktion: Markieren/Entmarkieren von Papers
function toggleSelect(index, btn) {
  const paper = publicationData[index];
  const paperKey = generatePaperKey(paper);

  if (!selectedPapers.has(paperKey)) {
    btn.classList.add('text-green-600');
    btn.textContent = '✅ Selected';
    selectedPapers.set(paperKey, paper);
  } else {
    btn.classList.remove('text-green-600');
    btn.textContent = '◯ Select';
    selectedPapers.delete(paperKey);
  }
}

function exportPapers() {
  if (selectedPapers.size === 0) {
    alert("Please select at least one paper to export.");
    return;
  }
    document.getElementById("exportModal").classList.remove("hidden");
    renderSelectedPapersList();
  }

  function closeExportModal() {
    document.getElementById("exportModal").classList.add("hidden");
  }

  function confirmExport() {
    const filename = document.getElementById("filenameInput").value.trim();
    downloadName = filename || searchQuery;
    downloadPapers();
    closeExportModal();
  }
// Renderfunktion für die Paperliste
function renderSelectedPapersList() {
  const list = document.getElementById("selectedPapersList");
  list.innerHTML = "";

  for (const [key, paper] of selectedPapers.entries()) {
    const li = document.createElement("li");
    li.className = "flex justify-between items-center text-sm bg-gray-100 px-3 py-2 rounded";

    li.innerHTML = `
      <span class="truncate max-w-[200px]" title="${paper.title}">${paper.title}</span>
      <button onclick="removePaperByKey('${key}')" class="text-red-500 hover:text-red-1000 text-sm font-bold">–</button>
    `;

    list.appendChild(li);
  }
}

// Funktion zum Entfernen eines Papers aus der Liste
function removePaperByKey(key) {
  selectedPapers.delete(key);
  renderSelectedPapersList();
}

// ===================================================
//  Filter: VHB und ABDC Rankings
  function vhbFilter(results){
  const selectedRatings = Array.from(document.querySelectorAll(".ratingCheckbox"))
    .filter(cb => cb.checked)
    .flatMap(cb => cb.value.split("/"));

  return results.filter(p => {
    const vhbRanking = p.vhbRanking || "N/A";

    // 2. Immer rausfiltern: "N/A" und "k.R."
    if (vhbRanking === "N/A" || vhbRanking === "k.R.") return false;

    // 3. Wenn keine Auswahl: alle außer "N/A" und "k.R." anzeigen
    if (selectedRatings.length === 0) return true;

    // 4. Nur anzeigen, wenn das vhbRanking zur Auswahl passt
    return selectedRatings.includes(vhbRanking);
  });
}

function abdcFilter(results){
  const selectedRatings = Array.from(document.querySelectorAll(".ratingCheckbox"))
    .filter(cb => cb.checked)
    .flatMap(cb => cb.value.split("/")); // <– Teilt z. B. "A*/A+" in ["A*", "A+"]

  return results.filter(p => {
    const abdcRanking = p.abdcRanking || "N/A";

    if (selectedRatings.length === 0) {
      return abdcRanking !== "N/A";
    }

    return selectedRatings.includes(abdcRanking);
  });
}

function getDuplicates() {
  duplicates = 0;
  dummy = publicationData.map(paper => {
    if(paper.souerce_count >1){
      duplicates += 1;
    }})
  console.log("Anzahl der Duplikate:", duplicates);
  return duplicates
}

//KPI Dashboard
function renderDashboard() {
  kpi = {
    total_papers: publicationData.length,
    duplicates: getDuplicates(),
    a_ranked: publicationData.filter(p => p.vhbRanking === "A" || p.abdcRanking === "A" || p.vhbRanking === "A+" || p.abdcRanking ==="A*").length,
  }
  console.log("📊 KPI-Dashboard wird gerendert:", kpi);

  const dashboardEl = document.getElementById("kpi-dashboard");
  if (!dashboardEl) return;

  // Zeige Dashboard an
  dashboardEl.style.display = "block";


  // Fülle die KPI-Werte ein
  document.getElementById("total-papers").textContent = kpi.total_papers ?? "0";
  document.getElementById("duplicates").textContent = kpi.duplicates || "0";
  document.getElementById("a-ranked").textContent = kpi.a_ranked ?? "0";

  // Quellen korrekt zählen
  const sourceCounts = {};
  publicationData.forEach(paper => {
    let sources = paper.sources ?? []; // Prüfe plural sources
    if (!Array.isArray(sources) || sources.length === 0) {
      sources = [paper.source ?? "Unknown"];
    }
    sources.forEach(src => {
      sourceCounts[src] = (sourceCounts[src] || 0) + 1;
    });
  });
    // Formatierte Liste der Datenbanken
  const sourcesList = {WOS: getcountWOS(), Scopus: getcountScopus(), OpenAlex: getcountOpenAlex()};
  const sourcesEntries = Object.entries(sourcesList)
    .map(([key, value]) => `${key}: ${value}`)
  document.getElementById("sources").textContent = sourcesEntries.join(", ") || "No sources found";
}

function getcountWOS(){
  return publicationData.filter(p => p.source === "WOS").length;
}
function getcountScopus(){
  return publicationData.filter(p => p.source === "Scopus").length;
}
function getcountOpenAlex(){
  return publicationData.filter(p => p.source === "OpenAlex").length;
}

// ===================================================
// 🔍 Hauptsuche: Filter sammeln, API aufrufen, anzeigen
// ===================================================

async function performSearch() {
  const heute = new Date();         //Änderung, da 9999 fehler wirft für WOS
  const yyyy = heute.getFullYear()+1;

  const searchInput = document.getElementById("searchInput")?.value?.trim() || "";
  const yearFrom = parseInt(document.getElementById("yearFrom")?.value) || 0;
  const yearTo = parseInt(document.getElementById("yearTo")?.value) || yyyy; // Änderung: Jahr bis auf nächstes Jahr setzen
  searchQuery = [searchInput || "null", yearFrom, yearTo].join("_");
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

    lastResults = data;
    if (document.getElementById("vhbCheckbox").checked){
      lastResults = vhbFilter(lastResults);
    }
    if (document.getElementById("abdcCheckbox").checked){
      lastResults = abdcFilter(lastResults);
    }
    
    publicationData = lastResults;
    updateList(publicationData);
    renderYearChart(publicationData);
    renderDashboard();
  } catch (err) {
    alert(error.message);
    container.innerHTML = "<p class='text-red-500'>Search failed. Please try again later.</p>";
  }
}

// Neue Funktion: Filter anwenden und Cards rendern
function updateList(dataArray) {
  const container = document.getElementById("resultsContainer");
  if (!container) return;
  // --- Min. Quellen Filter anwenden ---
  const filtered = dataArray.filter(p => {
    const count = p.source_count
               ?? p.sourceCount
               ?? (Array.isArray(p.sources)
                   ? new Set(p.sources.map(s => s.toLowerCase())).size
                   : 1);
    return count >= minSources;
  });
  container.innerHTML = "";
  filtered.forEach((result, index) => {
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
            <button 
                class="text-sm text-gray-600 hover:text-blue-600"
                onclick="toggleSelect(${index}, this)"
            >
                ◯ Select
            </button>
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
            VHB: ${result.vhbRanking}
          </span>
          <span class="inline-block px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800">
            ABDC: ${result.abdcRanking}
          </span>
          <span class="inline-block px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">
            Ranking: ${result.ranking ?? "N/A"}
          </span>
        </div>
        <div class="flex flex-wrap gap-2 mb-4">
          ${(result.tags || []).map(tag => `
            <span class="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full">${tag}</span>`
        ).join("")}
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
}

// Nur die minSources-Variable aktualisieren
document.getElementById("minSources")?.addEventListener("change", (e) => {
  minSources = Number(e.target.value);
});

// Nur beim Klick auf Apply Filters rendern
document.getElementById("applyFilter")?.addEventListener("click", () => {
  if (lastResults.length) {
    updateList(lastResults);
  }
});
