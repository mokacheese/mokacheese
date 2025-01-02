from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Restaurant, Recommend, RecommendComment, RestaurantComment
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import requests
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.db.models.functions import Coalesce
from .forms import CommentForm, CommentForm2
from django.contrib.auth.decorators import login_required
from board.models import RecommendComment, RestaurantComment
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
import json
import pandas as pd
from collections import Counter




class RecListView(LoginRequiredMixin, ListView):
    model = Recommend
    template_name = 'board/info_list.html'
    context_object_name = 'contacts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        sort_option = self.request.GET.get('sort', 'title')

        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(r_address__icontains=query))

        queryset = queryset.annotate(avg_rating=Coalesce(Avg('recommend_comments__comment_rating'), 0.0))

        if sort_option == 'name':
            queryset = queryset.order_by('title')
        elif sort_option == 'address':
            queryset = queryset.order_by('r_address')
        elif sort_option == 'avg_rating':
            queryset = queryset.order_by('-avg_rating')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['star_range'] = range(5, 0, -1)
        context['sort_option'] = self.request.GET.get('sort', 'title')
        return context


class RestaurantListView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = 'board/info_list2.html'
    context_object_name = 'restaurants'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        sort_option = self.request.GET.get('sort', 'r_name')

        if query:
            queryset = queryset.filter(Q(r_name__icontains=query) | Q(address__icontains=query))

        queryset = queryset.annotate(avg_rating=Coalesce(Avg('restaurant_comments__comment_rating'), 0.0))

        if sort_option == 'name':
            queryset = queryset.order_by('r_name')
        elif sort_option == 'address':
            queryset = queryset.order_by('address')
        elif sort_option == 'avg_rating':
            queryset = queryset.order_by('-avg_rating')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['star_range'] = range(5, 0, -1)
        context['sort_option'] = self.request.GET.get('sort', 'r_name')
        return context


class RecCreateView(LoginRequiredMixin, CreateView):
    model = Recommend
    fields = ['title', 'description', 'restaurant_name', 'r_address', 'file']
    template_name = 'board/r_form.html'
    success_url = reverse_lazy('board:info-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.my_latitude = self.request.POST.get('my_latitude')
        form.instance.my_longitude = self.request.POST.get('my_longitude')
        form.instance.my_address = self.request.POST.get('my_address')
        return super().form_valid(form)


class RecUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recommend
    fields = ['title', 'description', 'restaurant_name', 'r_address', 'file']
    template_name = 'board/r_form.html'
    success_url = reverse_lazy('board:info-list')

    def test_func(self):
        rec = self.get_object()
        return self.request.user == rec.user

    def handle_no_permission(self):
        return custom_403_view(self.request)


class RecDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recommend
    success_url = reverse_lazy('board:info-list')
    context_object_name = 'information'


    def test_func(self):
        rec = self.get_object()
        return self.request.user == rec.user

    def handle_no_permission(self):
        return custom_403_view(self.request)


class RecDetailView(LoginRequiredMixin, DetailView):
    model = Recommend
    template_name = 'board/info_detail.html'
    context_object_name = 'information'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        information = self.object
        comments = information.recommend_comments.all()
        # 평균 별점 계산 및 업데이트
        if comments.exists():
            average_rating = comments.aggregate(Avg('comment_rating'))['comment_rating__avg']
            information.rating = average_rating
            information.save()
        else:
            information.rating = 0
            information.save()

        context['comments'] = comments
        context['comment_form'] = CommentForm()
        context['star_range'] = range(5, 0, -1)
        context['naver_client_id'] = settings.NAVER_CLIENT_ID
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.info = self.object
            comment.user = request.user
            comment.comment_rating = request.POST.get('comment_rating')
            comment.save()
            return redirect('board:info_detail', pk=self.object.pk)

        context = self.get_context_data(object=self.object)
        context['comment_form'] = comment_form
        return self.render_to_response(context)


class RestaurantDetailView(LoginRequiredMixin, DetailView):
    model = Restaurant
    template_name = 'board/info_detail2.html'
    context_object_name = 'restaurant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = self.object
        comments = restaurant.restaurant_comments.all()
        # 평균 별점 계산 및 업데이트
        if comments.exists():
            average_rating = comments.aggregate(Avg('comment_rating'))['comment_rating__avg']
            restaurant.rating = average_rating
            restaurant.save()
        else:
            restaurant.rating = 0
            restaurant.save()

        context['comments'] = comments
        context['comment_form'] = CommentForm2()
        context['star_range'] = range(5, 0, -1)
        context['naver_client_id'] = settings.NAVER_CLIENT_ID
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        comment_form = CommentForm2(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.info = self.object
            comment.user = request.user
            comment.comment_rating = request.POST.get('comment_rating')
            comment.save()
            return redirect('board:info_detail2', pk=self.object.pk)

        context = self.get_context_data(object=self.object)
        context['comment_form'] = comment_form
        return self.render_to_response(context)


def custom_403_view(request, exception=None):
    return render(request, 'board/403.html', status=403)


def proxy_view(request):
    url = 'https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc'
    params = {
        'coords': request.GET.get('coords'),
        'orders': 'roadaddr',
        'output': 'json'
    }
    headers = {
        'X-NCP-APIGW-API-KEY-ID': settings.NAVER_CLIENT_ID,
        'X-NCP-APIGW-API-KEY': settings.NAVER_CLIENT_SECRET
    }
    response = requests.get(url, headers=headers, params=params)
    return JsonResponse(response.json())


def board3_view(request):
    restaurants = Restaurant.objects.all()
    context = {
        'restaurants': restaurants,
        'naver_client_id': settings.NAVER_CLIENT_ID,
    }
    return render(request, 'board/board3.html', context)


def board3_list(request):
    restaurants = Restaurant.objects.all().order_by('id')
    paginator = Paginator(restaurants, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'board/board3_list.html', {'page_obj': page_obj})


def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    context = {
        'restaurant': restaurant,
        'naver_client_id': settings.NAVER_CLIENT_ID,
    }
    return render(request, 'board/restaurant_detail.html', context)


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(RecommendComment, id=comment_id)
    info = comment.info

    if request.user != comment.user:  # 작성자가 아니면 상세페이지 화면으로
        return redirect('board:info_detail', pk=info.id)  # 권한 없음

    if request.method == 'POST':  # 댓글 수정 폼 제출
        form = CommentForm(request.POST, instance=comment)  # 수정할 댓글 객체 연결
        if form.is_valid():
            comment.comment_rating = form.cleaned_data.get('comment_rating', 0)  # 점수가 비었을 때
            comment.save()
            comments = info.recommend_comments.all()  # 별점 평균 업데이트
            if comments.exists():
                average_rating = sum(c.comment_rating for c in comments) / comments.count()
                info.rating = average_rating
            else:
                info.rating = 0  # 기본값 0
            info.save()

            return redirect('board:info_detail', pk=info.id)
    else:  # GET 요청
        form = CommentForm(instance=comment)  # 기존 댓글 내용을 표시
    star_range = list(range(5, 0, -1))
    return render(request, 'board/edit_comment.html', {'form': form})


def delete_comment(request, comment_id):
    comment = get_object_or_404(RecommendComment, id=comment_id)
    info = comment.info  # 별점때문에 필요

    if request.user == comment.user:
        comment.delete()
        comments = info.recommend_comments.all()  # 별점 평균 업데이트
        if comments.exists():
            average_rating = sum(c.comment_rating for c in comments) / comments.count()
            info.rating = average_rating
        else:
            info.rating = 0  # 기본값
        info.save()

    return redirect('board:info_detail', pk=info.id)


@login_required
def edit_comment2(request, comment_id):
    comment = get_object_or_404(RestaurantComment, id=comment_id)
    restaurant = comment.info

    if request.user != comment.user:  # 작성자가 아니면 상세페이지 화면으로
        return redirect('board:info_detail2', pk=restaurant.id)  # 권한 없음

    if request.method == 'POST':  # 댓글 수정 폼 제출
        form = CommentForm(request.POST, instance=comment)  # 수정할 댓글 객체 연결
        if form.is_valid():
            comment.comment_rating = form.cleaned_data.get('comment_rating', 0)  # 점수가 비었을 때
            comment.save()
            comments = restaurant.restaurant_comments.all()  # 별점 평균 업데이트
            if comments.exists():
                average_rating = sum(c.comment_rating for c in comments) / comments.count()
                restaurant.rating = average_rating
            else:
                restaurant.rating = 0  # 기본값 0
            restaurant.save()

            return redirect('board:info_detail2', pk=restaurant.id)
    else:  # GET 요청
        form = CommentForm(instance=comment)  # 기존 댓글 내용을 표시
    star_range = list(range(5, 0, -1))
    return render(request, 'board/edit_comment.html', {'form': form})


def delete_comment2(request, comment_id):
    comment = get_object_or_404(RestaurantComment, id=comment_id)
    restaurant = comment.info  # 별점때문에 필요

    if request.user == comment.user:
        comment.delete()
        comments = restaurant.restaurant_comments.all()  # 별점 평균 업데이트
        if comments.exists():
            average_rating = sum(c.comment_rating for c in comments) / comments.count()
            restaurant.rating = average_rating
        else:
            restaurant.rating = 0  # 기본값
        restaurant.save()

    return redirect('board:info_detail2', pk=restaurant.id)








class Dashboard2View(View):
    def get(self, request, *args, **kwargs):
        dates, recommend_comment_counts, restaurant_comment_counts = self.get_all_daily_stats()
        gu_counts = Counter({'대덕구': 2331, '서초구': 251, '단원구': 128, '상록구': 106})

        gu_labels = list(gu_counts.keys())
        gu_data = list(gu_counts.values())

        return render(request, 'dashboard2.html', {
            'dates': json.dumps(dates),
            'recommend_comment_counts': json.dumps(recommend_comment_counts),
            'restaurant_comment_counts': json.dumps(restaurant_comment_counts),
            'gu_labels': json.dumps(gu_labels),
            'gu_data': json.dumps(gu_data)
        })

    def extract_gu(self, address):
        for part in address.split():
            if part.endswith('구'):
                return part
        return '기타'

    def get_all_daily_stats(self):
        today = timezone.now().date()
        dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
        date_labels = [date.strftime("%m월%d일") for date in dates]

        recommend_comment_counts = [
            RecommendComment.objects.filter(create_at__date=date).count()
            for date in dates
        ]
        restaurant_comment_counts = [
            RestaurantComment.objects.filter(create_at__date=date).count()
            for date in dates
        ]

        return date_labels, recommend_comment_counts, restaurant_comment_counts

    def get_gu_data(self):
        ansan_data = pd.read_csv('경기도 안산시_생생맛집2.csv')
        daedeok_data = pd.read_csv('대전광역시 대덕구_일반음식점_20240520.csv')
        seocho_data = pd.read_csv('서울특별시 서초구_음식점 (모범음식점)_20240603.csv')

        ansan_data['address'] = ansan_data['address'].fillna('')
        daedeok_data['소재지(도로명)'] = daedeok_data['소재지(도로명)'].fillna('')
        seocho_data['address'] = seocho_data['address'].fillna('')

        ansan_gu = ansan_data['address'].apply(lambda x: x.split()[1] if '안산시' in x and len(x.split()) > 1 else '기타')
        daedeok_gu = daedeok_data['소재지(도로명)'].apply(lambda x: x.split()[1] if len(x.split()) > 1 else '기타')
        seocho_gu = seocho_data['address'].apply(lambda x: x.split()[1] if '서초구' in x and len(x.split()) > 1 else '기타')

        gu_list = list(ansan_gu) + list(daedeok_gu) + list(seocho_gu)
        gu_counts = Counter(gu_list)

        return gu_counts