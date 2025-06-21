
import { useState, useMemo } from 'react';
import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FilterSidebar } from '@/components/FilterSidebar';
import { LiteratureCard } from '@/components/LiteratureCard';

// Sample literature data structure
const sampleLiterature = [
  {
    id: 1,
    title: "Digital Transformation in Organizations: A Systematic Literature Review",
    authors: ["Schmidt, M.", "Mueller, J.", "Weber, A."],
    year: 2023,
    source: "Scopus",
    vhbRanking: "A",
    validityScore: "high",
    epistemicFlags: ["peer_reviewed", "strong_method"],
    abstract: "This study examines digital transformation processes in modern organizations..."
  },
  {
    id: 2,
    title: "Machine Learning Applications in Business Process Management",
    authors: ["Johnson, K.", "Liu, X."],
    year: 2022,
    source: "Web of Science",
    vhbRanking: "B",
    validityScore: "medium",
    epistemicFlags: ["peer_reviewed", "ambiguous_theory"],
    abstract: "An analysis of machine learning integration in business processes..."
  },
  {
    id: 3,
    title: "Sustainability Metrics in Supply Chain Management",
    authors: ["Anderson, P.", "Brown, S.", "Davis, L."],
    year: 2024,
    source: "OpenAlex",
    vhbRanking: "C",
    validityScore: "low",
    epistemicFlags: ["no_peer_review", "weak_method"],
    abstract: "This paper explores sustainability measurement approaches..."
  },
  {
    id: 4,
    title: "Artificial Intelligence Ethics in Business Decision Making",
    authors: ["Taylor, R.", "Wilson, M."],
    year: 2023,
    source: "Scopus",
    vhbRanking: "A+",
    validityScore: "high",
    epistemicFlags: ["peer_reviewed", "strong_method", "robust_theory"],
    abstract: "An examination of ethical considerations in AI-driven business decisions..."
  },
  {
    id: 5,
    title: "Blockchain Technology in Financial Services: Challenges and Opportunities",
    authors: ["Garcia, C.", "Martinez, D.", "Lopez, F."],
    year: 2021,
    source: "Web of Science",
    vhbRanking: "B+",
    validityScore: "medium",
    epistemicFlags: ["peer_reviewed", "limited_sample"],
    abstract: "This research investigates blockchain implementation in financial institutions..."
  }
];

export interface FilterState {
  yearRange: [number, number];
  vhbRankings: string[];
  sources: string[];
  sortBy: string;
}

const Index = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<FilterState>({
    yearRange: [2020, 2024],
    vhbRankings: [],
    sources: [],
    sortBy: 'year'
  });

  const filteredLiterature = useMemo(() => {
    let filtered = sampleLiterature.filter(item => {
      // Search filter
      const matchesSearch = searchTerm === '' || 
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.authors.some(author => author.toLowerCase().includes(searchTerm.toLowerCase())) ||
        item.abstract.toLowerCase().includes(searchTerm.toLowerCase());

      // Year filter
      const matchesYear = item.year >= filters.yearRange[0] && item.year <= filters.yearRange[1];

      // VHB ranking filter
      const matchesVHB = filters.vhbRankings.length === 0 || filters.vhbRankings.includes(item.vhbRanking);

      // Source filter
      const matchesSource = filters.sources.length === 0 || filters.sources.includes(item.source);

      return matchesSearch && matchesYear && matchesVHB && matchesSource;
    });

    // Sort results
    switch (filters.sortBy) {
      case 'year':
        filtered.sort((a, b) => b.year - a.year);
        break;
      case 'title':
        filtered.sort((a, b) => a.title.localeCompare(b.title));
        break;
      case 'validity':
        const validityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
        filtered.sort((a, b) => validityOrder[b.validityScore as keyof typeof validityOrder] - validityOrder[a.validityScore as keyof typeof validityOrder]);
        break;
      default:
        break;
    }

    return filtered;
  }, [searchTerm, filters]);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex w-full">
        {/* Left Sidebar - Filters */}
        <FilterSidebar filters={filters} onFiltersChange={setFilters} />
        
        {/* Main Content Area */}
        <div className="flex-1 p-6 lg:p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-blue-900 mb-2">
              Literatur-Explorer
            </h1>
            <p className="text-gray-600 mb-6">
              Evidenzbasierte Navigation durch strukturierte Literaturlandschaften
            </p>
            
            {/* Search Bar */}
            <div className="relative max-w-2xl">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <Input
                type="text"
                placeholder="Titel, Autor:innen oder Schlüsselwörter durchsuchen..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 py-3 text-lg"
              />
            </div>
          </div>

          {/* Results Summary */}
          <div className="mb-6">
            <div className="flex items-center justify-between">
              <p className="text-gray-600">
                <span className="font-semibold text-blue-900">{filteredLiterature.length}</span> Publikationen gefunden
              </p>
              <Badge variant="outline" className="text-sm">
                Epistemisch validiert
              </Badge>
            </div>
          </div>

          {/* Literature Results */}
          <div className="space-y-4">
            {filteredLiterature.length === 0 ? (
              <Card className="p-8 text-center">
                <CardContent>
                  <p className="text-gray-500 text-lg">
                    Keine Publikationen gefunden. Versuchen Sie andere Suchbegriffe oder Filter.
                  </p>
                </CardContent>
              </Card>
            ) : (
              filteredLiterature.map((item) => (
                <LiteratureCard key={item.id} literature={item} />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
