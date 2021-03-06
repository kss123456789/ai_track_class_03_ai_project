from rest_framework.response import Response

from .models import PlayList
from .models import Rating
from .models import VideoData
from .models import User
from .models import SearchLog

from rest_framework.views import APIView
from django.http import Http404
from rest_framework import generics
from rest_framework import status
from rest_framework import permissions

from .serializers import PlayListSerializer
from .serializers import PlayListDetailSerializer
from .serializers import VideoDataPostSerializer
from .serializers import VideoDataResponseSerializer
from .serializers import SearchLogSerializer
from .serializers import SearchLogDetailSerializer
from .serializers import UserSerializer
from .serializers import PlayListPostSerializer
from .serializers import RatingPostSerializer
from .exceptions import AlreadyRatedVideo
from .exceptions import AlreadyVideoInPlaylist

from drf_yasg.utils import swagger_auto_schema

from asgiref.sync import sync_to_async
import asyncio as aio

class AsyncMixin:
    """Provides async view compatible support for DRF Views and ViewSets.

    This must be the first inherited class.

        class MyViewSet(AsyncMixin, GenericViewSet):
            pass
    """
    @classmethod
    def as_view(cls, *args, **initkwargs):
        """Make Django process the view as an async view.
        """
        view = super().as_view(*args, **initkwargs)

        async def async_view(*args, **kwargs):
            # wait for the `dispatch` method
            return await view(*args, **kwargs)
        async_view.csrf_exempt = True
        return async_view

    async def dispatch(self, request, *args, **kwargs):
        """Add async support.
        """
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers

        try:
            await sync_to_async(self.initial)(
                request, *args, **kwargs)  # MODIFIED HERE

            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(),
                                self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            # accept both async and sync handlers
            # built-in handlers are sync handlers
            if not aio.iscoroutinefunction(handler):  # MODIFIED HERE
                handler = sync_to_async(handler)  # MODIFIED HERE
            response = await handler(request, *args, **kwargs)  # MODIFIED HERE

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(
            request, response, *args, **kwargs)
        return self.response


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# ???????????? ??? ??????
class PlayLists(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_user(self):
        return self.request.user

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: PlayListDetailSerializer,
            status.HTTP_400_BAD_REQUEST: "????????? ??????",
        }
    )
    def get(self, request):
        """
        ??????????????????(????????????) ?????? *token ??????
        ???????????? ????????? ???????????? ????????? ??????. 
        """
        self.user = self.get_user()
        playlist = PlayList.objects.filter(user_id=self.user.id)
        serializer = PlayListDetailSerializer(playlist, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=PlayListPostSerializer,
        responses={
            status.HTTP_200_OK: PlayListSerializer,
            status.HTTP_400_BAD_REQUEST: "????????? ??????",
        }
    )
    def post(self, request, format=None):
        """

        ??????????????????(????????????) ?????? *token ??????
        ??????????????????(????????????)??? ????????? ??????.
        """
        self.user = self.get_user()

        serializer = PlayListPostSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # checkExistVideoInPlayList
        if PlayList.objects.filter(
            user_id=self.user.id, list_name=serializer.validated_data["list_name"],
            video_data_id=serializer.validated_data["video_data_id"]
            ).exists():
            raise AlreadyVideoInPlaylist

        serializer.save()
        return Response(PlayListSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)


class PlayListDetail(APIView):
    def get_object(self, pk):
        try:
            return PlayList.objects.get(pk=pk)
        except PlayList.DoesNotExist:
            return Http404

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: PlayListSerializer,
            status.HTTP_400_BAD_REQUEST: "????????? ??????",
        }
    )
    def delete(self, request, pk, format=None):
        '''
        ????????????????????? ????????? ??????

        playlist?????? ????????? ??????
        '''
        playlist = self.get_object(pk)
        playlist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VideoDataList(AsyncMixin, APIView):
    @swagger_auto_schema(
        request_body=VideoDataPostSerializer,
        responses={
            status.HTTP_200_OK: VideoDataResponseSerializer,
            status.HTTP_400_BAD_REQUEST: "????????? ??????",
        },
    )
    def post(self, request, format=None):
        """
        ????????? ??????(????????? ??????) *token ??????(???????????? ???????????? ??????)

        ????????? ????????? ????????? DB??? ??????
        """
        try:
            request_url = request.data['url']
        except KeyError as e:
            return Response({'KeyError': f'?????????{e}??????'}, status=status.HTTP_400_BAD_REQUEST)
            
        # checkExistVideoData
        print('??????url : ', request_url)
        video = VideoData.objects.filter(url=request_url)
        if len(video) > 0:
            print(video[0].url)

            # ????????? ??????
            if request.user.is_authenticated:
                # save searchlog
                searchlog_input = {"user_id": request.user.id, "video_data_id": video[0].id}
                serializer_searchlog = SearchLogSerializer(data=searchlog_input)
                if serializer_searchlog.is_valid(raise_exception=True):
                    serializer_searchlog.save()
                    
            return Response(
                VideoDataResponseSerializer(video[0]).data,
                status=status.HTTP_201_CREATED,
            )

        serializer_videodata = VideoDataPostSerializer(
            data=request.data, context={"request": request}
        )

        if serializer_videodata.is_valid(raise_exception=True):
            serializer_videodata.save()
            video_data = serializer_videodata.instance

            # ????????? ??????
            if request.user.is_authenticated:
                # save searchlog
                searchlog_input = {"user_id": request.user.id, "video_data_id": video_data.id}
                serializer_searchlog = SearchLogSerializer(data=searchlog_input)
                if serializer_searchlog.is_valid(raise_exception=True):
                    serializer_searchlog.save()

            return Response(
                VideoDataResponseSerializer(video_data).data,
                status=status.HTTP_201_CREATED,
            )
        

        return Response(serializer_videodata.errors, status=status.HTTP_404_NOT_FOUND)


class VideoDataDetail(APIView):
    def get_object(self, pk):
        try:
            return VideoData.objects.get(pk=pk)
        except VideoData.DoesNotExist:
            return Http404

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: VideoDataResponseSerializer,
            status.HTTP_400_BAD_REQUEST: "????????? ??????",
        },
    )
    def get(self, request, pk, format=None):
        '''
        ????????? ????????? ?????? ????????????

        ?????? video_id??? video?????? ????????????
        '''
        videodata = self.get_object(pk)
        serializer = VideoDataResponseSerializer(videodata)
        return Response(serializer.data)


class SearchLogList(APIView):

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: SearchLogDetailSerializer,
            status.HTTP_400_BAD_REQUEST: "????????? ??????",
        }
    )
    def get(self, request, format=None):
        '''
        ?????? ????????????(?????? ?????????)

        ?????? ???????????? ?????? ???????????? 10???
        '''
        try:
            searchlog = SearchLog.objects.all()[:10]
        except SearchLog.DoesNotExist:
            searchlog = None
        serializer = SearchLogDetailSerializer(searchlog, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SearchLogUserList(APIView):

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: SearchLogDetailSerializer,
            status.HTTP_400_BAD_REQUEST: "????????? ??????",
        }
    )
    def get(self, request, format=None):
        '''
        ?????? ????????????(????????? ??????) *token ??????

        ?????? ?????? ???????????? ????????????
        '''
        try:
            searchlog = SearchLog.objects.filter(user_id=request.user.id)
        except SearchLog.DoesNotExist:
            searchlog = None
        serializer = SearchLogDetailSerializer(searchlog, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RatingDetail(APIView):
    @swagger_auto_schema(
        request_body=RatingPostSerializer,
        responses={
            status.HTTP_200_OK: RatingPostSerializer,
            status.HTTP_400_BAD_REQUEST: "????????? ??????",
        }
    )
    def post(self, request, format=None):
        """
        ???????????? ?????? ?????? ?????? *token ??????

        ???????????? ?????? ?????? ??????
        """

        serializer = RatingPostSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # checkExistRating
        if Rating.objects.filter(
            user_id=request.user, rating=serializer.validated_data["rating"],
            video_data_id=serializer.validated_data["video_data_id"]
            ).exists():
            raise AlreadyRatedVideo

        serializer.save()
        return Response(RatingPostSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)