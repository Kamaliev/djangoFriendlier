from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt import authentication

# Создаем объект Schema View
schema_view = get_schema_view(
    openapi.Info(
        title='Friendler',
        default_version='v1',
        description='My API description',
        terms_of_service='http://kamaliev.asuscomm.com/vk/redoc',
        contact=openapi.Contact(email='KamaIiev@yandex.ru')
    ),
    public=True,
    permission_classes=[AllowAny],

)
