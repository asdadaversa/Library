
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer


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
