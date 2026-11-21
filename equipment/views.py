
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import (
    Equipment,
    RentalRequest,
    Notification,
    Conversation,
    ChatMessage
)
from .forms import EquipmentForm, RentalRequestForm
from accounts.models import Profile


# Check whether the logged-in user is an equipment owner
def is_equipment_owner(user):
    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={'role': 'RENTER'}
    )
    return profile.role == 'OWNER'


# Display equipment for browsing with county filtering
def equipment_list(request):
    is_owner = False
    selected_county = request.GET.get('county', '')

    if request.user.is_authenticated and is_equipment_owner(request.user):
        equipment = Equipment.objects.filter(owner=request.user)
        is_owner = True
    else:
        equipment = Equipment.objects.filter(available=True)

        if selected_county:
            equipment = equipment.filter(county=selected_county)

    return render(
        request,
        'equipment/equipment_list.html',
        {
            'equipment': equipment,
            'is_owner': is_owner,
            'counties': Equipment.COUNTY_CHOICES,
            'selected_county': selected_county
        }
    )


# Add new equipment
@login_required
def add_equipment(request):
    if not is_equipment_owner(request.user):
        messages.error(request, 'Only equipment owners can add equipment.')
        return redirect('equipment_list')

    form = EquipmentForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.owner = request.user
            equipment.save()

            messages.success(request, 'Equipment added successfully.')
            return redirect('equipment_list')

    return render(
        request,
        'equipment/add_equipment.html',
        {'form': form}
    )


# Edit equipment belonging to the logged-in owner
@login_required
def edit_equipment(request, pk):
    if not is_equipment_owner(request.user):
        messages.error(request, 'Only equipment owners can edit equipment.')
        return redirect('equipment_list')

    equipment = get_object_or_404(
        Equipment,
        pk=pk,
        owner=request.user
    )

    form = EquipmentForm(
        request.POST or None,
        request.FILES or None,
        instance=equipment
    )

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment updated successfully.')
            return redirect('equipment_list')

    return render(
        request,
        'equipment/edit_equipment.html',
        {'form': form}
    )


# Delete equipment belonging to the logged-in owner
@login_required
def delete_equipment(request, pk):
    if not is_equipment_owner(request.user):
        messages.error(request, 'Only equipment owners can delete equipment.')
        return redirect('equipment_list')

    equipment = get_object_or_404(
        Equipment,
        pk=pk,
        owner=request.user
    )

    if request.method == 'POST':
        equipment.delete()
        messages.success(request, 'Equipment deleted successfully.')
        return redirect('equipment_list')

    return render(
        request,
        'equipment/delete_equipment.html',
        {'equipment': equipment}
    )


# Submit a rental request
@login_required
def request_equipment(request, pk):
    if is_equipment_owner(request.user):
        messages.error(
            request,
            'Equipment owners cannot submit rental requests.'
        )
        return redirect('equipment_list')

    equipment = get_object_or_404(
        Equipment,
        pk=pk,
        available=True
    )

    if equipment.owner == request.user:
        messages.error(request, 'You cannot request your own equipment.')
        return redirect('equipment_list')

    existing_request = RentalRequest.objects.filter(
        equipment=equipment,
        renter=request.user,
        status='PENDING'
    ).exists()

    if existing_request:
        messages.warning(
            request,
            'You already have a pending request for this equipment.'
        )
        return redirect('equipment_list')

    form = RentalRequestForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            rental_request = form.save(commit=False)
            rental_request.equipment = equipment
            rental_request.renter = request.user
            rental_request.save()

            Notification.objects.create(
                user=equipment.owner,
                rental_request=rental_request,
                message=(
                    f'{request.user.username} has submitted a rental '
                    f'request for your equipment: {equipment.name}.'
                )
            )

            messages.success(
                request,
                'Your rental request has been submitted successfully.'
            )

            return redirect('my_rental_requests')

    return render(
        request,
        'equipment/request_equipment.html',
        {
            'form': form,
            'equipment': equipment
        }
    )


# View rental requests submitted by the logged-in renter
@login_required
def my_rental_requests(request):
    if is_equipment_owner(request.user):
        messages.error(
            request,
            'This page is only available to equipment renters.'
        )
        return redirect('owner_dashboard')

    rental_requests = RentalRequest.objects.filter(
        renter=request.user
    ).select_related('equipment').order_by('-requested_at')

    return render(
        request,
        'equipment/my_rental_requests.html',
        {'rental_requests': rental_requests}
    )


# View incoming rental requests for the logged-in equipment owner
@login_required
def owner_rental_requests(request):
    if not is_equipment_owner(request.user):
        messages.error(
            request,
            'Only equipment owners can view incoming rental requests.'
        )
        return redirect('equipment_list')

    rental_requests = RentalRequest.objects.filter(
        equipment__owner=request.user
    ).select_related(
        'equipment',
        'renter'
    ).order_by('-requested_at')

    return render(
        request,
        'equipment/owner_rental_requests.html',
        {'rental_requests': rental_requests}
    )


# Accept or reject a rental request
@login_required
@require_POST
def update_rental_request(request, pk, action):
    if not is_equipment_owner(request.user):
        messages.error(request, 'Only equipment owners can manage requests.')
        return redirect('equipment_list')

    rental_request = get_object_or_404(
        RentalRequest,
        pk=pk,
        equipment__owner=request.user
    )

    if rental_request.status != 'PENDING':
        messages.warning(
            request,
            'This request has already been processed.'
        )
        return redirect('owner_rental_requests')

    if action == 'accept':
        rental_request.status = 'ACCEPTED'
        message = (
            f'Your rental request for {rental_request.equipment.name} '
            f'has been accepted!'
        )
        success_message = 'Rental request accepted successfully.'

    elif action == 'reject':
        rental_request.status = 'REJECTED'
        message = (
            f'Your rental request for {rental_request.equipment.name} '
            f'has been rejected.'
        )
        success_message = 'Rental request rejected.'

    else:
        messages.error(request, 'Invalid request action.')
        return redirect('owner_rental_requests')

    rental_request.save(update_fields=['status'])

    # Create a conversation when the owner accepts the request
    if action == 'accept':
        Conversation.objects.get_or_create(
            rental_request=rental_request
        )

    # Notify the renter about the owner's decision
    Notification.objects.create(
        user=rental_request.renter,
        rental_request=rental_request,
        message=message
    )

    messages.success(request, success_message)

    return redirect('owner_rental_requests')


# View notifications belonging to the logged-in renter
@login_required
def renter_notifications(request):
    if is_equipment_owner(request.user):
        messages.error(
            request,
            'Notifications are only available to renters.'
        )
        return redirect('owner_dashboard')

    notifications = Notification.objects.filter(
        user=request.user
    ).select_related(
        'rental_request',
        'rental_request__equipment'
    ).order_by('-created_at')

    return render(
        request,
        'equipment/renter_notifications.html',
        {'notifications': notifications}
    )


# Mark an individual renter notification as read
@login_required
@require_POST
def mark_notification_read(request, pk):
    if is_equipment_owner(request.user):
        messages.error(
            request,
            'Notifications are only available to renters.'
        )
        return redirect('owner_dashboard')

    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user
    )

    notification.is_read = True
    notification.save(update_fields=['is_read'])

    messages.success(request, 'Notification marked as read.')

    return redirect('renter_notifications')


# View notifications belonging to the logged-in equipment owner
@login_required
def owner_notifications(request):
    if not is_equipment_owner(request.user):
        messages.error(
            request,
            'This page is only available to equipment owners.'
        )
        return redirect('renter_dashboard')

    notifications = Notification.objects.filter(
        user=request.user
    ).select_related(
        'rental_request',
        'rental_request__equipment',
        'rental_request__renter'
    ).order_by('-created_at')

    return render(
        request,
        'equipment/owner_notifications.html',
        {'notifications': notifications}
    )


# Mark an individual owner notification as read
@login_required
@require_POST
def mark_owner_notification_read(request, pk):
    if not is_equipment_owner(request.user):
        messages.error(
            request,
            'Only equipment owners can access this action.'
        )
        return redirect('renter_dashboard')

    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user
    )

    notification.is_read = True
    notification.save(update_fields=['is_read'])

    messages.success(request, 'Notification marked as read.')

    return redirect('owner_notifications')


# Display conversations belonging to the logged-in user
@login_required
def message_inbox(request):
    conversations = Conversation.objects.filter(
        rental_request__status='ACCEPTED'
    ).filter(
        Q(rental_request__renter=request.user) |
        Q(rental_request__equipment__owner=request.user)
    ).select_related(
        'rental_request',
        'rental_request__equipment',
        'rental_request__renter',
        'rental_request__equipment__owner'
    ).order_by('-updated_at')

    unread_count = ChatMessage.objects.filter(
        conversation__in=conversations
    ).exclude(
        sender=request.user
    ).filter(
        is_read=False
    ).count()

    return render(
        request,
        'equipment/message_inbox.html',
        {
            'conversations': conversations,
            'unread_count': unread_count
        }
    )


# Open a conversation between the renter and equipment owner
@login_required
def chat_room(request, pk):
    conversation = get_object_or_404(
        Conversation.objects.select_related(
            'rental_request',
            'rental_request__equipment',
            'rental_request__renter',
            'rental_request__equipment__owner'
        ),
        pk=pk,
        rental_request__status='ACCEPTED'
    )

    renter = conversation.rental_request.renter
    owner = conversation.rental_request.equipment.owner

    # Only the renter and equipment owner can access this chat
    if request.user != renter and request.user != owner:
        messages.error(
            request,
            'You are not allowed to access this conversation.'
        )
        return redirect('message_inbox')

    # Mark messages from the other participant as read
    ChatMessage.objects.filter(
        conversation=conversation,
        is_read=False
    ).exclude(
        sender=request.user
    ).update(is_read=True)

    chat_messages = conversation.messages.select_related(
        'sender'
    ).all()

    other_participant = owner if request.user == renter else renter

    return render(
        request,
        'equipment/chat_room.html',
        {
            'conversation': conversation,
            'chat_messages': chat_messages,
            'other_participant': other_participant
        }
    )


# Send a message in an existing conversation
@login_required
@require_POST
def send_chat_message(request, pk):
    conversation = get_object_or_404(
        Conversation.objects.select_related(
            'rental_request',
            'rental_request__equipment'
        ),
        pk=pk,
        rental_request__status='ACCEPTED'
    )

    renter = conversation.rental_request.renter
    owner = conversation.rental_request.equipment.owner

    # Only the renter and equipment owner can send messages
    if request.user != renter and request.user != owner:
        messages.error(
            request,
            'You are not allowed to send messages in this conversation.'
        )
        return redirect('message_inbox')

    content = request.POST.get('content', '').strip()

    if not content:
        messages.error(request, 'Please enter a message before sending.')
        return redirect('chat_room', pk=conversation.pk)

    ChatMessage.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content
    )

    # Update the conversation's latest activity time
    conversation.save(update_fields=['updated_at'])

    return redirect('chat_room', pk=conversation.pk)
