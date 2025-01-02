from typing import Counter
from django.shortcuts import render
from django.views import View
from django.utils import timezone
from datetime import timedelta

import pandas as pd
from board.models import Recommend, RecommendComment, Restaurant, RestaurantComment
import json
from django.conf import settings



class DashboardView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        user_infos, user_comments, post_count, comment_count = self.get_user_data(user)
        user_restaurant_comments, restaurant_comment_count = self.get_user_restaurant_data(user)
        dates, post_counts, comment_counts, restaurant_comment_counts = self.get_daily_stats(user)
        user_locations = self.get_user_locations(user)
        gu_labels, gu_data = self.get_gu_data()

        return render(request, 'dashboard.html', {
            'user_infos': user_infos,
            'user_comments': user_comments,
            'post_count': post_count,
            'comment_count': comment_count,
            'user_restaurant_comments': user_restaurant_comments,
            'restaurant_comment_count': restaurant_comment_count,
            'dates': json.dumps(dates),
            'post_counts': json.dumps(post_counts),
            'comment_counts': json.dumps(comment_counts),
            'restaurant_comment_counts': json.dumps(restaurant_comment_counts),
            'user_locations': json.dumps(user_locations),
            'naver_client_id': settings.NAVER_CLIENT_ID,
            'gu_labels': json.dumps(gu_labels),
            'gu_data': json.dumps(gu_data),
        })

    def get_user_data(self, user):
        user_infos = Recommend.objects.filter(user=user)
        user_comments = RecommendComment.objects.filter(user=user).order_by('-create_at')
        post_count = user_infos.count()
        comment_count = user_comments.count()

        return user_infos, user_comments, post_count, comment_count

    def get_user_restaurant_data(self, user):
        user_restaurant_comments = RestaurantComment.objects.filter(user=user).order_by('-create_at')
        restaurant_comment_count = user_restaurant_comments.count()

        return user_restaurant_comments, restaurant_comment_count

    def get_daily_stats(self, user):
        end_date = timezone.localtime(timezone.now()).date()
        start_date = end_date - timedelta(days=6)  # 7일 전부터 시작
        dates = [start_date + timedelta(days=i) for i in range(7)]
        date_labels = [date.strftime("%m월%d일") for date in dates]

        post_counts = []
        comment_counts = []
        restaurant_comment_counts = []
        for date in dates:
            start_of_day = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.min.time()))
            end_of_day = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.max.time()))

            post_count = Recommend.objects.filter(create_at__range=(start_of_day, end_of_day), user=user).count()
            comment_count = RecommendComment.objects.filter(create_at__range=(start_of_day, end_of_day),
                                                            user=user).count()
            restaurant_comment_count = RestaurantComment.objects.filter(create_at__range=(start_of_day, end_of_day),
                                                                        user=user).count()

            post_counts.append(post_count)
            comment_counts.append(comment_count)
            restaurant_comment_counts.append(restaurant_comment_count)

        return date_labels, post_counts, comment_counts, restaurant_comment_counts

    def get_user_locations(self, user):
        locations = Recommend.objects.filter(user=user).values('id', 'title', 'my_latitude', 'my_longitude')
        return list(locations)

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

        gu_labels = list(gu_counts.keys())
        gu_data = list(gu_counts.values())

        return gu_labels, gu_data
