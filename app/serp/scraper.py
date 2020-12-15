import requests

from collections import Counter

from bs4 import BeautifulSoup

class GoogleScraper:
    base_url = 'https://google.com/search?q='
    session = requests.Session()

    _result_item_class = 'rc'
    _prefix_description_class = 'f'
    _result_stats_id = 'result-stats'

    def __init__(self, query=None, proxies=None, user_agent=None):
        if query is None:
            raise ValueError('Cannot create GoogleScraper class without query.')
        self.query = query
        if proxies:
            self.session.proxies.update(proxies)
        if user_agent:
            self.session.headers.update({'user-agent': user_agent})

    def create_url(self):
        return self.base_url + self.query.replace(' ', '+')

    def extract_stats(self, stats_div):
        ints = [s for s in stats_div.text.split() if s.isdigit()]
        return int(''.join(ints))

    def extract_link(self, div):
        anchor = div.find('a')
        link = anchor['href']
        title = anchor.find('h3').text
        return link, title

    def extract_description(self, div):
        description = div.text
        prefix = div.find('span', class_=self._prefix_description_class)
        if prefix:
            description = description.lstrip(prefix.text)
        return description

    def fetch_results(self):
        url = self.create_url()
        response = self.session.get(url)
        results = []

        if not response.ok:
            raise ValueError('Oops! Cannot fetch results.')

        bs = BeautifulSoup(response.content, "html.parser")

        words = []

        stats_div = bs.find('div', id=self._result_stats_id)
        result_stats = self.extract_stats(stats_div)

        for rc in bs.find_all('div', class_=self._result_item_class):
            divs = rc.find_all('div', recursive=False)
            if len(divs) >= 2:
                link, title = self.extract_link(divs[0])
                description = self.extract_description(divs[1])
                results.append({
                    "title": title,
                    "link": link,
                    "description": description,
                })
                words += title.split(' ')
                words += description.split(' ')


        most_common_words = Counter(words).most_common(10)

        return results, result_stats, most_common_words


