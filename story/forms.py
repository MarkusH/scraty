from django import forms


class StoryForm(forms.Form):
    id = forms.UUIDField(required=False)
    title = forms.CharField()
    link = forms.URLField(required=False)
