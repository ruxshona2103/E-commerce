from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, timedelta
from products.models import Product, ProductViewHistory, FlashSale
from rest_framework import generics, serializers, status
from django_filters import rest_framework as django_filters
from rest_framework.pagination import PageNumberPagination

from products.filters import FlashSaleFilter

class CustomPagination(PageNumberPagination):
    page_size = 2


class FlashSaleListCreateView(generics.ListCreateAPIView):
    queryset = FlashSale.objects.all()

    class FlashSaleSerializer(serializers.ModelSerializer):
        class Meta:
            model = FlashSale
            fields = ('id', 'product', 'discount_percentage', 'start_time', 'end_time')

    serializer_class = FlashSaleSerializer
    pagination_class = CustomPagination

    filter_backends = (django_filters.DjangoFilterBackend , )
    filterset_class = FlashSaleFilter


@api_view(['GET'])
def check_flash_sale(request, product_id):
    try:
        product = Product.objects.get(id = product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not fount."}, status=status.HTTP_404_NOT_FOUND)

    user_viewed = ProductViewHistory.objects.filter(user=request.user, product=product).exists()

    upcoming_flash_sale = FlashSale.objects.filter(
        product = product,
        start_time__lte = datetime.now() + timedelta(hours=24)
    ).first()

    if user_viewed and upcoming_flash_sale:
        discount = upcoming_flash_sale.discount_percentage
        start_time = upcoming_flash_sale.start_time
        end_time = upcoming_flash_sale.end_time
        return Response(
            {
                "message": f"This product will be on a {discount}% off flash sale !",
                "start_time": start_time,
                "end_time": end_time
             }
        )
    else:
        return Response({
            "message": "No upcoming flash sale for this product."
        })







