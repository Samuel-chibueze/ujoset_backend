from django.urls import path
from .views import (
    JournalWithDetailsView,
    UserListView,
    JournalListCreateView, JournalDetailView,
    VolumeListCreateView, VolumeDetailView,
    IssueListCreateView, IssueDetailView,
    ArticleListCreateView, ArticleDetailView,
    JournalDetailVolume,IssueDetailAPIView,
    SignupView,LoginView,ArticlesByIssueSlugView
)

urlpatterns = [
    # Users
    path('users/', UserListView.as_view(), name='user-list'),
   path('signup/', SignupView.as_view()),
    path('login/', LoginView.as_view()),
    # Journals
    path('journals/detailed/', JournalWithDetailsView.as_view(), name='journal-detailed-list'),
    path('journals_data/<str:slug>', JournalDetailVolume.as_view(), name='journal-list'),
    path('journals/', JournalListCreateView.as_view(), name='journal-list-create'),
    path('journals/<str:slug>/', JournalDetailView.as_view(), name='journal-detail'),
    path('journals/<slug:slug>/volumes/<str:volume_number>/<str:issue_number>/',IssueDetailAPIView.as_view(),name='issue-detail'),
    # Volumes
    path('volumes/', VolumeListCreateView.as_view(), name='volume-list-create'),
    path('volumes/<str:pk>/', VolumeDetailView.as_view(), name='volume-detail'),
    

    # Issues
    path('issues/', IssueListCreateView.as_view(), name='issue-list-create'),
    path('issues/<str:pk>/', IssueDetailView.as_view(), name='issue-detail'),

    # Articles
    path('articles/', ArticleListCreateView.as_view(), name='article-list-create'),
    path('articles/<str:slug>/', ArticleDetailView.as_view(), name='article-detail'),
    path('articles/issue/<str:slug>/', ArticlesByIssueSlugView.as_view(), name='articles-by-issue-slug'),]
