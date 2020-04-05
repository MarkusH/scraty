from django.conf import settings
from django.db.models import Prefetch
from django.forms.models import modelformset_factory
from django.http import QueryDict
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_POST

from .forms import CardForm, CardMoveForm, StoryForm
from .models import Card, Story, User


def serialize_card(card):
    return {
        "id": str(card.pk),
        "text": card.text,
        "status": card.status,
        "user": (
            {"name": card.user.name, "color": card.user.color}
            if card.user
            else {"name": "", "color": ""}
        ),
    }


def serialize_story(story, with_cards=False):
    data = {"id": str(story.pk), "title": story.title, "link": story.link}
    if with_cards:
        data["cards"] = [serialize_card(card) for card in story.cards.all()]
    return data


@ensure_csrf_cookie
def index(request):
    context = {"debug": settings.DEBUG}
    return render(request, "story/board.html", context=context)


@require_http_methods(["GET", "POST"])
def stories_view(request):
    if request.method == "POST":
        form = StoryForm(request.POST)
        if form.is_valid():
            story = form.save()
            return JsonResponse(serialize_story(story))
        return JsonResponse(form.errors.get_json_data(), status=400)
    else:
        cards_qs = Card.objects.filter(done=False).select_related("user")
        stories = Story.objects.filter(done=False).prefetch_related(
            Prefetch("cards", queryset=cards_qs),
        )
        data = {
            "stories": [serialize_story(story, with_cards=True) for story in stories],
        }
        return JsonResponse(data)


@require_http_methods(["PUT", "DELETE"])
def stories_detail_view(request, id):
    if request.method == "DELETE":
        story = get_object_or_404(Story, id=id, done=False)
        story.done = True
        story.save()
        return HttpResponse(status=204)
    elif request.method == "PUT":
        story = get_object_or_404(Story, id=id, done=False)
        form = StoryForm(QueryDict(request.body), instance=story)
        if form.is_valid():
            story = form.save()
            return JsonResponse(serialize_story(story))
        return JsonResponse(form.errors.get_json_data(), status=400)
    else:
        return HttpResponse(status=405)


@require_POST
def cards_view(request):
    form = CardForm(request.POST)
    if form.is_valid():
        card = form.save()
        return JsonResponse(serialize_card(card))
    return JsonResponse(form.errors.get_json_data(), status=400)


@require_http_methods(["PUT", "DELETE"])
def cards_detail_view(request, id):
    if request.method == "DELETE":
        card = get_object_or_404(Card, id=id, done=False)
        card.done = True
        card.save()
        return HttpResponse(status=204)
    elif request.method == "PUT":
        card = get_object_or_404(Card, id=id, done=False)
        form = CardForm(QueryDict(request.body), instance=card)
        if form.is_valid():
            card = form.save()
            return JsonResponse(serialize_card(card))
        return JsonResponse(form.errors.get_json_data(), status=400)
    else:
        return HttpResponse(status=405)


@require_POST
def cards_move_view(request, id):
    card = get_object_or_404(Card, id=id, done=False)
    form = CardMoveForm(request.POST, instance=card)
    if form.is_valid():
        card = form.save()
        return JsonResponse(serialize_card(card))
    return JsonResponse(form.errors.get_json_data(), status=400)


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
