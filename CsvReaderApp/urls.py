from django.urls import path
from . import views  # Ensure views is imported from your app
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('select-column/', views.select_column, name='select_column'),
    path('generate-charts/', views.generate_charts, name='generate_charts'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
