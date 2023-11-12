from django.urls import include, path
from .views import StoreReport

urlpatterns = [
    path('trigger_report', StoreReport.as_view(), name='trigger report'),
    path('get_report', StoreReport.as_view(), name='get report'),
]
