from rest_framework.urlpatterns import format_suffix_patterns

from . import views
from django.urls import path

app_name = 'articles'
urlpatterns = [
    path('', views.ArticlesController.as_view()),
    path('<int:pk>/', views.ArticleDetailsController.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
