from celery import shared_task
from .recommendation import train_recommendation_model, recommend_products
from .models import Recommendation, Product


@shared_task
def update_recommendations(user_id):
    model = train_recommendation_model()
    recommended_products = recommend_products(user_id, model)
    # Store recommendations in Recommendation model
    for product in recommended_products:
        Recommendation.objects.create(user_id=user_id, product=product, score=0.9)