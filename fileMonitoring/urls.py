from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('upload/', views.upload_document, name='upload_document'),
    path('preview/<int:doc_id>/', views.smart_view, name='smart_preview'),
    path('my-files/', views.my_files, name='my_files'),
    path('my-files/delete/<int:doc_id>/', views.delete_file, name='delete_file'),
    path('my-files/trash/', views.trash, name='trash'),
    path('my-files/restore/<int:doc_id>/', views.restore_file, name='restore_file'),
    path('my-files/permanent-delete/<int:doc_id>/', views.permanent_delete_file, name='permanent_delete_file'),
    path('analytics/', views.analytics, name='analytics'),
    path('categories/new/', views.create_category, name='create_category'),
    path('folders/new/', views.create_folder, name='create_folder'),
    path('folders/', views.view_categories_and_folders, name='view_folders'),
    path('folder/<int:folder_id>/documents/', views.view_folder_documents, name='view_folder_documents'),
    path('document/<int:doc_id>/upload-version/', views.upload_new_version, name='upload_new_version'),
    path('document/<int:doc_id>/versions/', views.document_versions, name='document_versions'),
    path('version/<int:version_id>/restore/', views.restore_version, name='restore_version'),
    path('document/<int:doc_id>/integrity-history/', views.integrity_history, name='integrity_history'),
    path('shared-documents/', views.shared_documents, name='shared_documents'),
    path('document/<int:doc_id>/access-log/', views.access_log, name='access_log'),path('document/<int:doc_id>/toggle-share/', views.toggle_share, name='toggle_share'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)