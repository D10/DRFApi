from django.db import models
from django.http import HttpResponse
from rest_framework import generics, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .models import Movie, Actor
from .serializers import MovieListSerializer, MovieDetailSerializer, ReviewCreateSerializer, CreateRatingSerializer, \
    ActorListSerializer, ActorDetailSerializer
from .service import get_client_ip, MovieFilter, PaginationMovies


def hello(request):
    return HttpResponse('<h1>Hello!!!</h1>')


'''API, написанное на viewsets классах'''


class MovieViewSet(viewsets.ReadOnlyModelViewSet):

    filter_backends = (DjangoFilterBackend, )
    filterset_class = MovieFilter
    pagination_class = PaginationMovies

    def get_queryset(self):
        movies = Movie.objects.filter(draft=False).annotate(
            rating_user=models.Count("ratings", filter=models.Q(ratings__ip=get_client_ip(self.request)))
        ).annotate(
            middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
        )
        return movies

    def get_serializer_class(self):
        if self.action == 'list':
            return MovieListSerializer
        elif self.action == 'retrieve':
            return MovieDetailSerializer


class ReviewCreateViewSet(viewsets.ModelViewSet):

    serializer_class = ReviewCreateSerializer


class AddStarRatingViewSet(viewsets.ModelViewSet):

    serializer_class = CreateRatingSerializer

    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip(self.request))


class ActorsViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Actor.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ActorListSerializer
        elif self.action == 'retrieve':
            return ActorDetailSerializer


'''API, написанное на generic классах'''


class MovieListView(generics.ListAPIView):

    # Просмотр полного списка фильмов с показом наличия оценки юзера и средней оценки от всех юзеров

    serializer_class = MovieListSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = MovieFilter
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        movies = Movie.objects.filter(draft=False).annotate(
            rating_user=models.Count("ratings", filter=models.Q(ratings__ip=get_client_ip(self.request)))
        ).annotate(
            middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
        )
        return movies


class MovieDetailView(generics.RetrieveAPIView):

    # Просмотр информации о конкретном фильме

    queryset = Movie.objects.filter(draft=False)
    serializer_class = MovieDetailSerializer


class ReviewCreateView(generics.CreateAPIView):

    # POST запрос для добавления отзыва к фильму

    serializer_class = ReviewCreateSerializer


class AddStarRatingView(generics.CreateAPIView):

    # POST запрос для добавления рейтинга к фильму

    serializer_class = CreateRatingSerializer

    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip(self.request))


class ActorsListView(generics.ListAPIView):

    # Вывод списка актеров и режисеров

    queryset = Actor.objects.all()
    serializer_class = ActorListSerializer


class ActorsDetailView(generics.RetrieveAPIView):

    # Вывод конкретного актера или режисера

    queryset = Actor.objects.all()
    serializer_class = ActorDetailSerializer
