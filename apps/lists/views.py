from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.titles.models import Title
from .models import Watchlist, CustomList, CustomListItem

@login_required
def toggle_watchlist(request, title_id):
    if request.method == 'POST':
        title = get_object_or_404(Title, id=title_id, is_deleted=False)
        
        # get_or_create tries to find the row. If it doesn't exist, it creates it.
        watchlist_item, created = Watchlist.objects.get_or_create(user=request.user, title=title)
        
        if not created:
            # It already existed! That means the user wants to REMOVE it.
            watchlist_item.delete()
            messages.info(request, f'Removed "{title.title}" from your Watchlist.')
        else:
            messages.success(request, f'Added "{title.title}" to your Watchlist.')
            
    # Safely redirect the user back to the exact page they clicked the button from
    return redirect(request.META.get('HTTP_REFERER', '/'))

# ... keep your toggle_watchlist view up here ...

@login_required
def watchlist_view(request):
    # Fetch the user's watchlist and optimize the query to grab the Title data at the same time
    watchlist_items = Watchlist.objects.filter(user=request.user).select_related('title')
    
    context = {
        'watchlist_items': watchlist_items
    }
    return render(request, 'lists/watchlist.html', context)

@login_required
def update_title_lists(request, title_id):
    if request.method == 'POST':
        title = get_object_or_404(Title, id=title_id, is_deleted=False)

        # 1. Handle the Watchlist Checkbox
        if request.POST.get('in_watchlist') == 'on':
            Watchlist.objects.get_or_create(user=request.user, title=title)
        else:
            Watchlist.objects.filter(user=request.user, title=title).delete()

        # 2. Handle Custom Lists Checkboxes (Check which ones are ticked)
        user_lists = CustomList.objects.filter(user=request.user)
        for custom_list in user_lists:
            # We will name our HTML checkboxes "list_1234", "list_5678", etc.
            list_field_name = f'list_{custom_list.id}'
            
            if request.POST.get(list_field_name) == 'on':
                CustomListItem.objects.get_or_create(custom_list=custom_list, title=title)
            else:
                CustomListItem.objects.filter(custom_list=custom_list, title=title).delete()

        # 3. Handle "Create New List" Input
        new_list_name = request.POST.get('new_list_name')
        if new_list_name and new_list_name.strip():
            new_list = CustomList.objects.create(user=request.user, name=new_list_name.strip())
            CustomListItem.objects.create(custom_list=new_list, title=title)

        messages.success(request, f'Updated your lists for "{title.title}".')

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def create_list_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public') == 'True'
        
        if name and name.strip():
            # Create the list and redirect the user back to their watchlist page
            CustomList.objects.create(
                user=request.user, 
                name=name.strip(), 
                description=description.strip(),
                is_public=is_public
            )
            messages.success(request, f'List "{name}" created successfully!')
            return redirect('apps.lists:watchlist')
            
    return render(request, 'lists/create_list.html')

@login_required
def toggle_custom_list(request, title_id, list_id):
    """Instantly adds or removes a movie from a specific custom list."""
    if request.method == 'POST':
        title = get_object_or_404(Title, id=title_id, is_deleted=False)
        custom_list = get_object_or_404(CustomList, id=list_id, user=request.user)
        
        item, created = CustomListItem.objects.get_or_create(custom_list=custom_list, title=title)
        
        if not created:
            item.delete()
            messages.info(request, f'Removed "{title.title}" from {custom_list.name}.')
        else:
            messages.success(request, f'Added "{title.title}" to {custom_list.name}.')
            
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def custom_list_detail(request, list_id):
    """Displays all the movies inside a specific custom list."""
    custom_list = get_object_or_404(CustomList, id=list_id, user=request.user)
    
    # Fetch the items and prefetch the movie data to avoid N+1 queries
    list_items = CustomListItem.objects.filter(custom_list=custom_list).select_related('title')
    
    context = {
        'custom_list': custom_list,
        'list_items': list_items,
    }
    return render(request, 'lists/custom_list_detail.html', context)

@login_required
def edit_list_view(request, list_id):
    """Allows a user to edit or delete their custom list."""
    # Ensure only the owner can edit this list
    custom_list = get_object_or_404(CustomList, id=list_id, user=request.user)
    
    if request.method == 'POST':
        # Check if the user clicked the "Delete" button
        if 'delete_list' in request.POST:
            list_name = custom_list.name
            custom_list.delete()
            messages.success(request, f'List "{list_name}" has been permanently deleted.')
            return redirect('apps.lists:watchlist') # Send them back to main watchlist
            
        # Otherwise, they clicked "Save Changes"
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public') == 'True'
        
        if name and name.strip():
            custom_list.name = name.strip()
            custom_list.description = description.strip()
            custom_list.is_public = is_public
            custom_list.save()
            messages.success(request, 'List updated successfully!')
            return redirect('apps.lists:custom_list_detail', list_id=custom_list.id)
            
    context = {'custom_list': custom_list}
    return render(request, 'lists/edit_list.html', context)