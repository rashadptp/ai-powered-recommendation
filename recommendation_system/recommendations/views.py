from rest_framework import viewsets, permissions
from .models import Product, UserInteraction, Recommendation, Notification
from .serializers import ProductSerializer, UserInteractionSerializer, RecommendationSerializer, NotificationSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from .recommendation import train_recommendation_model, recommend_products
from .tasks import update_recommendations


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
        return request.method in permissions.SAFE_METHODS

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

class UserInteractionViewSet(viewsets.ModelViewSet):
    queryset = UserInteraction.objects.all()
    serializer_class = UserInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def recommend(self, request):
        user = request.user

        # Train model and generate recommendations
        model, user_product_matrix = train_recommendation_model()
        
        if model is None or user_product_matrix.empty:
            return Response({'message': 'Not enough interaction data to generate recommendations.'}, status=400)

        # Check if user has interaction data
        if user.id not in user_product_matrix.index:
            return Response({'message': 'User has no interaction data.'}, status=404)

        recommended_products = recommend_products(user.id, model, user_product_matrix)
        
        if not recommended_products.exists():
            return Response({'message': 'No recommendations available for this user.'}, status=404)

        # Serialize the recommended products and return
        serializer = RecommendationSerializer(recommended_products, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Standard user interaction creation logic
        response = super().create(request, *args, **kwargs)
        
        # Trigger async recommendation update after interaction
        update_recommendations.delay(request.user.id)
        
        return response
        
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
