console.log("📦 script.js loaded");

// ===================================================
// 🎨 Ranking Color Helper
// ===================================================
function getRankingColor(ranking) {
  if (ranking === "A*" || ranking === "A+") {
    return "bg-purple-100 text-purple-800";
  }
  if (ranking === "A") {
    return "bg-green-200 text-green-900";
  }
  if (ranking === "B") {
    return "bg-green-100 text-green-800";
  }
  if (ranking === "C") {
    return "bg-orange-200 text-orange-800";
  }
  if (ranking === "D") {
    return "bg-red-200 text-red-800";
  }
  return "bg-gray-100 text-gray-800";
}

function getRankingClass(ranking) {
  if (ranking === "A*" || ranking === "A+") return "badge-vhb-aplus";
  if (ranking === "A") return "badge-vhb-a";
  if (ranking === "B") return "badge-vhb-b";
  if (ranking === "C") return "badge-vhb-c";
  if (ranking === "D") return "badge-vhb-d";
  return "badge-vhb-na";
}

// ===================================================
// 📦 Initialisierung & Globale Variablen
// ===================================================
let selectedPapers = new Map();
// zugehörige Paper-Keys generieren
function generatePaperKey(paper) {
  const rawString = `${paper.title}|${paper.authors}|${paper.date}|${paper.source}`;
  const utf8Safe = unescape(encodeURIComponent(rawString)); // UTF-8 → Latin1-kompatibel
  return btoa(utf8Safe).substring(0, 30);
}
let publicationData = [];
let isOfflineMode = false;
let yearChart;
let selectedYear = "";
let yearRange = { from: "", to: "" };

// === Mode-Switch Buttons und UI ===
const modeOnlineBtn = document.getElementById("modeOnlineBtn");
const modeOfflineBtn = document.getElementById("modeOfflineBtn");
const searchInput = document.getElementById("searchInput");
const searchBtn = document.querySelector('button[onclick="performSearch()"]');
const processBtn = document.getElementById("processUploadBtn");

function updateModeUI() {
  // === Dropzone & UploadInput ===
  const dropzone = document.getElementById("dropzone");
  const uploadInput = document.getElementById("uploadInput");
  // === SourceCheckboxes (Sidebar) ===
  const sourceCheckboxes = document.querySelectorAll(".sourceCheckbox");

  if (isOfflineMode) {
    // Disable search, enable process
    if (searchBtn) {
      searchBtn.disabled = true;
      searchBtn.classList.add("opacity-60", "pointer-events-none");
    }
    if (searchInput) searchInput.disabled = true;
    if (processBtn) {
      processBtn.disabled = false;
      processBtn.classList.remove("opacity-60", "pointer-events-none");
    }
    // Dropzone: aktivieren
    if (dropzone) {
      dropzone.classList.remove("opacity-60", "pointer-events-none");
    }
    if (uploadInput) {
      uploadInput.disabled = false;
    }
    // Sidebar-Checkboxen deaktivieren
    sourceCheckboxes.forEach(cb => {
      cb.disabled = true;
      cb.classList.add("opacity-60", "pointer-events-none");
    });
  } else {
    // Enable search, disable process
    if (searchBtn) {
      searchBtn.disabled = false;
      searchBtn.classList.remove("opacity-60", "pointer-events-none");
    }
    if (searchInput) searchInput.disabled = false;
    if (processBtn) {
      processBtn.disabled = true;
      processBtn.classList.add("opacity-60", "pointer-events-none");
    }
    // Dropzone: deaktivieren
    if (dropzone) {
      dropzone.classList.add("opacity-60", "pointer-events-none");
    }
    if (uploadInput) {
      uploadInput.disabled = true;
    }
    // Sidebar-Checkboxen aktivieren
    sourceCheckboxes.forEach(cb => {
      cb.disabled = false;
      cb.classList.remove("opacity-60", "pointer-events-none");
    });
  }
}

if (modeOnlineBtn && modeOfflineBtn) {

  modeOnlineBtn.addEventListener("click", function () {
    if (!isOfflineMode) return;
    resetDashboard();
    publicationData = [];
    selectedPapers.clear();
    isOfflineMode = false;
    modeOnlineBtn.classList.add("bg-blue-600", "text-white");
    modeOnlineBtn.classList.remove("bg-gray-200", "text-blue-800");
    modeOnlineBtn.style.opacity = 1;
    modeOfflineBtn.classList.remove("bg-blue-600", "text-white");
    modeOfflineBtn.classList.add("bg-gray-200", "text-blue-800");
    modeOfflineBtn.style.opacity = 0.7;
    updateModeUI();
    // NEU: Start-Info (Intro-Legende) anzeigen
    const legendEl = document.getElementById("introLegend");
    if (legendEl) legendEl.style.display = "block";
    // KEINE Suche mehr machen!
  });
  }

 modeOfflineBtn.addEventListener("click", function () {
  if (isOfflineMode) return;
  resetDashboard();
  publicationData = [];
  selectedPapers.clear();
  isOfflineMode = true;
  // ==== Filter zurücksetzen bei Upload/Offline ====
  document.getElementById("vhbCheckbox").checked = false;
  document.getElementById("abdcCheckbox").checked = false;
  Array.from(document.querySelectorAll(".ratingCheckbox")).forEach(cb => cb.checked = false);
  document.getElementById("yearFrom").value = "";
  document.getElementById("yearTo").value = "";
  document.getElementById("minSources").value = 1;
  modeOfflineBtn.classList.add("bg-blue-600", "text-white");
  modeOfflineBtn.classList.remove("bg-gray-200", "text-blue-800");
  modeOfflineBtn.style.opacity = 1;
  modeOnlineBtn.classList.remove("bg-blue-600", "text-white");
  modeOnlineBtn.classList.add("bg-gray-200", "text-blue-800");
  modeOnlineBtn.style.opacity = 0.7;
  updateModeUI();
  // HIER: Application Info immer zeigen, solange keine Ergebnisse da sind!
  const legendEl = document.getElementById("introLegend");
  if (legendEl) legendEl.style.display = "block";
  document.getElementById("uploadInput")?.focus();
});


updateModeUI();

// Min. Quellen Filter
let minSources = 1;    // 1 = alle, 2 = zweifach, 3 = dreifach
let lastResults = [];  // speichert API-Ergebnisse
let searchQuery = "null";
let downloadName = searchQuery;

// ===================================================
// 🧹 Helper: Reset Dashboard/results state
// ===================================================
function resetDashboard() {
  publicationData = [];
  selectedPapers.clear();

  const container = document.getElementById("resultsContainer");
  if (container) container.innerHTML = "";

  const dash = document.getElementById("kpi-dashboard");
  if (dash) dash.style.display = "block";

  // Striche als Platzhalter!
  document.getElementById("total-papers").textContent = "—";
  document.getElementById("duplicates").textContent   = "—";
  document.getElementById("a-ranked").textContent     = "—";
  document.getElementById("sources").innerHTML        = "—";

  // Chart auf leer rendern!
  if (yearChart) { yearChart.destroy(); yearChart = null; }
  renderYearChart([]); // <--- LEERER CHART!
}
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
        const blob = new Blob([response.data], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = downloadName+".xlsx"; // optional dynamisch
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
    renderSelectedPapersSidebar();
  } else {
    btn.classList.remove('text-green-600');
    btn.textContent = '◯ Select';
    selectedPapers.delete(paperKey);
    renderSelectedPapersSidebar();
  }
}

function exportPapers() {
  if (selectedPapers.size === 0) {
    alert("Please select at least one paper to export.");
    return;
  }
    document.getElementById("exportModal").classList.remove("hidden");
    renderSelectedPapersList();
    renderSelectedPapersSidebar();
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


//Sidebar-Funktion: Rendern der ausgewählten Papers in der Seitenleiste
function renderSelectedPapersSidebar() {
  const list = document.getElementById("selectedPapersSidebarList");
  list.innerHTML = "";

  for (const [key, paper] of selectedPapers.entries()) {
    const li = document.createElement("li");
    li.className = "flex justify-between items-center text-sm bg-gray-100 px-3 py-2 rounded";

    li.innerHTML = `
      <span class="truncate max-w-[160px]" title="${paper.title}">${paper.title}</span>
      <button onclick="removePaperByKey('${key}')" class="text-red-500 hover:text-red-700 text-sm font-bold">–</button>
    `;

    list.appendChild(li);
  }
}

// Funktion zum Entfernen eines Papers aus der Liste
function removePaperByKey(key) {
  selectedPapers.delete(key);
  renderSelectedPapersList();
  renderSelectedPapersSidebar();
}

// ===================================================
//  Filter: VHB und ABDC Rankings
function filterABCD(results){
  const selectedRatings = Array.from(document.querySelectorAll(".ratingCheckbox"))
    .filter(cb => cb.checked)
    .flatMap(cb => cb.value.split("/"));
  return results.filter(p => {
    const abdcRanking = p.abdcRanking || "N/A";
    const vhbRanking = p.vhbRanking || "N/A";
    if (vhbRanking === "N/A" || vhbRanking === "k.R." && abdcRanking === "N/A") return false;
    if (selectedRatings.length === 0) return true;
    return (selectedRatings.includes(abdcRanking) || selectedRatings.includes(vhbRanking));
})
}


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

function getDuplicates(data) {
  let duplicates = 0;
  data.forEach(paper => {
    if (paper.source && paper.source.split(" and ").length > 1) {
      duplicates += 1;
    }
  });
  return duplicates;
}

//KPI Dashboard
function renderDashboard(filteredData) {
    kpi = {
    total_papers: filteredData.length,
    duplicates: getDuplicates(filteredData),
    a_ranked: filteredData.filter(p => p.vhbRanking === "A" || p.abdcRanking === "A" || p.vhbRanking === "A+" || p.abdcRanking ==="A*").length,
  };
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
  filteredData.forEach(paper => {
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
  document.getElementById("sources").innerHTML = sourcesEntries.map(e => `<div>${e}</div>`).join("") || "No sources found";
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
  isOfflineMode = false;
  // --- Clear previous results & dashboard ---
  resetDashboard();

  // Wenn kein Suchbegriff eingegeben → Intro-Legende anzeigen und abbrechen
  const rawQuery = document.getElementById("searchInput")?.value?.trim() || "";
  if (rawQuery === "") {
    const legendEl = document.getElementById("introLegend");
    if (legendEl) legendEl.style.display = "block";
    return;     // keine API-Abfrage, altes Dashboard bleibt gelöscht
  }

  const heute = new Date();         //Änderung, da 9999 fehler wirft für WOS
  const yyyy = heute.getFullYear()+1;

  const searchInput = rawQuery;
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
    // 1️⃣  API‑Request
    const response = await axios.post("/api/search", payload, {
      headers: { "Content-Type": "application/json" }
    });
    const data = response.data;

    // Legende ein-/ausblenden je nach Trefferzahl
    const legendEl = document.getElementById("introLegend");

    if (!Array.isArray(data) || data.length === 0) {
      resetDashboard();
      renderDashboard();
      if (legendEl) legendEl.style.display = "block";
      return;
    }

// es gibt Ergebnisse → Legende ausblenden
if (legendEl) legendEl.style.display = "none";
    const sortOption = document.getElementById("sortOption")?.value;
const rankingOrder = ["A*", "A+", "A", "B", "C", "D", "N/A", "k.R."];

    if (sortOption === "newest") {
      data.sort((a, b) => new Date(b.date) - new Date(a.date));
    } else if (sortOption === "oldest") {
      data.sort((a, b) => new Date(a.date) - new Date(b.date));
    } else if (sortOption === "combined-ranking") {
      data.sort((a, b) => {
        const rankA = rankingOrder.indexOf(a.vhbRanking || a.abdcRanking || "N/A");
        const rankB = rankingOrder.indexOf(b.vhbRanking || b.abdcRanking || "N/A");
        return rankA - rankB;
      });
    }

    lastResults = data;

    const selectedRatings = Array.from(document.querySelectorAll(".ratingCheckbox"))
    .filter(cb => cb.checked)
    .flatMap(cb => cb.value.split("/")); 
    if (selectedRatings.length > 0) {
      lastResults = filterABCD(lastResults);
    }

    if (document.getElementById("vhbCheckbox").checked){
      lastResults = vhbFilter(lastResults);
    }
    if (document.getElementById("abdcCheckbox").checked){
      lastResults = abdcFilter(lastResults);
    }

    publicationData = lastResults;
    const filtered = updateList(publicationData);
    renderYearChart(filtered);
    renderDashboard(filtered);
  } catch (err) {
    alert(error.message);
    container.innerHTML = "<p class='text-red-500'>Search failed. Please try again later.</p>";
  }
}

// Neue Funktion: Filter anwenden und Cards rendern
function updateList(dataArray) {
  const yearFrom = parseInt(document.getElementById("yearFrom")?.value) || 0;
  const yearTo = parseInt(document.getElementById("yearTo")?.value) || new Date().getFullYear() + 1;
  const minSources = Number(document.getElementById("minSources")?.value) || 1;

  const vhbEnabled = document.getElementById("vhbCheckbox").checked;
  const abdcEnabled = document.getElementById("abdcCheckbox").checked;
  const selectedRatings = Array.from(document.querySelectorAll(".ratingCheckbox"))
    .filter(cb => cb.checked)
    .flatMap(cb => cb.value.split("/"));

  let filtered = [];

  // ===== OFFLINE-FILTER =====
  if (isOfflineMode) {
    filtered = dataArray.filter(paper => {
      // 1. Jahrfilter
      const pubYear = Number(String(paper.date).split("-")[0]);
      if (pubYear < yearFrom || pubYear > yearTo) return false;

      // 2. Min Source Filter
      const count = paper.source_count
          ?? paper.sourceCount
          ?? (Array.isArray(paper.sources)
              ? new Set(paper.sources.map(s => String(s).toLowerCase())).size
              : 1);
      if (count < minSources) return false;

      const vhb = (paper.vhbRanking || "").trim();
      const abdc = (paper.abdcRanking || "").trim();

      // ----- UNABHÄNGIGE, ENTPANNTE LOGIK -----

      if (vhbEnabled && abdcEnabled) {
        // Beide Rankings müssen gesetzt und gültig sein!
        if (vhb === "N/A" || vhb === "k.R." || abdc === "N/A") return false;
        if (selectedRatings.length === 0) return true;
        // Beide müssen im Rating-Set sein!
        return selectedRatings.includes(vhb) && selectedRatings.includes(abdc);
      }

      if (selectedRatings.length > 0) {
        // Nur Rating: Mindestens eines muss passen
        return selectedRatings.includes(vhb) || selectedRatings.includes(abdc);
      }
      return true; // Wenn nichts ausgewählt, alles anzeigen
    });
  }

  // Rendering wie gehabt:
  const container = document.getElementById("resultsContainer");
  if (!container) return;
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
          <span class="inline-block px-2 py-1 text-xs rounded-full ${getRankingClass(result.vhbRanking)}">
            VHB: ${result.vhbRanking || "N/A"}
          </span>
          <span class="inline-block px-2 py-1 text-xs rounded-full ${getRankingClass(result.abdcRanking)}">
            ABDC: ${result.abdcRanking || "N/A"}
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
          </p>
        </div>
        <div class="flex justify-between items-center pt-2 border-t border-gray-200 mt-2">
          <div class="flex gap-2">
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
  return filtered;
}

// Nur die minSources-Variable aktualisieren
document.getElementById("minSources")?.addEventListener("change", (e) => {
  minSources = Number(e.target.value);
});

document.getElementById("applyFilter")?.addEventListener("click", () => {
  const filtered = updateList(publicationData);
  renderYearChart(filtered);
  renderDashboard(filtered);
});

async function processUploadedFile() {
  const fileInput = document.getElementById("uploadInput");
  const file = fileInput.files[0];
  if (!file) {
    alert("Bitte wähle eine Datei aus.");
    return;
    isOfflineMode = true;
  }

  // Aktuelle Filter abrufen
  const filters = {
    q: "uploaded_file",
    source: [],
    range: {
      start: parseInt(document.getElementById("yearFrom")?.value) || 0,
      end: parseInt(document.getElementById("yearTo")?.value) || new Date().getFullYear() + 1
    },
    ranking: [],
    rating: Array.from(document.querySelectorAll(".ratingCheckbox"))
      .filter(cb => cb.checked)
      .flatMap(cb => cb.value.split("/"))
  };

  const formData = new FormData();
  formData.append("file", file);
  formData.append("filters", JSON.stringify(filters));

  const container = document.getElementById("resultsContainer");
  container.innerHTML = "<p class='text-gray-600'>Processing...</p>";
  resetDashboard();

  try {
    const response = await axios.post("/api/uploadfile", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    });

    const data = response.data;
    if (!Array.isArray(data) || data.length === 0) {
      container.innerHTML = "<p class='text-red-500'>Keine passenden Paper gefunden.</p>";
      // Intro trotzdem zeigen, da leer
      const legendEl = document.getElementById("introLegend");
      if (legendEl) legendEl.style.display = "block";
      return;
    }

// Ergebnisse da → Intro ausblenden
    const legendEl = document.getElementById("introLegend");
    if (legendEl) legendEl.style.display = "none";

    publicationData = data;
    const filtered = updateList(data);
    renderYearChart(filtered);
    renderDashboard(filtered);
    console.log("📥 Offline Upload verarbeitet:", data);

  } catch (err) {
    console.error("Fehler beim Hochladen:", err);
    container.innerHTML = "<p class='text-red-500'>Fehler beim Verarbeiten der Datei.</p>";
  }

  // Nach Upload: Process-Button deaktivieren
  const processBtn = document.querySelector('[onclick="processUploadedFile()"]');
  if (processBtn) processBtn.disabled = true;
}

// ===================================================
// 🆕 applyFilters: Entscheidet, ob Datei-Upload oder normale Suche
// ===================================================

function applyFilters() {
  if (isOfflineMode) {
    const filtered = updateList(publicationData);
    renderYearChart(filtered);
    renderDashboard(filtered);
  } else {
    performSearch();
  }
}

document.getElementById("uploadInput")?.addEventListener("change", function() {
  const processBtn = document.querySelector('[onclick="processUploadedFile()"]');
  if (processBtn) processBtn.disabled = false;
});

document.addEventListener("DOMContentLoaded", function() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("uploadInput");

  if (!dropzone || !fileInput) return;

  // Drag&Drop Support:
  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("ring-2", "ring-blue-300");
  });
  dropzone.addEventListener("dragleave", (e) => {
    e.preventDefault();
    dropzone.classList.remove("ring-2", "ring-blue-300");
  });
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("ring-2", "ring-blue-300");
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      // Automatisch Verarbeitung auslösen:
      if (typeof processUploadedFile === "function") processUploadedFile();
    }
  });
  // Klick auf Dropzone öffnet Dateiauswahl
  dropzone.addEventListener("click", () => fileInput.click());
  // Manuelle Auswahl löst auch Verarbeitung aus
  fileInput.addEventListener("change", () => {
    if (fileInput.files.length) {
      if (typeof processUploadedFile === "function") processUploadedFile();
    }
  });
});

document.getElementById("resetToOnlineBtn")?.addEventListener("click", () => {
  isOfflineMode = false;
  publicationData = [];
  resetDashboard();
  document.getElementById("searchInput").value = "";
  performSearch();
});

