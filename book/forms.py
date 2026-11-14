from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    # The reviewer's name and email are taken from their account.
    class Meta:
        model = Review
        fields = ['body']
        labels = {'body': 'Your review'}
        widgets = {'body': forms.Textarea(attrs={'rows': 3})}
