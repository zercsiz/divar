from django.urls import path, include
from rest_framework.routers import DefaultRouter
from entry import views

router = DefaultRouter()
router.register('entries', views.EntryViewSet)

app_name = 'entry'

urlpatterns = [
    path('', include(router.urls)),
    path('category-list/',
         views.CategoryListView.as_view(),
         name='category-list')
]
