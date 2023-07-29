from Cards import views
from django.urls import path

urlpatterns = [
    path('', views.index, name = 'index'),
    path('show_image', views.show_image, name = 'video_feed'),
    path('json_data', views.detection_json, name = 'json_data'),
]
