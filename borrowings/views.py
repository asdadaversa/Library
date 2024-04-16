from rest_framework import status, mixins, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer
)


class ListCreateBorrowingView(APIView, mixins.ListModelMixin):
    serializer_class = BorrowingReadSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        is_active = request.query_params.get("is_active")

        if request.user.is_staff:
            borrowings = Borrowing.objects.all()
        else:
            borrowings = Borrowing.objects.filter(user=self.request.user)

        if is_active:
            borrowings = Borrowing.objects.filter(actual_return_date__isnull=True)

        serializer = BorrowingReadSerializer(borrowings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = BorrowingCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetailBorrowingView(APIView):
    """ APIVIEW for list and detail endpoint for Borrowing """

    serializer_class = BorrowingReadSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        borrowings = get_object_or_404(Borrowing, pk=pk)
        serializer = BorrowingReadSerializer(borrowings)
        return Response(serializer.data, status=status.HTTP_200_OK)
