from django.urls import path
from . import views

urlpatterns = [
    # Certificate views
    path('', views.certificate_list, name='certificate_list'),
    path('<uuid:certificate_id>/', views.certificate_detail, name='certificate_detail'),
    path('<uuid:certificate_id>/download/', views.download_certificate, name='download_certificate'),
    path('<uuid:certificate_id>/share/', views.share_certificate, name='share_certificate'),
    
    # Blockchain verification
    path('verify/', views.verify_certificate, name='verify_certificate'),
    path('<uuid:certificate_id>/verify/', views.verify_certificate_detail, name='verify_certificate_detail'),
    path('<uuid:certificate_id>/blockchain-info/', views.blockchain_info, name='blockchain_info'),
    
    # Certificate issuance (for instructors/admins)
    path('issue/<int:course_id>/', views.issue_certificates, name='issue_certificates'),
    path('issue/<int:course_id>/<int:user_id>/', views.issue_certificate, name='issue_certificate'),
    path('<uuid:certificate_id>/revoke/', views.revoke_certificate, name='revoke_certificate'),
    
    # Certificate templates
    path('templates/', views.template_list, name='certificate_template_list'),
    path('templates/<int:template_id>/', views.template_detail, name='certificate_template_detail'),
    path('templates/create/', views.create_template, name='create_certificate_template'),
    path('templates/<int:template_id>/edit/', views.edit_template, name='edit_certificate_template'),
    
    # Certification authorities
    path('authorities/', views.authority_list, name='certification_authority_list'),
    path('authorities/<int:authority_id>/', views.authority_detail, name='certification_authority_detail'),
]
