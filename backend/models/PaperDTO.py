
class PaperDTO:
    def __init__(self, title, authors, abstract, date, source, quality_score,
                 journal_name=None, issn=None, eissn=None, doi=None, url=None,
                 citations=None, journal_quartile=None):
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.date = date
        self.source = source
        self.quality_score = quality_score
        self.journal_name = journal_name
        self.issn = issn
        self.eissn = eissn
        self.doi = doi
        self.url = url or (f"https://doi.org/{doi}" if doi else None)
        self.citations = citations
        self.journal_quartile = journal_quartile

    def to_dict(self):
        """Gibt das Paper als Dictionary zurück für CSV-Export"""
        return {
            'Title': self.title,
            'Authors': self.authors,
            'Abstract': self.abstract,
            'Date': self.date,
            'Source': self.source,
            'QualityScore': self.quality_score,
            'JournalName': self.journal_name or 'N/A',
            'ISSN': self.issn or 'N/A',
            'eISSN': self.eissn or 'N/A',
            'DOI': self.doi or 'N/A',
            'URL': self.url or 'N/A',
            'Citations': self.citations if self.citations is not None else 'N/A',
            'Quartile': self.journal_quartile or 'N/A'
        }
