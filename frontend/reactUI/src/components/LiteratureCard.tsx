
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Eye, MessageSquare, Star } from 'lucide-react';

interface Literature {
  id: number;
  title: string;
  authors: string[];
  year: number;
  source: string;
  vhbRanking: string;
  validityScore: 'high' | 'medium' | 'low';
  epistemicFlags: string[];
  abstract: string;
}

interface LiteratureCardProps {
  literature: Literature;
}

export const LiteratureCard = ({ literature }: LiteratureCardProps) => {
  const getValidityColor = (score: string) => {
    switch (score) {
      case 'high':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getVHBColor = (ranking: string) => {
    if (ranking.includes('A')) return 'bg-blue-100 text-blue-800 border-blue-200';
    if (ranking.includes('B')) return 'bg-purple-100 text-purple-800 border-purple-200';
    if (ranking.includes('C')) return 'bg-orange-100 text-orange-800 border-orange-200';
    return 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getFlagLabel = (flag: string) => {
    const labels: { [key: string]: string } = {
      'peer_reviewed': 'Peer-Review',
      'strong_method': 'Starke Methodik',
      'robust_theory': 'Robuste Theorie',
      'no_peer_review': 'Kein Peer-Review',
      'weak_method': 'Schwache Methodik',
      'ambiguous_theory': 'Unklare Theorie',
      'limited_sample': 'Begrenzte Stichprobe'
    };
    return labels[flag] || flag;
  };

  return (
    <Card className="hover:shadow-md transition-shadow duration-200 border-l-4 border-l-blue-500">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-blue-900 leading-tight hover:text-blue-700 cursor-pointer transition-colors">
              {literature.title}
            </h3>
            <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-gray-600">
              <span>{literature.authors.join(', ')}</span>
              <span>•</span>
              <span>{literature.year}</span>
              <span>•</span>
              <span>{literature.source}</span>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <Badge className={getVHBColor(literature.vhbRanking)}>
              VHB {literature.vhbRanking}
            </Badge>
            <Badge className={getValidityColor(literature.validityScore)}>
              {literature.validityScore === 'high' ? 'Hoch' : 
               literature.validityScore === 'medium' ? 'Mittel' : 'Niedrig'}
            </Badge>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <p className="text-gray-700 mb-4 leading-relaxed">
          {literature.abstract}
        </p>
        
        {/* Epistemic Flags */}
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Epistemische Indikatoren</h4>
          <div className="flex flex-wrap gap-2">
            {literature.epistemicFlags.map((flag) => (
              <Badge
                key={flag}
                variant="outline"
                className={`text-xs ${
                  flag.includes('no_') || flag.includes('weak_') || flag.includes('ambiguous_') || flag.includes('limited_')
                    ? 'border-red-300 text-red-700 bg-red-50'
                    : 'border-green-300 text-green-700 bg-green-50'
                }`}
              >
                {getFlagLabel(flag)}
              </Badge>
            ))}
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="flex items-center gap-3 pt-3 border-t border-gray-100">
          <Button variant="outline" size="sm" className="flex items-center gap-2">
            <Eye className="h-4 w-4" />
            Details
          </Button>
          <Button variant="outline" size="sm" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            Kommentieren
          </Button>
          <Button variant="outline" size="sm" className="flex items-center gap-2">
            <Star className="h-4 w-4" />
            Validieren
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
