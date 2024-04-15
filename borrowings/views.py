
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer
)


class GetBorrowingView(APIView):
    """ APIVIEW for list and detail endpoint for Borrowing """

    serializer_class = BorrowingReadSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, format=None):
        if pk:
            borrowings = get_object_or_404(Borrowing, pk=pk)
            serializer = BorrowingReadSerializer(borrowings)
        else:
            borrowings = Borrowing.objects.all()
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
