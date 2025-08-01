from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from urllib.parse import quote
from django.db.models import Count
import mimetypes
import hashlib


# --- Registration View ---
def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        create_user_with_profile(user, role='standard')  # safely defaults
        messages.success(request, 'Account created. You can now log in.')
        return redirect('login')

    return render(request, 'accounts/register.html')


# --- Login View ---
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            ActivityLog.objects.create(user=user, action='login')
            return redirect('dashboard')
        else:
            messages.warning(request, 'Invalid credentials.')

    return render(request, 'accounts/login.html')

@login_required
def dashboard(request):
    user = request.user

    recent_uploads = Document.objects.filter(uploaded_by=user, is_deleted=False).order_by('-uploaded_at')[:5]
    recent_activities = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:5]

    return render(request, 'dashboard.html', {
        'recent_uploads': recent_uploads,
        'recent_activities': recent_activities,
    })

@login_required
def upload_document(request):
    folders = Folder.objects.all()

    if request.method == 'POST':
        name = request.POST['name']
        file = request.FILES['file']
        folder_id = request.POST.get('folder')
        folder = Folder.objects.get(id=folder_id) if folder_id else None
        
        if not name:
            name = file.name

        doc = Document.objects.create(
            name=name,
            file=file,
            folder=folder,
            uploaded_by=request.user,
            uploaded_at=timezone.now()
        )

        # SHA256 hashing
        sha256 = hashlib.sha256()
        for chunk in file.chunks():
            sha256.update(chunk)
        hash_value = sha256.hexdigest()
        
        DocumentVersion.objects.create(
            document=doc,
            version_file=doc.file,
            version_number=1
        )

        FileHash.objects.create(document=doc, hash_value=hash_value)
        ActivityLog.objects.create(user=request.user, action='upload', document=doc)

        return redirect('dashboard')


    return render(request, 'documents/upload.html', {'folders': folders})

def smart_view(request, doc_id):
    doc = Document.objects.get(id=doc_id)
    file_url = request.build_absolute_uri(doc.file.url)
    mimetype, _ = mimetypes.guess_type(doc.file.path)

    if mimetype and mimetype.startswith('image'):
        return redirect(doc.file.url)

    elif mimetype == 'application/pdf':
        return redirect(doc.file.url)

    elif doc.file.name.lower().endswith(('.doc', '.docx', '.pptx', '.xlsx')):
        encoded_url = quote(file_url, safe='')
        office_url = f"https://view.officeapps.live.com/op/embed.aspx?src={encoded_url}"
        return redirect(office_url)

    else:
        return redirect('dashboard.html', {
            'message': "This file cannot be previewed in the browser."
        })

@login_required
def my_files(request):
    files = Document.objects.filter(uploaded_by=request.user, is_deleted=False).order_by('-uploaded_at')
    return render(request, 'documents/my_files.html', {'files': files})

@require_POST
@login_required
def delete_file(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id, uploaded_by=request.user, is_deleted=False)
    doc.is_deleted = True
    doc.deleted_at = timezone.now()
    doc.save()
    messages.success(request, f"'{doc.name or doc.file.name}' has been deleted.")
    return redirect('my_files')

@login_required
def trash(request):
    trashed_files = Document.objects.filter(uploaded_by=request.user, is_deleted=True).order_by('-deleted_at')
    return render(request, 'documents/trash.html', {'files': trashed_files})

@require_POST
@login_required
def restore_file(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id, uploaded_by=request.user, is_deleted=True)
    doc.is_deleted = False
    doc.deleted_at = None
    doc.save()
    messages.success(request, "File restored successfully.")
    return redirect('trash')

@require_POST
@login_required
def permanent_delete_file(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id, uploaded_by=request.user, is_deleted=True)
    file_path = doc.file.path
    doc.delete()
    if os.path.exists(file_path):
        os.remove(file_path)
    messages.success(request, "File permanently deleted.")
    return redirect('trash')

@login_required
def analytics(request):
    user = request.user

    # Total uploads
    total_uploads = Document.objects.filter(uploaded_by=user, is_deleted=False).count()

    # Total views/downloads on user's files
    user_docs = Document.objects.filter(uploaded_by=user)
    total_views = UsageStat.objects.filter(document__in=user_docs, action='view').count()
    total_downloads = UsageStat.objects.filter(document__in=user_docs, action='download').count()

    # Top 5 most viewed
    top_docs = UsageStat.objects.filter(document__in=user_docs, action='view') \
        .values('document__id', 'document__name') \
        .annotate(view_count=Count('id')) \
        .order_by('-view_count')[:5]

    context = {
        'total_uploads': total_uploads,
        'total_views': total_views,
        'total_downloads': total_downloads,
        'top_docs': top_docs
    }
    return render(request, 'documents/analytics.html', context)

@login_required
def create_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name, created_by=request.user)
            messages.success(request, "Category created successfully.")
            return redirect('create_category')
        else:
            messages.warning(request, "Name is required.")
    return render(request, 'documents/create_category.html')

@login_required
def create_folder(request):
    categories = Category.objects.filter(created_by=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        if name and category_id:
            category = Category.objects.get(id=category_id)
            Folder.objects.create(name=name, category=category)
            messages.success(request, "Folder created successfully.")
            return redirect('create_folder')
        else:
            messages.error(request, "All fields are required.")
    return render(request, 'documents/create_folder.html', {'categories': categories})


@login_required
def view_categories_and_folders(request):
    categories = Category.objects.filter(created_by=request.user).prefetch_related('folder_set')
    return render(request, 'documents/categories_folders.html', {'categories': categories})

@login_required
def view_folder_documents(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    documents = Document.objects.filter(folder=folder, is_deleted=False)
    return render(request, 'documents/folder_documents.html', {'folder': folder, 'documents': documents})

@login_required
def upload_new_version(request, doc_id):
    document = get_object_or_404(Document, id=doc_id, uploaded_by=request.user, is_deleted=False)

    if request.method == 'POST':
        new_file = request.FILES.get('version_file')
        if new_file:
            # increment version number
            current_versions = DocumentVersion.objects.filter(document=document).count()
            version_number = current_versions + 1

            DocumentVersion.objects.create(
                document=document,
                version_file=new_file,
                version_number=version_number
            )

            # update original document to point to new version
            document.file = new_file
            document.uploaded_at = timezone.now()
            document.save()

            ActivityLog.objects.create(user=request.user, action='modify', document=document)

            messages.success(request, "New version uploaded.")
            return redirect('my_files')

    return render(request, 'documents/upload_version.html', {'document': document})

@login_required
def document_versions(request, doc_id):
    document = get_object_or_404(Document, id=doc_id, uploaded_by=request.user)
    versions = DocumentVersion.objects.filter(document=document).order_by('-version_number')
    return render(request, 'documents/version_history.html', {'document': document, 'versions': versions})

@login_required
@require_POST
def restore_version(request, version_id):
    version = get_object_or_404(DocumentVersion, id=version_id)
    document = version.document

    # Create a new version entry using the restored file
    version_number = DocumentVersion.objects.filter(document=document).count() + 1
    DocumentVersion.objects.create(
        document=document,
        version_file=version.version_file,
        version_number=version_number
    )

    # Replace current file in main document
    document.file = version.version_file
    document.uploaded_at = timezone.now()
    document.save()

    ActivityLog.objects.create(user=request.user, action='modify', document=document)

    messages.success(request, f"Restored to version {version.version_number} (saved as version {version_number}).")
    return redirect('document_versions', doc_id=document.id)





# --- Logout View ---
def logout_user(request):
    ActivityLog.objects.create(user=request.user, action='logout')
    logout(request)
    return redirect('login')
