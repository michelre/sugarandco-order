from django.urls import path
from .views import HomeView, CreateView, SummaryView, DetailView

app_name = 'order'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('create/', CreateView.as_view(), name='create'),
    path('summary/', SummaryView.as_view(), name='summary'),
    path('detail/<int:order_id>/', DetailView.as_view(), name="detail"),    
]