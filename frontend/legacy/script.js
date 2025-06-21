let publicationData = [];

async function init() {
    publicationData = await loadCSVData();
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

function performSearch() {
    const query = document.getElementById("searchInput").value.toLowerCase();
    const year = document.getElementById("yearFilter").value;
    const sortOption = document.getElementById("sortOption").value;

    const selectedVhb = Array.from(document.querySelectorAll(".vhbCheckbox"))
        .filter(cb => cb.checked)
        .map(cb => cb.value);

    const selectedSources = Array.from(document.querySelectorAll(".sourceCheckbox"))
        .filter(cb => cb.checked)
        .map(cb => cb.value);

    const container = document.getElementById("resultsContainer");
    container.innerHTML = "";

    let filtered = publicationData.filter(item => {
        const searchableText = `
      ${item.Title || ""}
      ${item.Authors || ""}
      ${item.Source || ""}
    `.toLowerCase();

        const matchesQuery = searchableText.includes(query);
        const matchesYear = !year || item.Date?.startsWith(year);
        const matchesVhb = selectedVhb.length === 0 || selectedVhb.includes(item.VHB); // VHB optional
        const matchesSource = selectedSources.includes(item.Source);

        return matchesQuery && matchesYear && matchesVhb && matchesSource;
    });

    if (sortOption === "newest") {
        filtered.sort((a, b) => new Date(b.Date) - new Date(a.Date));
    }
    if (sortOption === "oldest") {
        filtered.sort((a, b) => new Date(a.Date) - new Date(b.Date));
    }

    if (filtered.length === 0) {
        container.innerHTML = "<p class='text-gray-500 text-center'>Keine Ergebnisse gefunden.</p>";
        return;
    }

    filtered.forEach(result => {
        container.innerHTML += `
      <div class="bg-white border border-gray-200 p-4 rounded-lg shadow-sm">
        <h2 class="text-xl font-semibold text-blue-800">${result.Title}</h2>
        <p class="text-sm text-gray-700">
          Autoren: ${result.Authors || 'unbekannt'} |
          Jahr: ${result.Date?.split('-')[0] || '—'} |
          VHB: ${result.VHB || 'N/A'} |
          Quelle: ${result.Source || '—'}
        </p>
      </div>
    `;
    });
}

init();
