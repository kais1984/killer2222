"""
Authentication URLs and views
"""

from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from core.models import User

class LoginView(APIView):
    """User login endpoint"""
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """User logout endpoint"""
    
    def post(self, request):
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'})


class ProfileView(APIView):
    """Get current user profile"""
    
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': getattr(user, 'phone', ''),
        })


class RegisterView(APIView):
    """User registration (admin only)"""
    
    def post(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.create_user(
                username=request.data.get('username'),
                email=request.data.get('email'),
                password=request.data.get('password'),
                first_name=request.data.get('first_name', ''),
                last_name=request.data.get('last_name', ''),
                role=request.data.get('role', 'sales'),
            )
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'User created successfully',
                'user_id': user.id,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
]
