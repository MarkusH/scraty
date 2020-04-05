from django import forms

from .models import Card, Story, User


class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ["link", "title"]


class CardForm(forms.ModelForm):
    user = forms.CharField(required=False)

    class Meta:
        model = Card
        fields = ["status", "story", "text"]

    def save(self, commit=True):
        username = self.cleaned_data.get("user")
        if username:
            self.instance.user, _ = User.objects.get_or_create(name=username)
        else:
            self.instance.user = None
        return super().save(commit=commit)


class CardMoveForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ["status", "story"]
