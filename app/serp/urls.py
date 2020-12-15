from django.urls import path

from . import views


urlpatterns = [
    path('', views.SearchView.as_view(), name='search-view'),
    path('<pk>/', views.ResultsSearchView.as_view(), name='results-view'),
]
