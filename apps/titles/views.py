from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Title, Genre
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


def browse_view(request):
    # 1. Start with all active movies
    qs = Title.objects.filter(type=Title.TitleType.MOVIE, is_deleted=False)
    
    # 2. Grab all filter parameters from the URL
    genre_id = request.GET.get('genre')
    year_min = request.GET.get('year_min')
    year_max = request.GET.get('year_max')
    rating_min = request.GET.get('rating_min')
    sort_by = request.GET.get('sort_by', '-popularity') # Default sort

    # 3. Apply Filters Dynamically
    if genre_id:
        qs = qs.filter(genres__id=genre_id)
        
    if year_min and year_min.isdigit():
        qs = qs.filter(release_date__year__gte=year_min)
        
    if year_max and year_max.isdigit():
        qs = qs.filter(release_date__year__lte=year_max)
        
    if rating_min:
        try:
            qs = qs.filter(avg_rating__gte=float(rating_min))
        except ValueError:
            pass

    # 4. Apply Sorting
    valid_sorts = {
        '-popularity': '-popularity',
        '-release_date': '-release_date',
        '-avg_rating': '-avg_rating',
        'title': 'title'
    }
    qs = qs.order_by(valid_sorts.get(sort_by, '-popularity')).distinct()

    # 5. Pagination (24 movies per page for a clean grid)
    paginator = Paginator(qs, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 6. Get all genres for the dropdown menu
    all_genres = Genre.objects.all().order_by('name')

    context = {
        'page_obj': page_obj,
        'all_genres': all_genres,
        # Pass current filters back to the template so the form remembers what you selected!
        'current_genre': int(genre_id) if genre_id and genre_id.isdigit() else '',
        'current_year_min': year_min,
        'current_year_max': year_max,
        'current_rating_min': rating_min,
        'current_sort': sort_by,
    }
    return render(request, 'titles/browse.html', context)