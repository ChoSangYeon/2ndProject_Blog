from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, UpdateView, DetailView, CreateView
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment, Tag, Category
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
import random
from .models import Post, Category, Tag
from django.views.generic.edit import CreateView


class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'post_list'
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(title__icontains=q)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['random_posts'] = self.get_random_posts()
        return context

    def get_random_posts(self):
        all_posts = Post.objects.all()
        random_posts = random.sample(list(all_posts), min(len(all_posts), 3))
        return random_posts

post_list = PostListView.as_view()


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('blog:post_list')
    template_name = 'blog/post_new.html'

    def form_valid(self, form):
        category_name = form.cleaned_data.get('new_category')
        tag_name = form.cleaned_data.get('new_tag')

        if category_name:
            category, created = Category.objects.get_or_create(name=category_name)
            form.instance.category = category

        form.instance.author = self.request.user
        response = super().form_valid(form)

        if tag_name:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            form.instance.tags.set([tag])  # set()에는 반복 가능한(iterable) 객체를 전달해야 함

        return response

post_new = PostCreateView.as_view()


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        post = get_object_or_404(Post, pk=pk)
        post.view_count += 1
        post.save(update_fields=['view_count'])
        return post

post_detail = PostDetailView.as_view()


class PostUpdateView(UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('blog:post_list')
    template_name = 'blog/post_new.html'

    def test_func(self):
        return self.get_object().author == self.request.user

post_edit = PostUpdateView.as_view()


class PostDeleteView(UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:post_list')

    def test_func(self):
        return self.get_object().author == self.request.user

post_delete = PostDeleteView.as_view()


@login_required
def comment_new(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'blog/post_detail.html', {'form': form, 'post': post})

