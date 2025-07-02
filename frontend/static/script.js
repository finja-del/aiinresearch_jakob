console.log("📦 script.js loaded");

let publicationData = [];
let yearChart;
let selectedYear = "";
let yearRange = { from: "", to: "" };

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

function selectAllRatings() {
  document.querySelectorAll(".rankingSourceCheckbox, .ratingCheckbox").forEach(cb => cb.checked = true);
}

function deselectAllRatings() {
  document.querySelectorAll(".rankingSourceCheckbox, .ratingCheckbox").forEach(cb => cb.checked = false);
}


function renderYearChart(data) {
  const yearCounts = {};
  data.forEach(item => {
    const year = item.date?.split("-")[0];
    if (year) {
      yearCounts[year] = (yearCounts[year] || 0) + 1;
    }
  });

  const allYears = Object.keys(yearCounts).map(Number).sort((a, b) => a - b);
  const minYear = allYears.length > 0 ? Math.min(...allYears) : 2000;
  const maxYear = 2025;

  const yearFromInput = document.getElementById("yearFrom");
  const yearToInput = document.getElementById("yearTo");

  if (!yearFromInput.value) yearFromInput.value = minYear;
  if (!yearToInput.value) yearToInput.value = maxYear;

  const from = parseInt(yearFromInput.value);
  const to = parseInt(yearToInput.value);

  yearRange.from = from;
  yearRange.to = to;

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
        label: "Papers per Year",
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
          renderYearChart(publicationData);
          performSearch();
        }
      },
      plugins: { legend: { display: false } },
      scales: {
        x: { title: { display: true, text: "Year" } },
        y: { beginAtZero: true, title: { display: true, text: "Papers" } }
      }
    }
  });
}

async function performSearch() {
  const query = document.getElementById("searchInput").value.trim();
  const sortOption = document.getElementById("sortOption").value;

  const selectedSources = Array.from(document.querySelectorAll(".sourceCheckbox"))
    .filter(cb => cb.checked)
    .map(cb => cb.value);

  const selectedRankingSources = Array.from(document.querySelectorAll(".rankingSourceCheckbox"))
    .filter(cb => cb.checked)
    .map(cb => cb.value);

  const selectedRatings = Array.from(document.querySelectorAll(".ratingCheckbox"))
    .filter(cb => cb.checked)
    .map(cb => cb.value);

  const yearFrom = document.getElementById("yearFrom").value;
  const yearTo = document.getElementById("yearTo").value;

  const container = document.getElementById("resultsContainer");
  container.innerHTML = "<p class='text-gray-600'>Loading...</p>";

  try {
    const params = new URLSearchParams({
      q: query,
      year_from: yearFrom,
      year_to: yearTo,
      source: selectedSources.join(","),
      ranking: selectedRankingSources.join(","),
      rating: selectedRatings.join(",")
    });

    const response = await axios.get(`/api/search?${params.toString()}`);
    const data = response.data;

    if (!Array.isArray(data) || data.length === 0) {
      container.innerHTML = "<p class='text-gray-500 text-center'>No results found.</p>";
      return;
    }

    if (sortOption === "newest") {
      data.sort((a, b) => new Date(b.date) - new Date(a.date));
    } else if (sortOption === "oldest") {
      data.sort((a, b) => new Date(a.date) - new Date(b.date));
    }

    container.innerHTML = "";
    data.forEach(result => {
      container.innerHTML += `
        <div class="bg-white border border-gray-200 p-4 rounded-lg shadow-sm">
          <h2 class="text-xl font-semibold text-blue-800">${result.title}</h2>
          <p class="text-sm text-gray-700">
            Authors: ${Array.isArray(result.authors) ? result.authors.join(", ") : result.authors || "Unknown"}<br>
            Year: ${result.date?.split("-")[0] || "—"} |
            Ranking: ${result.journal_quartile || "N/A"} |
            Source: ${result.source || "—"}
          </p>
          <p class="text-sm mt-2">${result.abstract || "No abstract available."}</p>
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

init();
