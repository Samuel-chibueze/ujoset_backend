from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
# from home_app.views import FrontendAppView
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('home_app.urls')),
    # re_path(r'^.*$', FrontendAppView.as_view()),  # catch-all to serve index.html for React
]

if settings.DEBUG:
    # Serve uploaded media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # # Serve React build's asset files in development
    # urlpatterns += static(
    #     '/static/',  # This must match STATIC_URL in settings.py
    #     document_root=os.path.join(settings.BASE_DIR, 'frontend', 'build', 'static')
    # )
