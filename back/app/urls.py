from django.urls import path, include
from .views import PlayLists, PlayListDetail, VideoDataList, VideoDataDetail
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path("playlist/", PlayLists.as_view(), name="playlist_list"),
    path("playlist/<int:pk>/", PlayListDetail.as_view(), name="playlist_detail"),
    path("videodata/", VideoDataList.as_view(), name="videodata_lilst"),
    path("videodata/<str:pk>/", VideoDataDetail.as_view(), name="videodata_detail"),
    # path('signup/', views.UserCreate.as_view()),
    # path('auth/', include('rest_framework.urls')),
]

urlpatterns = format_suffix_patterns(urlpatterns)
