from django.db.models import Prefetch
from django.forms.models import modelformset_factory
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .forms import CardForm, StoryForm
from .models import Card, Story, User


def serialize_card(card):
    return {
        "id": str(card.pk),
        "text": card.text,
        "status": card.status,
        "user": (
            {"name": card.user.name, "color": card.user.color} if card.user else None
        ),
    }


@ensure_csrf_cookie
def index(request):
    cards_qs = Card.objects.select_related("user")
    stories = Story.objects.filter(done=False).prefetch_related(
        Prefetch("cards", queryset=cards_qs),
    )
    context = {
        "stories": [
            {
                "id": str(story.pk),
                "title": story.title,
                "link": story.link,
                "cards": [serialize_card(card) for card in story.cards.all()],
            }
            for story in stories
        ]
    }
    return render(request, "story/board.html", context=context)


@require_POST
def save_story(request):
    form = StoryForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        story, _ = Story.objects.update_or_create(
            id=data.get("id"),
            defaults={"title": data["title"], "link": data.get("link")},
        )
        return JsonResponse(
            {"id": str(story.pk), "title": story.title, "link": story.link}
        )
    return JsonResponse(form.errors.get_json_data(), status=400)


@require_POST
def delete_story(request, id):
    Story.objects.get(id=id).delete()
    return HttpResponse(status=204)


@require_POST
def save_card(request):
    form = CardForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        if data.get("user"):
            user, _ = User.objects.get_or_create(name=data["user"])
        else:
            user = None

        if data.get("id"):
            card = Card.objects.select_related("user").get(id=data["id"])
            card.text = data["text"]
            card.story_id = data["story"]
            card.status = data["status"]
        else:
            card = Card(
                text=data["text"], story_id=data["story"], status=data["status"]
            )

        card.user = user
        card.save()

        return JsonResponse(serialize_card(card))
    return JsonResponse(form.errors.get_json_data(), status=400)


@require_POST
def delete_card(request, id):
    Card.objects.get(id=id).delete()
    return HttpResponse(status=204)


@require_POST
def move_card(request, id, story, status):
    if status in Card.Status:
        card = Card.objects.get(id=id)
        card.story_id = story
        card.status = status
        card.save()
        return JsonResponse(serialize_card(card), status=200)
    else:
        return JsonResponse({"errors": "unknown status"}, status=400)


def users(request):
    FormSet = modelformset_factory(
        User, extra=0, can_delete=True, fields=("name", "color")
    )
    if request.method == "POST":
        formset = FormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect("index")
    else:
        formset = FormSet(queryset=User.objects.all())
    return render(request, "story/users.html", context={"formset": formset})
