from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import action

from drf_haystack.serializers import HaystackSerializer
from drf_haystack.viewsets import HaystackViewSet

from dry_rest_permissions.generics import DRYPermissions

from FigureSite.search_indexes import UserIndex
from FigureSite.models import User
from FigureSite import serializers


# Paginations

class UserPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 20
    page_size_query_param = 'page_size'

class UserPostPagination(PageNumberPagination):
    page_size = 10

# Haystack stuff

class UserSearchSerializer(HaystackSerializer):
    class Meta:
        # The `index_classes` attribute is a list of which search indexes
        # we want to include in the search.
        index_classes = [UserIndex]

        # The `fields` contains all the fields we want to include.
        # NOTE: Make sure you don't confuse these with model attributes. These
        # fields belong to the search index!
        fields = [ "avatar", "text", "date_joined", "post_count", "is_staff" ]

class UserSearchView(HaystackViewSet):
    index_models = [User]
    # `index_models` is an optional list of which models you would like to include
    # in the search result. You might have several models indexed, and this provides
    # a way to filter out those of no interest for this particular view.
    # (Translates to `SearchQuerySet().models(*index_models)` behind the scenes.
    pagination_class = UserPagination
    serializer_class = UserSearchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def finalize_response(self, request, response, *args, **kwargs):
      response = super(UserSearchView, self).finalize_response(request, response, *args, **kwargs)
      print(response.data)
      for i, user in enumerate(response.data['results']):
        response.data['results'][i]['avatar'] = request.build_absolute_uri(response.data['results'][i]['avatar'])
      return response

# API Views

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  permission_classes = (DRYPermissions,)
  lookup_field = 'username'

  def retrieve(self, request, username=None):
    return super(UserViewSet, self).retrieve(request, username)
  def get_serializer_class(self):
    if self.action == 'partial_update':
      return serializers.UpdateUserSerializer
    if self.request.user.is_staff or self.kwargs.get('pk') == 'current':
      return serializers.FullUserSerializer

    return serializers.PublicUserSerializer

  @action(methods=['post'], detail=True)
  def ban_user(self, request, username=None):
    user = self.get_object()
    if request.data['post']:
      post = Post.objects.get(pk=internal_id_from_model_and_external_id(Post, request.data['post']))
      ban_reason = BanReason(post=post, ban_reason=request.data['ban_reason'], banner=request.user, banned_user=post.creator, ban_expiry_date=request.data['ban_expiry_date'])
      ban_reason.save()
      return Response(serializers.BanReasonSerializer(ban_reason).data, status=status.HTTP_200_OK)
    return Response({}, status=status.HTTP_400_BAD_REQUEST)

  @action(methods=['post'], detail=True)
  def send_message(self, request, username=None):
    user = self.get_object()
    request.data['creator'] = request.user.id
    request.data['receiver'] = user.id
    serializer = serializers.CreatePrivateMessageSerializer(data=request.data)
    if serializer.is_valid():
      message = serializer.save()
      return Response(serializers.PrivateMessageSerializer(message, context={'request': request}).data, status=status.HTTP_200_OK)
    else: 
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def get_object(self):
    pk = self.kwargs.get('username')
    if pk == "current":
      return self.request.user

    return super(UserViewSet, self).get_object()

  @action(methods=['get'], pagination_class=UserPostPagination, detail=True)
  def posts(self, request, username=None):
    user = self.get_object()
    page = self.paginate_queryset(user.posts.all().order_by('created'))
    if page is not None:
      serializer = serializers.PostSerializer(page, many=True, context={'request': request})
      return self.get_paginated_response(serializer.data)
    else:
      posts = serializers.PostSerializer(user.posts, many=True, context={'request': request})
    return Response(posts.data)

  @action(methods=['get'], pagination_class=UserPostPagination, detail=True)
  def threads(self, request, username=None):
    user = self.get_object()
    page = self.paginate_queryset(user.threads.all().order_by('-created'))
    if page is not None:
      serializer = serializers.ThreadSerializer(page, many=True, context={'request': request})
      return self.get_paginated_response(serializer.data)
    else:
      threads = serializers.ThreadSerializer(user.threads.all().order_by('-created'), many=True, context={'request': request})
    return Response(threads.data)