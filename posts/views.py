from datetime import datetime as dt

from django.views.decorators.cache import cache_page
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User

from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm


@cache_page(20)
def index(request):
    post_list = Post.objects.order_by("-pub_date").all().select_related()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {"page": page, "paginator": paginator},
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {"group": group, "page": page, "paginator": paginator},
    )


@login_required()
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(
            request,
            "new_post.html",
            {"form": form},
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("/")


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    post_list = user.posts.all().select_related("pk")
    count_all_posts = post_list.count()
    form = CommentForm(instance=None)
    items = Comment.objects.filter(post=post)
    return render(
        request,
        "post.html",
        {
            "post": post,
            "author": post.author,
            "count_all_posts": count_all_posts,
            "items": items,
            "form": form,
            "post_id": post_id,
        },
    )


@login_required()
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect("post", username=username, post_id=post_id)


@login_required()
def post_edit(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=user, pk=post_id)
    if post.author == request.user:
        form = PostForm(
            request.POST or None, files=request.FILES or None, instance=post
        )
        if not form.is_valid() and request.method=="POST":
            return render(
                request,
                "new_post.html",
                {"form": form, "flag_edit": True},
            )
        post = form.save(commit=False)
        post.author = request.user
        post.pub_date = dt.now()
        post.save()
    return redirect(f"/{username}/{post_id}/")


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404,
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user).all().select_related()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    if (
        Follow.objects.filter(user__username=request.user)
        .filter(author__username=username)
        .exists()
    ):
        flag_subscribe = True
    else:
        flag_subscribe = False
    count_subscribers = Follow.objects.filter(author__username=username).count()
    count_subscriptions = Follow.objects.filter(user__username=username).count()
    return render(
        request,
        "profile.html",
        {
            "page": page,
            "paginator": paginator,
            "user": user,
            "flag_subscribe": flag_subscribe,
            "count_subscribers": count_subscribers,
            "count_subscriptions": count_subscriptions,
        },
    )


@login_required
def follow_index(request):
    # post_list = Post.objects.filter(author__follower__author=request.user)
    post_list = Post.objects.filter(author__following__user=request.user)
    if not post_list:
        return render(
            request,
            "follow.html",
            {},
        )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "follow.html",
        {"page": page, "paginator": paginator},
    )


@login_required
def profile_follow(request, username):
    Follow.objects.create(
        user=User.objects.get(username=request.user),
        author=User.objects.get(username=username),
    )
    return redirect(f"/{username}/")


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(user__username=request.user).filter(
        author__username=username
    ).delete()
    return redirect(f"/{username}/")
