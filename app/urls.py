
from django.urls import path
from . import views

app_name = "app"

urlpatterns = [
    path("", views.homepage, name="homepage"),

    path('movies', views.movies, name="movies"),
    path('movies/<int:prime_id>/', views.movie, name="movie"),
    path('movies/filter/', views.movie_filter, name="movie_filter"),
    path('movies/search/', views.movies_ajax_search),

    # scrap data from IMDB website by going to this url.
    path('scrap', views.scrap, name="scrap"),
]
