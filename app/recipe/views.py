

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base viewset for user owned recipe attributes"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewset(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewset(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Return recipe objects for the current authenticated user"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tags_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tags_ids)
        # '__' is the django syntax for filtering on foreign key objects
        # There is a 'tags' field in the 'Recipe' queryset which is a
        # foreign key to the 'Tags' table where the tag ids are found
        # Hence, search the tags table for ids that are in the list provided
        if ingredients:
            ingredients_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        # This is all thats needed to create an object, built in function of
        # the ModelViewSet class
        # Default functionality: pass in a serializer class that is assigned
        # to a model, the MVS knows how to create new objects with
        # the model when using an HTTP post
        # Just assign an authenticated user to the model for it to work
        serializer.save(user=self.request.user)

# 'actions' aredefined as functions in the viewset
# 'detail' defines that the 'action' will be for a specific recipe, hence
# images will only be uploaded to objects that already exist
# The ID of the object will need to be included in the url
# 'url-path' is the path name for the url ---> '/recipe/<id>/upload-image/'
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        # retrieves and assigns the object that is being accessed by the id
        recipe = self.get_object()
# Pass in the object and request data to the serializer for validation
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )
# Validates that only the required fields are present and correct
        if serializer.is_valid():
            # since a ModelSerializer is used we can use the 'save()'
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
