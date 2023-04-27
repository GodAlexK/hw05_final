from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page


from .forms import PostForm, CommentForm
from .models import Post, Group, Follow, User
from .utils import get_paginator


@cache_page(20, key_prefix='index_page')
def index(request):
    posts = Post.objects.all()
    context = {
        'page_obj': get_paginator(posts, request),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()
    context = {
        'group': group,
        'page_obj': get_paginator(posts, request),
    }
    return render(request, 'posts/group_list.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None
                    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if not request.user == post.author:
        return redirect('posts:post_detail', post_id=post_id)
    if not form.is_valid():
        context = {
            'form': form,
            'is_edit': True,
        }
        return render(request, 'posts/create_post.html', context)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.filter(author=author)
    context = {
        'author': author,
        'page_obj': get_paginator(posts, request),
        'following':
            request.user.is_authenticated
            and request.user != author
            and Follow.objects.filter(user=request.user, author=author)
    }
    return render(request, 'posts/profile.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': get_paginator(posts, request),
    }
    return render(
        request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user,
                                     author=author
                                     )
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user,
                          author=user).delete()
    return redirect('posts:profile', username=username)
