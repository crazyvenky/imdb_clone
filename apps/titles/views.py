from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Title
from apps.interactions.models import Review, Rating
from apps.interactions.services import InteractionService
from apps.lists.models import CustomList, CustomListItem, Watchlist
from apps.search.utils import fetch_tmdb_details, sync_tmdb_details

def home_view(request):
    latest_movies = Title.objects.filter(
        type=Title.TitleType.MOVIE,
        is_deleted=False
    ).prefetch_related('genres').order_by('-release_date')[:12]
    context = {'latest_movies': latest_movies}
    return render(request, 'titles/home.html', context)

def movie_detail_view(request, pk):
    movie = get_object_or_404(
        Title.objects.prefetch_related('genres', 'cast_members__person', 'reviews__user'),
        pk=pk, type=Title.TitleType.MOVIE, is_deleted=False
    )

    # LAZY LOADER
    if movie.tmdb_id and not movie.cast_members.exists():
        details_data = fetch_tmdb_details(movie.tmdb_id)
        if details_data:
            sync_tmdb_details(movie, details_data)
            movie = get_object_or_404(
                Title.objects.prefetch_related('genres', 'cast_members__person', 'reviews__user'),
                pk=pk
            )

    actors = movie.cast_members.filter(role='ACT')
    directors = movie.cast_members.filter(role='DIR')

    user_rating = None
    user_review = None
    in_watchlist = False
    user_custom_lists = []
    user_lists_with_movie = []
    
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(user=request.user, title=movie).first()
        user_review = Review.objects.filter(user=request.user, title=movie).first()
        in_watchlist = Watchlist.objects.filter(user=request.user, title=movie).exists()
        user_custom_lists = CustomList.objects.filter(user=request.user).order_by('-created_at')
        user_lists_with_movie = CustomListItem.objects.filter(
            custom_list__user=request.user, title=movie
        ).values_list('custom_list_id', flat=True)

    # ==========================================
    # NEW: DECOUPLED POST LOGIC
    # ==========================================
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be signed in to do that.")
            return redirect('account_login')

        action = request.POST.get('action')

        if action == 'delete_rating':
            Rating.objects.filter(user=request.user, title=movie).delete()
            messages.success(request, "Your rating has been removed.")
            
        elif action == 'delete_review':
            Review.objects.filter(user=request.user, title=movie).delete()
            messages.success(request, "Your review has been removed.")
            
        elif action == 'submit_rating':
            rating_val = request.POST.get('rating')
            if rating_val and rating_val.isdigit():
                InteractionService.create_or_update_rating(
                    user=request.user, title_id=movie.id, value=int(rating_val)
                )
                messages.success(request, "Your rating has been saved!")
                
        elif action == 'submit_review':
            review_text = request.POST.get('text', '').strip()
            if review_text:
                Review.objects.update_or_create(
                    user=request.user, title=movie, defaults={'text': review_text}
                )
                messages.success(request, "Your review has been saved!")

        return redirect('apps.titles:movie_detail', pk=movie.id)

    # NEW: BUNDLE RATINGS INTO REVIEWS
    # ==========================================
    # Fetch all reviews for this movie
    movie_reviews = list(Review.objects.filter(title=movie).select_related('user').order_by('-created_at'))
    
    # Fetch all ratings for this movie and map them by user_id
    movie_ratings = Rating.objects.filter(title=movie)
    user_rating_map = {rating.user_id: rating.value for rating in movie_ratings}

    # Attach the rating value directly to the review object for the template
    for review in movie_reviews:
        review.user_star_rating = user_rating_map.get(review.user_id)

    context = {
        'movie': movie,
        'actors': actors,
        'directors': directors,
        'user_rating': user_rating,
        'user_review': user_review,
        'in_watchlist': in_watchlist,
        'user_custom_lists': user_custom_lists,
        'user_lists_with_movie': user_lists_with_movie,
        'movie_reviews': movie_reviews, # <-- ADD THIS TO CONTEXT
    }
    return render(request, 'titles/movie_detail.html', context)