
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { FilterState } from '@/pages/Index';

interface FilterSidebarProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
}

export const FilterSidebar = ({ filters, onFiltersChange }: FilterSidebarProps) => {
  const [tempFilters, setTempFilters] = useState<FilterState>(filters);

  const vhbRankings = ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D'];
  const sources = ['OpenAlex', 'Scopus', 'Web of Science'];

  const handleVHBChange = (ranking: string, checked: boolean) => {
    const newRankings = checked
      ? [...tempFilters.vhbRankings, ranking]
      : tempFilters.vhbRankings.filter(r => r !== ranking);
    
    setTempFilters({ ...tempFilters, vhbRankings: newRankings });
  };

  const handleSourceChange = (source: string, checked: boolean) => {
    const newSources = checked
      ? [...tempFilters.sources, source]
      : tempFilters.sources.filter(s => s !== source);
    
    setTempFilters({ ...tempFilters, sources: newSources });
  };

  const applyFilters = () => {
    onFiltersChange(tempFilters);
  };

  const resetFilters = () => {
    const resetState = {
      yearRange: [2020, 2024] as [number, number],
      vhbRankings: [],
      sources: [],
      sortBy: 'year'
    };
    setTempFilters(resetState);
    onFiltersChange(resetState);
  };

  return (
    <div className="w-80 bg-white border-r border-gray-200 p-6 space-y-6 h-screen overflow-y-auto">
      <div className="space-y-6">
        <h2 className="text-xl font-semibold text-gray-900">Filter & Sortierung</h2>

        {/* Year Range */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Zeitraum</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="px-2">
              <Slider
                value={tempFilters.yearRange}
                onValueChange={(value) => setTempFilters({ ...tempFilters, yearRange: value as [number, number] })}
                min={2015}
                max={2024}
                step={1}
                className="w-full"
              />
            </div>
            <div className="flex justify-between text-sm text-gray-600">
              <span>{tempFilters.yearRange[0]}</span>
              <span>{tempFilters.yearRange[1]}</span>
            </div>
          </CardContent>
        </Card>

        {/* VHB Ranking */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">VHB-Ranking</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {vhbRankings.map((ranking) => (
              <div key={ranking} className="flex items-center space-x-2">
                <Checkbox
                  id={`vhb-${ranking}`}
                  checked={tempFilters.vhbRankings.includes(ranking)}
                  onCheckedChange={(checked) => handleVHBChange(ranking, checked as boolean)}
                />
                <Label htmlFor={`vhb-${ranking}`} className="text-sm cursor-pointer">
                  {ranking}
                </Label>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Sources */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Quellen</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {sources.map((source) => (
              <div key={source} className="flex items-center space-x-2">
                <Checkbox
                  id={`source-${source}`}
                  checked={tempFilters.sources.includes(source)}
                  onCheckedChange={(checked) => handleSourceChange(source, checked as boolean)}
                />
                <Label htmlFor={`source-${source}`} className="text-sm cursor-pointer">
                  {source}
                </Label>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Sorting */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Sortierung</CardTitle>
          </CardHeader>
          <CardContent>
            <Select
              value={tempFilters.sortBy}
              onValueChange={(value) => setTempFilters({ ...tempFilters, sortBy: value })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="year">Jahr (neueste zuerst)</SelectItem>
                <SelectItem value="title">Titel (alphabetisch)</SelectItem>
                <SelectItem value="validity">Validität (höchste zuerst)</SelectItem>
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="space-y-3">
          <Button onClick={applyFilters} className="w-full bg-blue-600 hover:bg-blue-700">
            Filter anwenden
          </Button>
          <Button onClick={resetFilters} variant="outline" className="w-full">
            Filter zurücksetzen
          </Button>
        </div>
      </div>
    </div>
  );
};
