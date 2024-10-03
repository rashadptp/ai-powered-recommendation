from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *
from django.urls import path

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('products/', ProductViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('user-interactions/', UserInteractionViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('recommendations/', UserInteractionViewSet.as_view({'get': 'recommend'})),
    path('notifications/', NotificationViewSet.as_view({'get': 'list'})),
]
