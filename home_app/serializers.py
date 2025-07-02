from rest_framework import serializers
from .models import User, Journal, Volume, Issue, Article


# -------------------------
# User Serializer
# -------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'email_verified', 'image',
            'role', 'is_active', 'is_staff','bio', 'Institution'
        ]
        read_only_fields = ['id', 'is_active', 'is_staff']


# -------------------------
# Journal Serializer
# -------------------------
# class JournalSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Journal
#         fields = [
#             'id', 'name', 'slug', 'description', 'issn',
#             'created_at', 'updated_at'
#         ]
#         read_only_fields = ['id', 'created_at', 'updated_at']

from django.utils.text import slugify
from rest_framework import serializers

class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = ['id', 'name', 'slug', 'description', 'issn', 'created_at',"" 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_slug(self, value):
        # Ensure slug is slugified even if some client provides it
        return slugify(value) if value else slugify(self.initial_data.get('name', ''))

    def create(self, validated_data):
        if not validated_data.get('slug'):
            validated_data['slug'] = slugify(validated_data.get('name', ''))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if not validated_data.get('slug') and 'name' in validated_data:
            validated_data['slug'] = slugify(validated_data['name'])
        return super().update(instance, validated_data)

# -------------------------
# Volume Serializer
# -------------------------

class Issue3Serializer(serializers.ModelSerializer):
    # volume = VolumeSerializer(read_only=True)
    # volume_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Volume.objects.all(), source='volume', write_only=True
    # )
    
    class Meta:
        model = Issue
        fields ="__all__"



class VolumeSerializer(serializers.ModelSerializer):
    journal = JournalSerializer(read_only=True)
    journal_id = serializers.PrimaryKeyRelatedField(
        queryset=Journal.objects.all(), source='journal', write_only=True
    )
    issues = Issue3Serializer(many=True, read_only=True)  # 🔁 This gives full issue data

    class Meta:
        model = Volume
        fields = [
            'id', 'number', 'year', 'journal', 'journal_id',
            'created_at', 'updated_at', 'issues'  # 🔁 renamed from issue_ids
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

# -------------------------
# Issue Serializer
# -------------------------
class IssueSerializer(serializers.ModelSerializer):
    volume = VolumeSerializer(read_only=True)
    volume_id = serializers.PrimaryKeyRelatedField(
        queryset=Volume.objects.all(), source='volume', write_only=True
    )
    

    class Meta:
        model = Issue
        fields = [
            'id', 'number', 'title', 'month',
            'volume', 'volume_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# -------------------------
# Article Serializer
# # -------------------------
# class ArticleSerializer(serializers.ModelSerializer):
#     issue = IssueSerializer(read_only=True)
#     issue_id = serializers.PrimaryKeyRelatedField(
#         queryset=Issue.objects.all(), source='issue', write_only=True, allow_null=True, required=False
#     )

#     publisher = UserSerializer(read_only=True)
#     publisher_id = serializers.PrimaryKeyRelatedField(
#         queryset=User.objects.all(), source='publisher', write_only=True
#     )

#     class Meta:
#         model = Article
#         fields = [
#             'id', 'title', 'slug', 'authors', 'abstract',
#             'file_url', 'status', 'payment_proof', 'payment_verified',
#             'issue', 'issue_id',
#             'publisher', 'publisher_id',
#             'created_at', 'updated_at'
#         ]
#         read_only_fields = ['id', 'created_at', 'updated_at']

class ArticleSerializer(serializers.ModelSerializer):
    issue = IssueSerializer(read_only=True)
    # Change publisher from read_only to a primary key field:
    publisher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Article
        fields = '__all__'

from rest_framework import serializers
from .models import Journal, Volume, Issue


class IssueWithCountSerializer(serializers.ModelSerializer):
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = ['id', 'number', 'month', 'article_count']

    def get_article_count(self, obj):
        return obj.articles.count()


class VolumeWithIssuesSerializer(serializers.ModelSerializer):
    issues = IssueWithCountSerializer(many=True)

    class Meta:
        model = Volume
        fields = ['id', 'number', 'year', 'issues']


class JournalWithNestedSerializer(serializers.ModelSerializer):
    volumes = VolumeWithIssuesSerializer(many=True)

    class Meta:
        model = Journal
        fields = ['id', 'name', 'slug', 'description', 'issn', 'created_at', 'updated_at', 'volumes']


# New serializer for detailed view (used with slug)
class JournalDetailSerializer(serializers.ModelSerializer):
    volumes = serializers.SerializerMethodField()

    class Meta:
        model = Journal
        fields = ['id', 'name', 'slug', 'description', 'issn', 'created_at', 'updated_at', 'volumes']

    def get_volumes(self, obj):
        volumes = obj.volumes.all()
        return VolumeWithIssuesSerializer(volumes, many=True, context=self.context).data



from django.contrib.auth.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError("Passwords must match.")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        # Assign publisher role and activate
        user.is_active = True
        user.save()
        return user
