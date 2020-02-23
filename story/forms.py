from django import forms
from .models import Card


class StoryForm(forms.Form):
    id = forms.UUIDField(required=False)
    title = forms.CharField()
    link = forms.URLField(required=False)


class CardForm(forms.Form):
    id = forms.UUIDField(required=False)
    text = forms.CharField()
    story = forms.UUIDField()
    user = forms.CharField(required=False)
    status = forms.ChoiceField(choices=Card.Status.choices)
