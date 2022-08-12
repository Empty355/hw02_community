from django.core.paginator import Paginator
from posts.models import Post, Group, User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from posts.forms import PostForm
from yatube.settings import LIST_COUNT


def index(request):
    post_list = Post.objects.all().select_related("group", "author")
    paginator = Paginator(post_list, LIST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_list = Post.objects.filter(group=group).select_related(
        "group", "author"
    )
    paginator = Paginator(group_list, LIST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts_list = user.posts.select_related("group", "author")
    posts_numbers = posts_list.count()
    paginator = Paginator(posts_list, LIST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "author": user,
        "posts_numbers": posts_numbers,
        "page_obj": page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_numbers = post.author.posts.count()
    context = {
        'post': post,
        'posts_numbers': posts_numbers,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)
        return render(request, 'posts/post_create.html', {'form': form})
    form = PostForm()
    return render(
        request,
        'posts/post_create.html',
        {'form': form}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id=post_id)

    is_edit = True
    return render(request, 'posts/post_create.html', {'form': form,
                                                      'is_edit': is_edit,
                                                      'post': post})
