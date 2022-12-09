from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers

from .views import CommentViewSet, FollowViewSet, GroupViewSet, PostViewSet

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register(r'groups', GroupViewSet, basename='groups')
router_v1.register(r'posts', PostViewSet, basename='posts')
router_v1.register(
    r'posts/(?P<post_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router_v1.register(r'follow', FollowViewSet, basename='follow')

urlpatterns = [
    path(r'v1/', include(router_v1.urls)),
    path(r'v1/', include('djoser.urls.jwt')),
    path(
        r'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    )
]
