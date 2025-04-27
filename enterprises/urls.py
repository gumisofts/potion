from rest_framework.routers import DefaultRouter, SimpleRouter

router = DefaultRouter()
from .views import *

# router.register(
#     r"enterprises",
#     EnterpriseViewset,
#     basename="enterprises",
# )
# router.register(
#     r"enterprise-users",
#     EnterpriseUserViewset,
#     basename="enterprise-users",
# )

router.register(r"users/grants", UserGrantViewset, basename="user-grants")
urlpatterns = router.urls
