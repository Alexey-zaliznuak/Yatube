from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm


POSTS_PER_PAGE = 10
LEN_SHORT_POST = 30


@cache_page(20)
def index(request):
    paginator = Paginator(Post.objects.all(), POSTS_PER_PAGE)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)

    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)

    posts = user.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=user).exists()

    context = {
        'page_obj': page_obj,
        'posts_count': posts.count(),
        'author': user,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post)
    author = post.author

    posts_count = Post.objects.filter(author=author).count()
    context = {
        'post': post,
        "posts_count": posts_count,
        'short_post': post.text[:LEN_SHORT_POST],
        'comments': comments,
        'form': CommentForm()
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_create(request):
    user = request.user
    form = PostForm(
        request.POST or None,
        files=request.FILES,
    )
    if form.is_valid():

        post = form.save(commit=False)
        post.author = user
        post.save()

        return redirect('posts:profile', user.username)

    context = {
        'form': form,
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = Post.objects.get(pk=post_id)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    following = Follow.objects.filter(user=request.user).values('author')
    posts = Post.objects.filter(author__in=following)
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    if (
        request.user.username != username
        and not Follow.objects.filter(
            user=request.user,
            author=User.objects.get(username=username)
        ).exists()
    ):
        Follow.objects.create(
            user=request.user,
            author=User.objects.get(username=username)
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    follow = Follow.objects.filter(
        user=request.user,
        author=User.objects.get(username=username)
    )

    follow.delete()

    return redirect('posts:profile', username=username)
