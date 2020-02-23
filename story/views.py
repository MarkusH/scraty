from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.db.models import Prefetch
from django.shortcuts import render
from django.shortcuts import reverse
from django.http.response import JsonResponse, HttpResponse

from .forms import StoryForm, CardForm
from .models import Card, Story, User


@ensure_csrf_cookie
def index(request):
    cards_qs = Card.objects.select_related("user")
    stories = Story.objects.filter(done=False).prefetch_related(
        Prefetch(
            "cards",
            queryset=cards_qs.filter(status=Card.Status.TODO),
            to_attr="cards_todo",
        ),
        Prefetch(
            "cards",
            queryset=cards_qs.filter(status=Card.Status.IN_PROGRESS),
            to_attr="cards_in_progress",
        ),
        Prefetch(
            "cards",
            queryset=cards_qs.filter(status=Card.Status.VERIFY),
            to_attr="cards_verifie",
        ),
        Prefetch(
            "cards",
            queryset=cards_qs.filter(status=Card.Status.DONE),
            to_attr="cards_done",
        ),
    )
    context = {"stories": stories, "urls": {"save_story": reverse("save_story")}}
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

        return JsonResponse(
            {
                "id": str(card.pk),
                "text": card.text,
                "user": (
                    {"name": card.user.name, "color": card.user.color}
                    if card.user
                    else None
                ),
            }
        )
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
        return JsonResponse({}, status=200)
    else:
        return JsonResponse({"errors": "unknown status"}, status=400)
