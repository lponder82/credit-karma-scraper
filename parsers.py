import datetime

from bs4 import BeautifulSoup


class ScoreBoard(object):
    bureau_names = [
        'transunion',
        'equifax'
    ]

    def __init__(self, soup):
        self.soup = soup

    @property
    def _score_box(self):
        return self.soup.find('a', {'class': 'user-score-box'})

    @property
    def _score_and_category_elements(self):
        svg = self.soup.find('svg', {'class': 'thermodial-svg'})
        return svg.find_all('text', recursive=False)[-2:]

    @property
    def score(self):
        return int(self._score_and_category_elements[0].text.strip())

    @property
    def category(self):
        return self._score_and_category_elements[1].text.strip()

    @property
    def hyperlink(self):
        return self._score_box.get('href')

    @property
    def bureau_name(self):
        for name in self.bureau_names:
            if name in self.hyperlink:
                return name
        return

    @classmethod
    def _get_score_boards(cls, soup):
        return soup.find_all('div', {'class': 'user-score-board'})

    @classmethod
    def from_response_content(cls, content):
        soup = BeautifulSoup(content, 'html.parser')
        return cls.from_soup(soup)

    @classmethod
    def from_soup(cls, soup):
        return [cls(x) for x in cls._get_score_boards(soup)]
