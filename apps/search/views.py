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
        def get_local_results(current_query):
            qs = Title.objects.filter(is_deleted=False)
            
            if search_type in ['all', 'titles']:
                qs = qs.annotate(similarity=TrigramSimilarity('title', current_query))
                title_match = Q(similarity__gt=0.3) | Q(title__icontains=current_query)
                
                desc_match = Q(id__isnull=True)
                if len(current_query) > 4 and not current_query.isdigit():
                    desc_match = Q(description__icontains=current_query)

                return qs.filter(title_match | desc_match).order_by(
                    '-similarity',
                    '-popularity'
                )
                
            elif search_type == 'directors':
                return qs.filter(
                    cast_members__person__name__icontains=current_query, 
                    cast_members__role='DIR'
                ).order_by('-popularity')
                
            elif search_type == 'year' and current_query.isdigit():
                return qs.filter(release_date__year=current_query).order_by('-popularity')
                
            return qs

        # Step 1: Initial Local Check
        local_results = get_local_results(query)
        results_list = list(local_results[:20]) 
        if len(results_list) < 3 and search_type in ['all', 'titles']:
            tmdb_data = fetch_tmdb_titles(query)
            if not tmdb_data and len(query.split()) > 1:
                relaxed_query = " ".join(query.split()[:-1])
                tmdb_data = fetch_tmdb_titles(relaxed_query)

            if tmdb_data:
                sync_tmdb_to_local(tmdb_data)
                results_list = list(get_local_results(query)[:20])

        results = results_list

    context = {
        'query': query,
        'search_type': search_type,
        'results': results,
    }
    return render(request, 'search/search_results.html', context)
