from django.urls import path
from . import views

urlpatterns = [
    # Chat rooms
    path('', views.chat_home, name='chat_home'),
    path('rooms/', views.chat_room_list, name='chat_room_list'),
    path('rooms/create/', views.create_chat_room, name='create_chat_room'),
    path('rooms/<int:room_id>/', views.chat_room_detail, name='chat_room_detail'),
    path('rooms/<int:room_id>/messages/', views.room_messages, name='room_messages'),
    
    # Direct messaging
    path('direct/', views.direct_message_list, name='direct_message_list'),
    path('direct/<int:user_id>/', views.direct_message_detail, name='direct_message_detail'),
    
    # Message handling
    path('api/send-message/<int:room_id>/', views.send_message, name='send_message'),
    path('api/edit-message/<int:message_id>/', views.edit_message, name='edit_message'),
    path('api/read-messages/<int:room_id>/', views.mark_messages_read, name='read_messages'),
    
    # Room management
    path('rooms/<int:room_id>/members/', views.room_members, name='room_members'),
    path('rooms/<int:room_id>/add-member/', views.add_room_member, name='add_room_member'),
    path('rooms/<int:room_id>/leave/', views.leave_chat_room, name='leave_chat_room'),
    
    # Live sessions
    path('live/', views.live_session_list, name='live_session_list'),
    path('live/create/', views.create_live_session, name='create_live_session'),
    path('live/<int:session_id>/', views.live_session_detail, name='live_session_detail'),
    path('live/<int:session_id>/join/', views.join_live_session, name='join_live_session'),
    path('live/<int:session_id>/end/', views.end_live_session, name='end_live_session'),
]
