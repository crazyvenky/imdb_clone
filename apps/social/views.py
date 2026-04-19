from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .forms import UserEditForm
from apps.interactions.models import Review, Rating 
from apps.lists.models import CustomList 

User = get_user_model()

def user_profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    section = request.GET.get('section', 'overview')

    # Safe additive queries
    user_reviews = Review.objects.filter(user=profile_user).select_related('title').order_by('-created_at')
    user_ratings = Rating.objects.filter(user=profile_user).select_related('title').order_by('-created_at')
    user_lists = CustomList.objects.filter(user=profile_user)

    context = {
        'profile_user': profile_user,
        'section': section,
        'rating_count': user_ratings.count(),
        'review_count': user_reviews.count(),
        'list_count': user_lists.count(),
    }

    if section == 'overview' or section == 'reviews':
        reviews_to_show = list(user_reviews[:4]) if section == 'overview' else list(user_reviews)
        
        for review in reviews_to_show:
            matching_rating = user_ratings.filter(title=review.title).first()
            # THE FIX 2: Changed .rating to .value to match your model exactly!
            review.attached_rating = matching_rating.value if matching_rating else None
            
        context['display_reviews'] = reviews_to_show

    elif section == 'ratings':
        context['all_ratings'] = user_ratings

    elif section == 'lists':
        context['all_lists'] = user_lists

    return render(request, 'social/profile.html', context)

@login_required 
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            form.save()
            return redirect('apps.social:profile', username=request.user.username)
        else:
            # THE SCREAM TEST: This will print the exact error in your terminal!
            print("FORM ERRORS:", form.errors)
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'social/edit_profile.html', {'form': form})