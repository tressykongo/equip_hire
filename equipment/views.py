
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Equipment, RentalRequest
from .forms import EquipmentForm, RentalRequestForm
from accounts.models import Profile


# Check whether the logged-in user is an equipment owner
def is_equipment_owner(user):
    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={'role': 'RENTER'}
    )
    return profile.role == 'OWNER'


# Display equipment for browsing
def equipment_list(request):

    is_owner = False

    if request.user.is_authenticated and is_equipment_owner(request.user):
        equipment = Equipment.objects.filter(owner=request.user)
        is_owner = True
    else:
        equipment = Equipment.objects.filter(available=True)

    return render(
        request,
        'equipment/equipment_list.html',
        {
            'equipment': equipment,
            'is_owner': is_owner
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

    return render(request, 'equipment/add_equipment.html', {'form': form})


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

    return render(request, 'equipment/edit_equipment.html', {'form': form})


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
        {
            'rental_requests': rental_requests
        }
    )
