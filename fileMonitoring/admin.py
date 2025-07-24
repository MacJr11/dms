from django.contrib import admin
from .models import (
    UserProfile, Category, Folder, Document, DocumentVersion,
    FileHash, ActivityLog, MonitoredFile, UsageStat
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username', 'role')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by')
    search_fields = ('name',)

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_locked')
    list_filter = ('is_locked',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'folder', 'uploaded_by', 'uploaded_at', 'is_deleted')
    list_filter = ('is_deleted',)
    search_fields = ('name',)

@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'version_number', 'created_at')

@admin.register(FileHash)
class FileHashAdmin(admin.ModelAdmin):
    list_display = ('document', 'hash_value', 'last_checked')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'document', 'timestamp')
    list_filter = ('action',)

@admin.register(MonitoredFile)
class MonitoredFileAdmin(admin.ModelAdmin):
    list_display = ('document', 'is_monitored')

@admin.register(UsageStat)
class UsageStatAdmin(admin.ModelAdmin):
    list_display = ('document', 'accessed_by', 'action', 'accessed_at')
    list_filter = ('action',)
