from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=10,
        widget=forms.HiddenInput(attrs={'id': 'hidden-rating-input'})
    )

    class Meta:
        model = Review
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Write your review here...',
                'style': 'width: 100%; padding: 10px; border-radius: 4px; border: none; margin-bottom: 10px; resize: vertical;'
            }),
        }