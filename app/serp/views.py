from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic.detail import DetailView

from .forms import SearchForm
from .helpers import extract_ip_address
from .models import SearchRequest, Resusult
from .scraper import GoogleScraper


class SearchView(FormView):
    model = SearchRequest
    template_name = 'search_view.html'
    form_class = SearchForm

    def form_valid(self, form):
        query = form.cleaned_data.get('query')

        try:
            obj = SearchRequest.objects.get_from_cache(query, self.request)
        except SearchRequest.DoesNotExist:
            scraper = GoogleScraper(
                query,
                user_agent=form.cleaned_data.get('user_agent', None),
            )
            results, stats, most_common_words = scraper.fetch_results()

            words = [item[0] for item in most_common_words]
            obj = self.save_results(form.cleaned_data, results, stats, words)

        return HttpResponseRedirect(self.get_success_url(obj.pk))

    def save_results(self, cleaned_data, results, stats, most_common_words):
        ip = extract_ip_address(self.request)
        search_request = SearchRequest.objects\
            .create(ip=ip, results=stats, most_common_words=most_common_words,
                    **cleaned_data)

        objs = []
        for idx, result in enumerate(results):
            objs.append(Resusult(request=search_request, order=idx, **result))
        Resusult.objects.bulk_create(objs)

        return search_request

    def get_success_url(self, pk):
        return reverse_lazy('results-view', kwargs={'pk': pk})


class ResultsSearchView(DetailView):
    model = SearchRequest
    template_name = 'search_view.html'
    form_class = SearchForm

    def get_queryset(self):
        return SearchRequest.objects.active()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_init_data = {
            'query': self.object.query,
            'user_agent': self.object.user_agent,
        }
        form = self.form_class(initial=form_init_data)
        context.update({'form': form})
        return context


def handler404(request, *args, **argv):
    return redirect('search-view')
