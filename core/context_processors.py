from .models import Booking, Message

def notification_counts(request):
    if request.user.is_authenticated:
        # Count incoming requests for lenders
        pending_requests = Booking.objects.filter(tool__owner=request.user, status='pending').count()
        
        # Count unread messages (if you add an is_read field to Message model)
        # For now, let's stick to active bookings that need attention
        return {
            'nav_notification_count': pending_requests
        }
    return {'nav_notification_count': 0}