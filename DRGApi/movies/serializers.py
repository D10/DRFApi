from rest_framework import serializers

from .models import Movie, Reviews, Rating, Actor


class FilterReviewListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class RecursiveSerializer(serializers.Serializer):

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class ActorDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Actor
        fields = '__all__'


class ActorListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Actor
        fields = ("id", "name", "image")


class MovieListSerializer(serializers.ModelSerializer):

    # Список фильмов

    rating_user = serializers.BooleanField()
    middle_star = serializers.IntegerField()

    class Meta:
        model = Movie
        fields = ('id', 'title', 'tagline', 'rating_user', 'middle_star')


class ReviewCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):

    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterReviewListSerializer
        model = Reviews
        fields = ("name", "email", "text", "children")


class MovieDetailSerializer(serializers.ModelSerializer):

    # Выборочный фильм
    directors = ActorDetailSerializer(read_only=True, many=True)
    actors = ActorDetailSerializer(read_only=True, many=True)
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        fields = ('title', 'tagline', 'reviews', 'directors', 'actors')


class CreateRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        fields = ("star", "movie")

    def create(self, validated_data):
        rating, _ = Rating.objects.update_or_create(
            ip=validated_data.get('ip', None),
            movie=validated_data.get('movie', None),
            defaults={'star': validated_data.get("star")}
        )
        return rating
