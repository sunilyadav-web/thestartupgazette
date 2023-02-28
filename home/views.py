from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView, DetailView

from .models import *
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin


class HomeView(TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        posts = Post.objects.filter(status=1)
        ctx['posts'] = Post.objects.filter(status=1).order_by('-publish_date')[:10]
        ctx['last_post'] = posts.latest('publish_date')

        featured_post_list = []
        featured = Featured.objects.order_by('-created_at')[:2]

        for item in featured:
            split = item.link.split('/')
            slug = split[-1]
            check = Post.objects.filter(slug=slug).exists()
            if check:
                object = Post.objects.get(slug=slug)
                featured_post_list.append(object)

        tag = Tag.objects.get(name='startup stories')
        startup_stories = posts.filter(tag=tag)[:6]
        ctx['startup_stories'] = startup_stories
        ctx['featured_post_list'] = featured_post_list
        ctx['sliders'] = Slider.objects.all()
        return ctx


def error(request):
    return HttpResponse('Hello error')


class PostDetailView(DetailView):
    model = Post
    template_name = "home/post_detail.html"


def category_filter(request, name):
    context = {}
    try:

        check = Category.objects.filter(name=name).exists()
        if check:
            category_obj = Category.objects.get(name=name)
            queryset = Post.objects.filter(category=category_obj)
            posts = queryset.filter(status=1)
            context['posts'] = posts
            context['category'] = name
        else:
            messages.warning(request, 'This ' + name + ' Category Not Found!')
    except Exception as e:
        print('Category Filter Exception : ', e)
        messages.error(request, 'Somthing went Wrong!')
    return render(request, 'home/category.html', context)


def tag_filter(request, name):
    context = {}
    try:
        check = Tag.objects.filter(name=name).exists()
        if check:
            tag_obj = Tag.objects.get(name=name)
            queryset = Post.objects.filter(tag=tag_obj)
            posts = queryset.filter(status=1)
            context['posts'] = posts
            context['tag'] = name
        else:
            messages.warning(request, 'Topic Not Found! ' + name)
    except Exception as e:
        print("Tag Exception : ", e)
    return render(request, 'home/tag.html', context)


class ContactView(SuccessMessageMixin, generic.CreateView):
    template_name = 'home/contact.html'
    model = Contact
    success_url = '/contact/'
    fields = '__all__'
    success_message = 'ThanYou, Will Responde you very soon!'


class AboutUsView(TemplateView):
    template_name = "home/about_us.html"


# =============Search Functionality===============
def search(request):
    context = {}
    try:
        query = request.GET.get('q')
        if query:
            context['query'] = query
            checkquery = list(query)

            if len(query) > 78:
                messages.warning(request, 'Query length cannot be greater than 77 characters')
                context['posts'] = Post.objects.none()

            elif len(query) == checkquery.count(' '):
                messages.warning(request, 'Query cannot be empty!')
                context['posts'] = Post.objects.none()

            else:

                posts = Post.objects.filter(status=1)
                queryset = posts.filter(Q(title__icontains=query) | Q(content__icontains=query)).order_by(
                    '-publish_date')

                paginator = Paginator(queryset, 2)
                pager_number = request.GET.get('page')
                page = paginator.get_page(pager_number)
                page_range = paginator.page_range
                context['posts'] = page
                context['page_range'] = page_range
                context['querysetLength'] = queryset.count()
                if queryset.count() < 1:
                    messages.warning(request, 'Query not found ' + query)
        else:
            messages.warning(request, 'Query cannot be empty. Please define something!')
            context['posts'] = Post.objects.none()
    except Exception as e:
        print('Search Exception : ', e)
        messages.error(request, 'Something went wrong!')
    return render(request, 'home/search.html', context)


class TermAndConditionView(TemplateView):
    template_name = "home/term_condition.html"


class PrivacyPolicyView(TemplateView):
    template_name = "home/privacy_policy.html"


# ========SEO Robots.txt File=======
def robot(request):
    return render(request, 'home/robots.txt')
