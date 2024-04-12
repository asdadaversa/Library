from rest_framework import routers

from books.views import BookViewSet

router = routers.DefaultRouter()
router.register("", BookViewSet, basename="books")


urlpatterns = router.urls


app_name = "books"
