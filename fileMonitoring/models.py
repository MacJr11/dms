from django.db import models
from django.contrib.auth.models import User
import hashlib
import os
import uuid

# --- User Roles ---
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('standard', 'Standard User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


# --- Category & Folder ---
class Category(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

class Folder(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_locked = models.BooleanField(default=False)


# --- Document & Versioning ---
def document_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('documents', new_filename)

class Document(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=document_upload_path)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_file = models.FileField(upload_to=document_upload_path)
    version_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


# --- Integrity Check ---
class FileHash(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE)
    hash_value = models.CharField(max_length=64)  # SHA-256
    last_checked = models.DateTimeField(auto_now=True)

    @staticmethod
    def generate_sha256(file_path):
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()


# --- Activity Logging ---
class ActivityLog(models.Model):
    ACTIONS = [
        ('upload', 'Upload'),
        ('download', 'Download'),
        ('delete', 'Delete'),
        ('modify', 'Modify'),
        ('login', 'Login'),
        ('logout', 'Logout')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTIONS)
    document = models.ForeignKey(Document, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)


# --- Custom Monitored ---
class MonitoredFile(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE)
    is_monitored = models.BooleanField(default=True)


# --- Analytics Placeholder (e.g., usage counters) ---
class UsageStat(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    accessed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20)
    accessed_at = models.DateTimeField(auto_now_add=True)


# --- Admin Access Control Utility ---
def user_has_admin_access(user):
    try:
        return user.userprofile.role == 'admin'
    except UserProfile.DoesNotExist:
        return False
