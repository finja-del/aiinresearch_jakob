
class PaperDTO:
    def __init__(self, title, authors, abstract, date, source, vhbRanking,abdcRanking,
                 journal_name=None, issn=None, eissn=None, doi=None, url=None,
                 citations=None, journal_quartile=None):
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.date = date
        self.source = source
        self.vhbRanking = vhbRanking
        self.abdcRanking = abdcRanking
        self.journal_name = journal_name
        self.issn = issn
        self.eissn = eissn
        self.doi = doi
        self.url = url or (f"https://doi.org/{doi}" if doi else None)
        self.citations = citations
        self.journal_quartile = journal_quartile


    # API expects lowercase keys test
    # This method is used to convert the object to a dictionary format suitable for API responses
    def to_api_dict(self):
        return {
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'date': self.date,
            'source': self.source,
            'vhbRanking': self.vhbRanking,
            'abdcRanking': self.abdcRanking,
            'journal_name': self.journal_name,
            'issn': self.issn,
            'eissn': self.eissn,
            'doi': self.doi,
            'url': self.url,
            'citations': self.citations,
            'journal_quartile': self.journal_quartile
        }

