from unittest import mock

from http import HTTPStatus
from django.conf import settings
from django.test import TestCase
from django.utils.timezone import now, timedelta

from .consts import CHROME
from serp.models import SearchRequest

RESULTS = [
    {
        'title': 'Test title',
        'description': 'Lorem ipsum...',
        'link': 'http://example.com',
    }
]
STATS = 1
MOST_COMMON_WORDS = ['aaa', 'bbb', 'ccc']
SCRAPER_RESULT = (RESULTS, STATS, MOST_COMMON_WORDS,)
IP = '127.0.0.1'

class SearchTests(TestCase):

    @mock.patch('serp.scraper.GoogleScraper.fetch_results')
    def test_post_query(self, mock_google_scraper):
        query = 'Python Unit Tests'

        mock_google_scraper.return_value = SCRAPER_RESULT

        response = self.client.post(
            '/', data={'query': query, 'user_agent': CHROME}
        )

        mock_google_scraper.assert_called_once()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(SearchRequest.objects.all().count(), 1)

        obj = SearchRequest.objects.all().first()
        self.assertEqual(obj.query, query)
        self.assertEqual(obj.user_agent, CHROME)
        self.assertEqual(obj.search_results.all().count(), 1)

        result = obj.search_results.all().first()
        self.assertEqual(result.title, RESULTS[0]['title'])
        self.assertEqual(result.description, RESULTS[0]['description'])
        self.assertEqual(result.link, RESULTS[0]['link'])

    def test_get_from_history(self):
        query = 'Python Unit Tests'
        obj = SearchRequest.objects\
            .create(ip=IP, query=query, user_agent=CHROME, results=STATS)

        response = self.client.get(f'/{obj.pk}/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response,
            f'<h4>Liczba wyników: <span class="badge badge-secondary">{STATS}</span></h4>',
            html=True,
        )

    def test_get_from_history_expired_item(self):
        query = 'Python Unit Tests'
        created_at = now() - timedelta(minutes=settings.SEARCH_CACHE_TIMEOUT + 10)

        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=created_at)):
            obj = SearchRequest.objects\
                .create(ip=IP, query=query, user_agent=CHROME, results=STATS)

        response = self.client.get(f'/{obj.pk}/')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_get_from_history_not_found(self):
        response = self.client.get("/1/")

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
