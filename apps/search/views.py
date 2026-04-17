from django.shortcuts import render
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from apps.titles.models import Title
from .utils import fetch_tmdb_titles, sync_tmdb_to_local

def search_results_view(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('s', 'all')
    
    results = Title.objects.none()

    if query:
        def get_local_results():
            """Bulletproof local query that avoids NULL SearchVector crashes."""
            qs = Title.objects.filter(is_deleted=False)
            
            if search_type in ['all', 'titles']:
                # Use Trigram for typos + standard icontains for absolute matches
                return qs.annotate(
                    similarity=TrigramSimilarity('title', query)
                ).filter(
                    Q(similarity__gt=0.1) | 
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                ).order_by('-popularity', '-similarity')
                
            elif search_type == 'directors':
                return qs.filter(cast_members__person__name__icontains=query, cast_members__role='DIR').order_by('-popularity')
                
            elif search_type == 'year' and query.isdigit():
                return qs.filter(release_date__year=query).order_by('-popularity')
                
            return qs

        # 1. Check local Postgres DB
        local_results = get_local_results()

        # 2. Waterfall Logic: Ask TMDB for help if we have less than 3
        if local_results.count() < 3 and search_type in ['all', 'titles']:
            tmdb_data = fetch_tmdb_titles(query)
            
            if tmdb_data:
                sync_tmdb_to_local(tmdb_data)
                
                # Re-query the database to pull the 20 newly saved movies!
                local_results = get_local_results()

        # 3. Lock in top 20
        results = local_results[:20]

    context = {
        'query': query,
        'search_type': search_type,
        'results': results,
    }
    return render(request, 'search/search_results.html', context)