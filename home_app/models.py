from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.text import slugify
import uuid

# -------------------------
# ENUMs using Choices
# -------------------------
class RoleChoices(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    PUBLISHER = "PUBLISHER", "Publisher"
    REVIEWER = "REVIEWER", "Reviewer"


class ArticleStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SUBMITTED = "SUBMITTED", "Submitted"
    UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    PUBLISHED = "PUBLISHED", "Published"


# -------------------------
# Custom User Manager
# -------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', RoleChoices.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# -------------------------
# Custom User Model
# -------------------------
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    bio = models.CharField(max_length=255, null=True, blank=True)
    Institution = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True)
    email_verified = models.DateTimeField(null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    password = models.CharField(max_length=128)
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.PUBLISHER
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email or "Unnamed User"


# -------------------------
# Journal
# -------------------------
class Journal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    issn = models.CharField(max_length=20, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# -------------------------
# Volume
# -------------------------
class Volume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.IntegerField()
    year = models.IntegerField()
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='volumes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('journal', 'number')

    def __str__(self):
        return f"Volume {self.number} ({self.year}) - {self.journal.name}"


# -------------------------
# Issue
# -------------------------
class Issue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.IntegerField()
    title = models.CharField(max_length=255, null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE, related_name='issues')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('volume', 'number')

    def __str__(self):
        return self.title or f"Issue {self.number}"


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    authors = models.TextField()
    abstract = models.TextField(null=True, blank=True)

    file = models.FileField(upload_to='articles/', null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT
    )
    payment_proof = models.FileField(upload_to='payment_proofs/', null=True, blank=True)
    payment_verified = models.BooleanField(default=False)

    issue = models.ForeignKey(
        'Issue',
        on_delete=models.CASCADE,
        related_name='articles',
        null=True,
        blank=True
    )
    publisher = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='articles'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while Article.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
