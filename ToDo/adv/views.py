from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from .filters import AdvertisementFilter
from .models import Advertisement, AdvertisementStatusChoices, \
    FavoriteAdvertisement
from .serializers import AdvertisementSerializer


class AdvertisementViewSet(ModelViewSet):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertisementFilter

    # --- фильтрация видимых объявлений ---
    def get_queryset(self):
        user = self.request.user
        qs = Advertisement.objects.all()

        if user.is_authenticated:
            if user.is_staff:
                # админ видит все объявления
                return qs
            # обычный пользователь видит: не-DRAFT + свои DRAFT
            return qs.filter(
                Q(status__in=[AdvertisementStatusChoices.OPEN,
                              AdvertisementStatusChoices.CLOSED])
                | Q(status=AdvertisementStatusChoices.DRAFT, creator=user)
            )
        # анонимный пользователь видит только OPEN/CLOSED
        return qs.filter(status__in=[AdvertisementStatusChoices.OPEN,
                                     AdvertisementStatusChoices.CLOSED])

    # --- проверка прав ---
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return []

    # --- удаление с проверкой прав ---
    def destroy(self, request, *args, **kwargs):
        ad = self.get_object()
        user = request.user
        if not user.is_staff and ad.creator != user:
            return Response(
                {"detail": "Нельзя удалить чужое объявление"},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(ad)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # --- обновление с проверкой прав ---
    def update(self, request, *args, **kwargs):
        ad = self.get_object()
        user = request.user
        if not user.is_staff and ad.creator != user:
            return Response(
                {"detail": "Нельзя изменить чужое объявление"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    # --- добавить в избранное ---
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        ad = self.get_object()
        user = request.user

        if ad.creator == user:
            return Response(
                {"detail": "Нельзя добавить своё объявление в избранное"},
                status=400)

        fav, created = FavoriteAdvertisement.objects.get_or_create(user=user,
                                                                   advertisement=ad)
        if not created:
            return Response({"detail": "Уже в избранном"}, status=400)
        return Response({"detail": "Добавлено в избранное"})

    # --- просмотр своих избранных объявлений ---
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def favorites(self, request):
        user = request.user
        fav_ads = Advertisement.objects.filter(favoriteadvertisement__user=user)
        serializer = self.get_serializer(fav_ads, many=True)
        return Response(serializer.data)
