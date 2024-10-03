import pandas as pd
from sklearn.neighbors import NearestNeighbors
from .views import *

def train_recommendation_model():
    interactions = pd.DataFrame(list(UserInteraction.objects.all().values()))
    
    user_product_matrix = interactions.pivot_table(index='user_id', columns='product_id', values='action', aggfunc='count', fill_value=0)
    
    model = NearestNeighbors(metric='cosine', algorithm='brute')
    model.fit(user_product_matrix)
    return model

def recommend_products(user_id, model, user_product_matrix):
    
    distances, indices = model.kneighbors(user_product_matrix.loc[user_id].values.reshape(1, -1), n_neighbors=5)
    recommended_products = user_product_matrix.columns[indices.flatten()]
    return Product.objects.filter(id__in=recommended_products)