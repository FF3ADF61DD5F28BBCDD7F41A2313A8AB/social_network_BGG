from datetime import datetime as dt

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User

from .models import Post, Group, Comment
from .forms import PostForm, CommentForm


def index(request):
    post_list = (Post.objects.order_by("-pub_date").all().select_related())[:10]
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


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user).all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "profile.html",
        {"page": page, "paginator": paginator, "user": user},
    )


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(
        Post.objects.filter(author=user)
        .order_by("-pub_date")
        .all()[post_id - 1 : post_id]
    )
    post_list = user.posts.all()
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
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(
        Post.objects.filter(author=user)
        .order_by("-pub_date")
        .all()[post_id - 1 : post_id]
    )
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
    post = get_object_or_404(
        Post.objects.filter(author=user)
        .order_by("-pub_date")
        .all()[post_id - 1 : post_id]
    )
    if post.author == request.user:
        form = PostForm(
            request.POST or None, files=request.FILES or None, instance=post
        )
        if not form.is_valid():
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
