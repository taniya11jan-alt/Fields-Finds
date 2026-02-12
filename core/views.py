from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from datetime import datetime

from .models import Profile, Tool, Booking, Message, Review, Report
from .forms import RegistrationForm, ToolForm


# ---------- AUTH ----------
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            profile, created = Profile.objects.get_or_create(user=user)
            profile.mobile_number = user.username
            profile.village = form.cleaned_data.get('village')
            profile.district = form.cleaned_data.get('district')
            profile.pincode = form.cleaned_data.get('pincode')
            profile.save()

            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('dashboard')
    else:
        form = RegistrationForm()

    return render(request, 'core/register.html', {'form': form})


def public_profile(request, username):
    user_obj = get_object_or_404(User, username=username)
    user_tools = Tool.objects.filter(owner=user_obj, is_approved=True)
    return render(request, 'core/public_profile.html', {
        'profile_user': user_obj,
        'tools': user_tools
    })


# ---------- STATIC ----------
def home(request):
    recent_tools = Tool.objects.filter(is_approved=True).order_by('-id')[:6]
    return render(request, 'core/home.html', {'tools': recent_tools})


def about_view(request):
    return render(request, 'core/about.html')


def contact_view(request):
    return render(request, 'core/contact.html')


# ---------- DISCOVERY ----------
def tool_discovery(request):
    query = request.GET.get('search', '')
    pincode = request.GET.get('location', '')
    tools = Tool.objects.filter(is_approved=True)

    if query:
        tools = tools.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if pincode:
        tools = tools.filter(owner__profile__pincode=pincode)

    return render(request, 'core/discovery.html', {'tools': tools})


# ---------- TOOL DETAIL ----------
def tool_detail(request, tool_id):
    tool = get_object_or_404(Tool, id=tool_id, is_approved=True)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.info(request, "Please login to book this tool.")
            return redirect('login')

        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date and end_date:
            d1 = datetime.strptime(start_date, '%Y-%m-%d')
            d2 = datetime.strptime(end_date, '%Y-%m-%d')
            days = max((d2 - d1).days, 1)

            Booking.objects.create(
                tool=tool,
                borrower=request.user,
                start_date=start_date,
                end_date=end_date,
                status='pending',
                total_price=tool.price_per_day * days
            )
            messages.success(request, "Booking request sent!")
            return redirect('dashboard')

        messages.error(request, "Please select valid dates.")

    return render(request, 'core/tool_detail.html', {'tool': tool})


# ---------- DASHBOARD ----------
@login_required
def dashboard(request):
    context = {
        'my_borrowings': Booking.objects.filter(borrower=request.user),
        'my_tools': Tool.objects.filter(owner=request.user),
        'incoming_requests': Booking.objects.filter(tool__owner=request.user),
        'all_tools': Tool.objects.filter(is_approved=True).exclude(owner=request.user)[:8],
    }
    return render(request, 'core/dashboard.html', context)


# ---------- BOOKING APPROVAL ----------
@login_required
def manage_booking(request, booking_id, action):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.tool.owner != request.user:
        return HttpResponseForbidden("Not authorized")

    if action == 'approve':
        booking.status = 'approved'
        messages.success(request, "Booking approved")
    elif action == 'reject':
        booking.status = 'rejected'
        messages.error(request, "Booking rejected")

    booking.save()
    return redirect('dashboard')

@login_required
def upload_handover_proof(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # 🔓 allow borrower ONLY (you are uploading from My Borrowings)
    if booking.borrower != request.user:
        messages.error(request, "You are not allowed to upload proof for this booking.")
        return redirect('dashboard')

    if request.method == 'POST' and request.FILES.get('proof_image'):
        file = request.FILES['proof_image']

        if booking.status == 'approved':
            booking.pickup_proof = file
            booking.status = 'picked_up'

        elif booking.status == 'picked_up':
            booking.return_proof = file
            booking.status = 'returned'

        booking.save()
        messages.success(request, "Proof uploaded successfully.")

    return redirect('dashboard')


# ---------- REVIEWS ----------
@login_required
def leave_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        Review.objects.create(
            booking=booking,
            reviewer=request.user,
            reviewee=booking.tool.owner if request.user == booking.borrower else booking.borrower,
            rating=request.POST.get('rating'),
            comment=request.POST.get('comment')
        )
        messages.success(request, "Review submitted")

    return redirect('dashboard')


# ---------- CHAT ----------
@login_required
def chat_room(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.user not in [booking.borrower, booking.tool.owner]:
        return HttpResponseForbidden("Access denied")

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                booking=booking,
                sender=request.user,
                content=content
            )
            return redirect('chat_room', booking_id=booking_id)

    chat_messages = Message.objects.filter(booking=booking).order_by('timestamp')
    return render(request, 'core/chat.html', {
        'booking': booking,
        'messages_list': chat_messages
    })


# ---------- ADD TOOL ----------
@login_required
def add_tool(request):
    if request.method == 'POST':
        form = ToolForm(request.POST, request.FILES)
        if form.is_valid():
            tool = form.save(commit=False)
            tool.owner = request.user
            tool.is_approved = False
            tool.save()
            messages.success(request, "Tool submitted for admin approval")
            return redirect('dashboard')
    else:
        form = ToolForm()

    return render(request, 'core/add_tool.html', {'form': form})


# ---------- REPORT ----------
@login_required
def report_tool(request, tool_id):
    tool = get_object_or_404(Tool, id=tool_id)

    if request.method == 'POST':
        Report.objects.create(
            tool=tool,
            reporter=request.user,
            reason=request.POST.get('reason'),
            description=request.POST.get('description')
        )
        messages.success(request, "Tool reported successfully.")
        return redirect('tool_detail', tool_id=tool.id)

    return render(request, 'core/report_tool.html', {'tool': tool})
