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
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)