from .permissions import IsTeacherOrReadOnly
from .models import CustomUser
from .services import get_google_access_token, get_google_user_info
from .serializers import GoogleAuthSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView

class UserRoleView(APIView):
    permission_classes = [IsTeacherOrReadOnly]

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            return Response({'role': user.role})
        else:
            return Response({'error': 'Пользователь не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        user = request.user
        if user.is_authenticated:
            new_role = request.data.get('role')
            if new_role in [CustomUser.Role.STUDENT, CustomUser.Role.TEACHER]:
                user.role = new_role
                user.save()
                return Response({'message': 'Роль успешно обновлена', 'new_role': user.role})
            else:
                return Response({'error': 'Недопустимая роль'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Пользователь не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        
        google_token = get_google_access_token(code)
        
        user_info = get_google_user_info(google_token)
        email = user_info.get('email')
        
        if not email:
            return Response(
                {"error": "Google не предоставил email пользователя."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user = CustomUser.objects.filter(email=email).first()
        created = False

        if not user:
            user = CustomUser.objects.create_user(
                email=email,
                username=user_info.get('name', ''),
                role=CustomUser.Role.STUDENT,
                is_active=True
            )
            user.set_unusable_password()
            user.save()
            created = True

        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['role'] = user.role

        return Response({
            "message": "Успешная авторизация через Google",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "is_new_user": created,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
            },
        }, status=status.HTTP_200_OK)