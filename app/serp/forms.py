from django import forms

from .consts import UA_LIST
from .models import SearchRequest


class SearchForm(forms.ModelForm):
    user_agent = forms.ChoiceField(choices=UA_LIST)

    class Meta:
        model = SearchRequest
        fields = ('query', 'user_agent')
