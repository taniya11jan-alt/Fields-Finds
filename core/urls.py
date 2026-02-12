from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('discovery/', views.tool_discovery, name='tool_discovery'),
    path('tool/<int:tool_id>/', views.tool_detail, name='tool_detail'),
    path('profile/<str:username>/', views.public_profile, name='public_profile'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Tool management
    path('add-tool/', views.add_tool, name='add_tool'),

    # Booking
    path('booking/<int:booking_id>/<str:action>/', views.manage_booking, name='manage_booking'),

    # ✅ SINGLE PROOF PAGE
    path('booking/<int:booking_id>/proof/', views.upload_handover_proof, name='upload_handover_proof'),

    # Review
    path('booking/<int:booking_id>/review/', views.leave_review, name='leave_review'),

    # Chat
    path('chat/<int:booking_id>/', views.chat_room, name='chat_room'),

    # Report
    path('tool/<int:tool_id>/report/', views.report_tool, name='report_tool'),
]
