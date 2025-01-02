from django import forms
from .models import Recommend, RecommendComment, RestaurantComment

class RecommendForm(forms.ModelForm):
    class Meta:
        model = Recommend
        fields = ['title', 'description', 'rating', 'restaurant_name', 'r_address']

class CommentForm(forms.ModelForm):
    class Meta:
        model = RecommendComment
        fields = ['content', 'comment_rating']

    def clean_comment_rating(self):
        rating = self.cleaned_data.get('comment_rating')
        if rating is None:
            raise forms.ValidationError("별점을 선택해야 합니다.") 
        return rating
    

class CommentForm2(forms.ModelForm):
    class Meta:
        model = RestaurantComment
        fields = ['content', 'comment_rating']

    def clean_comment_rating(self):
        rating = self.cleaned_data.get('comment_rating')
        if rating is None:
            raise forms.ValidationError("별점을 선택해야 합니다.") 
        return rating
        
        