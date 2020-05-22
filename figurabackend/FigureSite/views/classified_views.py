
from dry_rest_permissions.generics import DRYPermissions
from rest_framework_serializer_extensions.utils import external_id_from_model_and_internal_id
from rest_framework_serializer_extensions.views import ExternalIdViewMixin
from rest_framework import mixins
from FigureSite import serializers
from rest_framework import viewsets
from FigureSite.models import ClassifiedAD, PrivateMessage, User, ClassifiedReview, ClassifiedCategory
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_haystack.serializers import HaystackSerializer
from drf_haystack.viewsets import HaystackViewSet
from rest_framework import permissions
from FigureSite.search_indexes import ClassifiedIndex
class ClassifiedADPagination(PageNumberPagination):
    page_size = 4
    max_page_size = 20
    page_size_query_param = 'page_size'

class ClassifiedCategoryViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  queryset = ClassifiedCategory.objects.all()
  permission_classes = (DRYPermissions,)
  serializer_class = serializers.ClassifiedCategorySerializer
class ClassifiedADViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  queryset = ClassifiedAD.objects.all()
  permission_classes = (DRYPermissions,)
  serializer_class = serializers.ClassifiedADSerializer
  pagination_class=ClassifiedADPagination
  lookup_field = 'slug'
  def filter_queryset(self, queryset):
    queryset = super(ClassifiedADViewSet, self).filter_queryset(queryset)
    return queryset.order_by('-created')
  @action(detail=False, methods=['post'])
  def create_ad(self, request):
    request.data['creator'] = request.user.id
    serializer = serializers.CreateClassifiedADSerializer(data=request.data)
    if serializer.is_valid():
      ad = serializer.save()
      for i in range(int(request.data['image_count'])):
        image_request_data = {
          'ad': ad.id,
          'image': request.data['image' + str(i)],
          'primary': i == 0
        }
        image_serializer = serializers.CreateclassifiedImageSerializer(data=image_request_data)
        if not image_serializer.is_valid():
          return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
          image_serializer.save()
        ad.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  @action(methods=['post'], detail=True)
  def sell_to_user(self, request, slug):
    ad = self.get_object()
    receiving_user = User.objects.get(username=request.data['username'])
    ad.sold_to = receiving_user
    ad.sold = True
    ad.save()
    
    message = PrivateMessage(creator=request.user, receiver=receiving_user, subject='Deja tu opinión sobre {}'.format(ad.title), content="Pincha en el anuncio y deja tu opinión sobre la compra!", related_ad=ad)
    message.save()

    return Response({}, status=status.HTTP_201_CREATED)
  @action(methods=['post'], detail=True)
  def send_review(self, request, slug):
    ad = self.get_object()
    if ad.reviewed:
      return Response({'error': 'Este anuncio ya tiene una reseña'}, status=status.HTTP_400_BAD_REQUEST)
    if request.user == ad.sold_to:
      if 'content' in request.data and 'recommended' in request.data:
        content = request.data['content']
        recommended = request.data['recommended']
        if content != '':
          review = ClassifiedReview.objects.create(creator=request.user, recommended=recommended, content=content, for_user=ad.creator, related_ad=ad)
          review.save()
          ad.reviewed = True
          ad.save()
          ad.creator.save()
          return Response({}, status=status.HTTP_201_CREATED)
      return Response({}, status=status.HTTP_400_BAD_REQUEST)
    else:
      return Response({'error': 'No has comprado este producto'}, status=status.HTTP_403_FORBIDDEN)
class ClassifiedsSearchSerializer(HaystackSerializer):
  class Meta:
    # The `index_classes` attribute is a list of which search indexes
    # we want to include in the search.
    index_classes = [ClassifiedIndex]

    # The `fields` contains all the fields we want to include.
    # NOTE: Make sure you don't confuse these with model attributes. These
    # fields belong to the search index!
    fields = [ "text", "username", "image", "created", "slug", "price", "price_currency", "sold", "category" ]
class ClassifiedADSearchView(HaystackViewSet):
  index_models = [ClassifiedAD]
  # `index_models` is an optional list of which models you would like to include
  # in the search result. You might have several models indexed, and this provides
  # a way to filter out those of no interest for this particular view.
  # (Translates to `SearchQuerySet().models(*index_models)` behind the scenes.
  pagination_class = ClassifiedADPagination
  serializer_class = ClassifiedsSearchSerializer
  permission_classes = [permissions.IsAuthenticatedOrReadOnly]
  def finalize_response(self, request, response, *args, **kwargs):
    response = super(ClassifiedADSearchView, self).finalize_response(request, response, *args, **kwargs)
    print(response.data['results'])
    for i, user in enumerate(response.data['results']):
      response.data['results'][i]['image'] = request.build_absolute_uri(response.data['results'][i]['image'])
    return response
  def filter_queryset(self, queryset):
    queryset = super(ClassifiedADSearchView, self).filter_queryset(queryset)
    return queryset.order_by('-created')