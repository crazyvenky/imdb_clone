from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Title
from apps.interactions.forms import ReviewForm
from apps.interactions.models import Review, Rating
from apps.interactions.services import InteractionService
from apps.lists.models import CustomList, CustomListItem, Watchlist

def home_view(request):
    latest_movies = Title.objects.filter(
        type=Title.TitleType.MOVIE,
        is_deleted=False
    ).prefetch_related('genres').order_by('-release_date')[:12]

    context = {'latest_movies': latest_movies}
    return render(request, 'titles/home.html', context)

def movie_detail_view(request, pk):
    movie = get_object_or_404(
        Title.objects.prefetch_related(
            'genres',
            'cast_members__person',
            'reviews__user'
        ),
        pk=pk,
        type=Title.TitleType.MOVIE,
        is_deleted=False
    )

    # NEW: Find the user's current rating, review, and watchlist status
    user_rating = None
    user_review = None
    in_watchlist = False # Default to False
    user_custom_lists = []     # NEW
    user_lists_with_movie = []
    
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(user=request.user, title=movie).first()
        user_review = Review.objects.filter(user=request.user, title=movie).first()
        
        # ADD THESE TWO LINES: Check if it's in the watchlist
        from apps.lists.models import Watchlist
        in_watchlist = Watchlist.objects.filter(user=request.user, title=movie).exists()

        user_custom_lists = CustomList.objects.filter(user=request.user).order_by('-created_at')
        user_lists_with_movie = CustomListItem.objects.filter(
            custom_list__user=request.user, title=movie
        ).values_list('custom_list_id', flat=True)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be signed in to leave a review.")
            return redirect('account_login')

        form = ReviewForm(request.POST)
        if form.is_valid():
            InteractionService.create_or_update_rating(
                user=request.user, title_id=movie.id, value=form.cleaned_data['rating']
            )
            # Only save text if they actually wrote something
            if form.cleaned_data['text']:
                Review.objects.update_or_create(
                    user=request.user, title=movie, defaults={'text': form.cleaned_data['text']}
                )
            messages.success(request, "Your rating has been saved!")
            return redirect('apps.titles:movie_detail', pk=movie.id)
            
    else:
        # Pre-fill the form if they already have a review
        initial_data = {}
        if user_rating: initial_data['rating'] = user_rating.value
        if user_review: initial_data['text'] = user_review.text
        form = ReviewForm(initial=initial_data)

    context = {
        'movie': movie,
        'form': form,
        'user_rating': user_rating,
        'in_watchlist': in_watchlist, # Pass the status to the template
        'user_custom_lists': user_custom_lists,         # NEW
        'user_lists_with_movie': user_lists_with_movie,
    }
    return render(request, 'titles/movie_detail.html', context)