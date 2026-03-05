from django.urls import path, include


urlpatterns = [
    path('v1/', include('movies_together.api.v1.urls')),
]
