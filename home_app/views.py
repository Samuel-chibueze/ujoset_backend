from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import HttpResponse


from .models import User, Journal, Volume, Issue, Article
from .serializers import (
    UserSerializer,
    JournalSerializer,
    VolumeSerializer,
    IssueSerializer,
    ArticleSerializer,
    JournalWithNestedSerializer,
    JournalDetailSerializer
)



class FrontendAppView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        try:
            return render(request, self.template_name)
        except:
            return HttpResponse(
                "index.html not found! Run `npm run build` in your React app.",
                status=501,
            )


class UserListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=500)
        
    def post(self, request):
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response({'errors': serializer.errors}, status=400)


# -------------------------------
# Journal Views
# -------------------------------

class JournalWithDetailsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        journals = Journal.objects.prefetch_related(
            'volumes__issues__articles'
        ).all()
        serializer = JournalWithNestedSerializer(journals, many=True)
        return Response(serializer.data)


class JournalListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        journals = Journal.objects.all()
        serializer = JournalSerializer(journals, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = JournalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response({'errors': serializer.errors}, status=400)


class JournalDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        journal = get_object_or_404(Journal, slug=slug)
        serializer = JournalSerializer(journal)
        return Response(serializer.data)

    def put(self, request, slug):
        journal = get_object_or_404(Journal, slug=slug)
        serializer = JournalSerializer(journal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status=400)

    def delete(self, request, pk):
        journal = get_object_or_404(Journal, pk=pk)
        journal.delete()
        return Response({'detail': 'Deleted successfully.'}, status=204)

class JournalDetailVolume(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        journal = get_object_or_404(Journal, slug=slug)
        serializer = JournalDetailSerializer(journal, context={'request':request})
        return Response(serializer.data)
# -------------------------------
# Volume Views
# -------------------------------
class IssueDetailAPIView(APIView):
    def get(self, request, slug, volume_number, issue_number):
        try:
            issue = Issue.objects.select_related(
                'volume__journal'
            ).prefetch_related('articles').get(
                id=issue_number,  # ✅ Use UUID for issue
                volume__id=volume_number,  # ✅ Use UUID for volume
                volume__journal__slug=slug
            )
        except Issue.DoesNotExist:
            return Response({'detail': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)

        data = {
            'id': issue.id,
            'number': issue.number,
            'title': issue.title,
            'month': issue.month,
            'volume': {
                'id': issue.volume.id,
                'number': issue.volume.number,
                'year': issue.volume.year,
                'journal': {
                    'name': issue.volume.journal.name,
                    'slug': issue.volume.journal.slug,
                    'issn': issue.volume.journal.issn
                }
            },
            'articles': ArticleSerializer(issue.articles.all(), many=True,context={"request":request}).data
        }

        return Response(data, status=status.HTTP_200_OK)
    

class VolumeListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        volumes = Volume.objects.all()
        serializer = VolumeSerializer(volumes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VolumeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response({'errors': serializer.errors}, status=400)


class VolumeDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        volume = get_object_or_404(Volume, pk=pk)
        serializer = VolumeSerializer(volume)
        return Response(serializer.data)

    def put(self, request, pk):
        volume = get_object_or_404(Volume, pk=pk)
        serializer = VolumeSerializer(volume, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status=400)

    def delete(self, request, pk):
        volume = get_object_or_404(Volume, pk=pk)
        volume.delete()
        return Response({'detail': 'Deleted successfully.'}, status=204)


# -------------------------------
# Issue Views
# -------------------------------

class IssueListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        issues = Issue.objects.all()
        serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = IssueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response({'errors': serializer.errors}, status=400)


class IssueDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        issue = get_object_or_404(Issue, pk=pk)
        serializer = IssueSerializer(issue)
        return Response(serializer.data)

    def put(self, request, pk):
        issue = get_object_or_404(Issue, pk=pk)
        serializer = IssueSerializer(issue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status=400)

    def delete(self, request, pk):
        issue = get_object_or_404(Issue, pk=pk)
        issue.delete()
        return Response({'detail': 'Deleted successfully.'}, status=204)


# -------------------------------
# Article Views
# -------------------------------

class ArticleListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        # You can uncomment the next line if you want to auto-assign the logged-in user
        # data['publisher_id'] = request.user.id
        print(data)
        serializer = ArticleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response({'errors': serializer.errors}, status=400)


class ArticlesByIssueSlugView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        # Step 1: Find the issue by slug
        issue = get_object_or_404(Issue, id=slug)  # Make sure `Issue` model has a `slug` field

        # Step 2: Get all related articles
        articles = issue.articles.all()

        # Step 3: Serialize the article list
        serializer = ArticleSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data)
    

class ArticleDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        serializer = ArticleSerializer(article, context={'request':request})
        return Response(serializer.data)


    def put(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        serializer = ArticleSerializer(article, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status=400)

    def delete(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        article.delete()
        return Response({'detail': 'Deleted successfully.'}, status=204)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class SignupView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        username = request.data.get("name", "")

        if not email or not password:
            return Response({"error": "Email and password required"}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=400)

        user = User.objects.create_user(name=username, email=email, password=password)
        # user.first_name = username
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {"id":user.id, "email": user.email,"role": user.role,"name": user.name}
        })


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, username=email, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {"id":user.id,"email": user.email,"role": user.role,"name": user.name}
        })


# from rest_framework import status
# from rest_framework.authtoken.models import Token
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from django.contrib.auth import authenticate
# from .serializers import RegisterSerializer

# class RegisterView(APIView):
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         token = Token.objects.create(user=user)
#         return Response({
#             "token": token.key,
#             "user": {
#                 "id": user.id,
#                 "username": user.username,
#                 "email": user.email,
#                 "role": "PUBLISHER",
#                 "is_active": user.is_active
#             }
#         }, status=status.HTTP_201_CREATED)

# class LoginView(ObtainAuthToken):
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data,
#                                            context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, _ = Token.objects.get_or_create(user=user)
#         return Response({
#             "token": token.key,
#             "user": {
#                 "id": user.id,
#                 "username": user.username,
#                 "email": user.email,
#                 "role": "PUBLISHER",
#                 "is_active": user.is_active
#             }
#         })
