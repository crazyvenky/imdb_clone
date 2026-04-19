from django import forms
from django.contrib.auth import get_user_model

# This automatically grabs your custom User model from accounts.models!
User = get_user_model()

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'bio', 'location', 'website', 'date_of_birth', 'avatar']
        
        # Adding some clean widgets so the UI matches our dark theme
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell everyone about your favorite movies...'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g. New York, NY'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}),
        }