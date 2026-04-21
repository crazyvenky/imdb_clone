from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.titles.models import Title
from .models import Watchlist, CustomList, CustomListItem, SavedList

@login_required
def toggle_watchlist(request, title_id):
    if request.method == 'POST':
        title = get_object_or_404(Title, id=title_id, is_deleted=False)
        watchlist_item, created = Watchlist.objects.get_or_create(user=request.user, title=title)
        
        if not created:
            watchlist_item.delete()
            messages.info(request, f'Removed "{title.title}" from your Watchlist.')
        else:
            messages.success(request, f'Added "{title.title}" to your Watchlist.')

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def watchlist_view(request):
    watchlist_items = Watchlist.objects.filter(user=request.user).select_related('title')

    my_lists = CustomList.objects.filter(user=request.user).order_by('-created_at')
    saved_lists = SavedList.objects.filter(user=request.user).select_related('custom_list__user').order_by('-created_at')
    
    context = {
        'watchlist_items': watchlist_items,
        'my_lists': my_lists,
        'saved_lists': saved_lists,
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
    custom_list = get_object_or_404(CustomList, id=list_id)

    if not custom_list.is_public and custom_list.user != request.user:
        messages.error(request, "This list is private.")
        return redirect('apps.lists:public_lists')
        
    list_items = CustomListItem.objects.filter(custom_list=custom_list).select_related('title')

    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedList.objects.filter(user=request.user, custom_list=custom_list).exists()
    
    context = {
        'custom_list': custom_list,
        'list_items': list_items,
        'is_saved': is_saved,
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


@login_required
def public_lists_feed(request):
    """Displays all public lists across the platform, excluding the user's own."""
    # .prefetch_related prevents N+1 database crashes when loading posters!
    public_lists = CustomList.objects.filter(is_public=True).exclude(
        user=request.user
    ).select_related('user').prefetch_related('items__title').order_by('-created_at')
    
    return render(request, 'lists/public_lists.html', {'public_lists': public_lists})

@login_required
def save_list_reference(request, list_id):
    """Bookmarks/Saves another user's public list (By Reference)."""
    if request.method == 'POST':
        custom_list = get_object_or_404(CustomList, id=list_id, is_public=True)
        
        if custom_list.user == request.user:
            messages.error(request, "You cannot save your own list.")
            return redirect('apps.lists:custom_list_detail', list_id=list_id)

        saved_item, created = SavedList.objects.get_or_create(user=request.user, custom_list=custom_list)
        
        if not created:
            saved_item.delete()
            messages.info(request, f'Removed "{custom_list.name}" from your saved library.')
        else:
            messages.success(request, f'Saved "{custom_list.name}" to your library.')
            
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def clone_list(request, list_id):
    """Forks/Duplicates a list and all its movies into the user's account."""
    if request.method == 'POST':
        original_list = get_object_or_404(CustomList, id=list_id, is_public=True)
        
        if original_list.user == request.user:
            messages.error(request, "You cannot clone your own list.")
            return redirect('apps.lists:custom_list_detail', list_id=list_id)

        # 1. Create the new cloned list wrapper (Private by default!)
        new_list = CustomList.objects.create(
            user=request.user,
            name=f"Copy of {original_list.name}",
            description=f"Cloned from {original_list.user.username}. {original_list.description}",
            is_public=False 
        )

        # 2. Bulk copy the movies to save database performance
        original_items = original_list.items.all()
        new_items = [
            CustomListItem(custom_list=new_list, title=item.title)
            for item in original_items
        ]
        # bulk_create writes them all to the database in exactly 1 query!
        CustomListItem.objects.bulk_create(new_items)

        messages.success(request, f'Successfully cloned! You can now edit "{new_list.name}".')
        # Teleport them directly into their newly cloned list
        return redirect('apps.lists:custom_list_detail', list_id=new_list.id)
        
    return redirect(request.META.get('HTTP_REFERER', '/'))