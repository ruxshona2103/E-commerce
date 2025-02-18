from django.db import  models
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as django_filters
from rest_framework import filters

from .models import Product, Review, Category
from .serializers import ProductSerializer, CategorySerializer, ReviewSerializer
from .filters import ProductFilter



class CustomPagination(PageNumberPagination):
    page_size = 4

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    pagination_class = CustomPagination

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer

    pagination_class = CustomPagination

    filter_backends = (django_filters.DjangoFilterBackend, filters.SearchFilter)
    filterset_class = ProductFilter
    search_fields = ['name', 'description']




    def list(self, request, *args, **kwargs):
        category = request.query_params.get('category', None)
        if category is not None:
            self.queryset = self.queryset.filter(category=category)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        related_products = Product.objects.filter(category=instance.category).exclude(id = instance.id)[:7]
        related_serializer = ProductSerializer(related_products, many=True)
        return Response({
            'product':serializer.data,
            'related_products': related_serializer.data
        })


    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        top_products = Product.objects.annotate(avg_rating = models.Avg('reviews__rating')).order_by('-avg_rating')[:2]
        serializer = ProductSerializer(top_products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def average_rating(self, request, pk=None):
        product = self.get_object()
        reviews = product.reviews.all()

        if reviews.count() == 0:
            return Response({'average_rating':"No reviews yet!"})

        avg_rating = sum([review.rating for review in reviews]) / reviews.counts

        return Response({'average_rating': avg_rating})








































