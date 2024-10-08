from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User


class CommentMixin:
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    comment = None

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Comment, pk=kwargs.get(
                'comment_id'
            )
        )
        if instance.author != request.user:
            return redirect('blog:post_detail', self.kwargs.get('comment_id'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.comment = self.comment
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs.get('post_id')}
        )


class IndexListView(ListView):
    model = Post
    queryset = Post.objects.prefetch_related(
        'comments'
    ).select_related('author').filter(
        pub_date__lt=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).annotate(comment_count=Count('comments'))
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = 10


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    ordering = ('-pub_date',)
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('post')
        )
        return context

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.author == request.user:
            self.object = get_object_or_404(Post.objects.filter(
                is_published=True,
                pub_date__lte=timezone.now(),
                category__is_published=True
            ), id=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        return context

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )

        queryset = category.posts.filter(
            pub_date__lt=timezone.now(),
            is_published=True,
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
        return queryset


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    ordering = 'id'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(User, username=self.kwargs.get(
            'username'
        )
        )
        return context

    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs.get('username'))
        instance = author.posts.filter(
            author__username__exact=self.kwargs.get('username')
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
        return instance


@login_required
def add_comment(request, post_id):
    comment = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        commentary = form.save(commit=False)
        commentary.author = request.user
        commentary.post = comment
        commentary.save()
    return redirect('blog:post_detail', pk=post_id)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    posts = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def dispatch(self, request, *args, **kwargs):
        self.posts = get_object_or_404(Post, pk=kwargs.get('post_id'))
        if self.posts.author != request.user:
            return redirect('blog:post_detail', self.kwargs.get('post_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.posts.pk}
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_delete'] = True
        return context

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs.get('post_id'))
        if instance.author != request.user:
            return redirect('blog:post_detail', self.kwargs.get('post_id'))
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_delete'] = True
        return context


class ProfiletUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username})
