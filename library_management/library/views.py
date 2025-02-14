from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import User, Book, Loan
from .serializers import BookSerializer, LoanSerializer, UserSerializer

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_admin

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filterset_fields = ['title', 'author', 'isbn']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def get_permissions(self):
        if self.action in ['list', 'update', 'partial_update', 'destroy', 'return_book']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request):
        book = Book.objects.get(pk=request.data['book'])

        if book.available_quantity <= 0:
            return Response(
                {'error': 'Book is not available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        loan = Loan.objects.create(
            user=request.user,
            book=book,
            borrowed_date=timezone.now()
        )
        book.available_quantity -= 1
        book.save()

        return Response(
            LoanSerializer(loan).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def return_book(self):
        loan = self.get_object()
        if loan.is_returned:
            return Response(
                {'error': 'Book already returned'},
                status=status.HTTP_400_BAD_REQUEST
            )

        loan.is_returned = True
        loan.return_date = timezone.now()
        loan.save()

        book = loan.book
        book.available_quantity += 1
        book.save()

        return Response(
            LoanSerializer(loan).data,
            status=status.HTTP_200_OK
        )