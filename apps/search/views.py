from django.shortcuts import render
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity
from apps.titles.models import Title

def search_results_view(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('s', 'all') # Default filter is 'all'
    
    results = Title.objects.none()

    if query:
        # Start with all active movies
        qs = Title.objects.filter(is_deleted=False)

        # 1. Title Search (Typo-Tolerant using Trigram)
        if search_type in ['all', 'titles']:
            qs = qs.annotate(
                similarity=TrigramSimilarity('title', query)
            ).filter(
                Q(similarity__gt=0.1) | Q(title__icontains=query)
            ).order_by('-similarity', '-release_date')

        # 2. Filter by Director
        elif search_type == 'directors':
            qs = qs.filter(director__icontains=query).order_by('-release_date')
            
        # 3. Filter by Year (Exact match required for numbers)
        elif search_type == 'year' and query.isdigit():
            qs = qs.filter(release_date__year=query).order_by('-release_date')

        results = qs

    context = {
        'query': query,
        'search_type': search_type,
        'results': results,
    }
    return render(request, 'search/search_results.html', context)