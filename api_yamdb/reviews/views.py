from django.shortcuts import get_object_or_404

from rest_framework import viewsets

from api.permissions import IsAuthorOrReadOnly, IsModeratorOrAdminOrReadOnly
from .serializers import ReviewSerializer, CommentSerializer
from .models import Review, Title


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrReadOnly | IsModeratorOrAdminOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(title_id=self.kwargs['title_id'])

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(
            author=self.request.user, title=title
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly | IsModeratorOrAdminOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(
            Review, pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id')
        )
        serializer.save(
            author=self.request.user, review=review
        )
