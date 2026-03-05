from django.urls import path

from movies_together.api.v1 import views

urlpatterns = [
    path('movies_together/', views.MoviesListApi.as_view()),
    path('movies_together/<uuid:pk>/', views.MoviesDetailApi.as_view()),
]
