
from django.shortcuts import render, get_object_or_404, redirect 
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings




@login_required
def search_view(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        ).order_by('-date_posted')

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'blog/search_results.html', context)



def landing_page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Compose the message
        email_body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        # Send the email
        send_mail(
            subject='New Contact Form Submission - PyWithRaman',
            message=email_body,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['dak99ine@gmail.com'],  # Replace with your personal email
            fail_silently=False,
        )

        messages.success(request, 'Thanks! Your message has been sent.')
        return redirect('landing-page')  

    recent_posts = Post.objects.order_by('-date_posted')[:6]
    return render(request, 'blog/landing.html', {'recent_posts': recent_posts})







def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False



def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})
