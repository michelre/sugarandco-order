from django.urls import path
from .views import HomeView, CreateView, SummaryView

app_name = 'orderapp'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('create/', CreateView.as_view(), name='create'),
    path('summary/', SummaryView.as_view(), name='summary'),
]