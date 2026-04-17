import requests
from django.conf import settings
from django.contrib.postgres.search import SearchVector
from apps.titles.models import Title, Genre, TitleCast
from apps.people.models import Person

# ==========================================
# 1. SEARCH API (Used by Search Bar)
# ==========================================
def fetch_tmdb_titles(query):
    url = "https://api.themoviedb.org/3/search/movie"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {settings.TMDB_READ_ACCESS_TOKEN}"
    }
    params = {"query": query, "include_adult": "false", "language": "en-US", "page": 1}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        return response.json().get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"TMDB Search API Error: {e}")
        return []

def sync_tmdb_to_local(tmdb_results):
    synced_ids = []
    for item in tmdb_results:
        release_date = item.get('release_date')
        if not release_date or release_date == "":
            release_date = None
            
        title_obj, created = Title.objects.update_or_create(
            tmdb_id=item['id'],
            defaults={
                'title': item.get('title', ''),
                'description': item.get('overview', ''),
                'release_date': release_date,
                'popularity': item.get('popularity', 0.0),
                'poster_path': item.get('poster_path', ''),
                'avg_rating': item.get('vote_average', 0.0), 
                'rating_count': item.get('vote_count', 0),   
            }
        )
        synced_ids.append(title_obj.id)
    
    if synced_ids:
        Title.objects.filter(id__in=synced_ids).update(
            search_vector=SearchVector('title', weight='A') + SearchVector('description', weight='B')
        )

# ==========================================
# 2. DETAILS API (Used by Detail View)
# ==========================================
def fetch_tmdb_details(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?append_to_response=credits"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {settings.TMDB_READ_ACCESS_TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"TMDB Details API Error: {e}")
        return None

def sync_tmdb_details(title_obj, data):
    if not data:
        return
    title_obj.runtime_minutes = data.get('runtime')
    title_obj.save()

    for g in data.get('genres', []):
        genre, _ = Genre.objects.get_or_create(name=g['name'])
        title_obj.genres.add(genre)

    credits = data.get('credits', {})
    for cast_member in credits.get('cast', [])[:10]:
        person, _ = Person.objects.update_or_create(
            name=cast_member['name'],
            defaults={'profile_path': cast_member.get('profile_path')}
        )
        TitleCast.objects.get_or_create(
            title=title_obj, person=person, role=TitleCast.RoleType.ACTOR,
            defaults={'character_name': cast_member.get('character', '')}
        )

    for crew_member in credits.get('crew', []):
        if crew_member.get('job') == 'Director':
            person, _ = Person.objects.get_or_create(name=crew_member['name'])
            TitleCast.objects.get_or_create(title=title_obj, person=person, role=TitleCast.RoleType.DIRECTOR)
            break