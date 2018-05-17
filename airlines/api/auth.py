from rest_framework import views
from rest_framework.response import Response
from rest_framework import routers, serializers, viewsets
from django.contrib.auth.models import User
  
class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = [ 'username', 'email' ]

  
class AuthViewSet(viewsets.ViewSet):
   def get_queryset(self):
      return User.objects.all()

   def list(self, request):
      print('filter user by:')
      print(request.user.username)
      queryset = User.objects.all().filter(username=request.user.username)
      serializer = UserSerializer(queryset, many=True)
      return Response(serializer.data)
      
   def retrieve(self, request, pk=None):
      queryset = User.objects.all()
      user = get_object_or_404(queryset, pk=pk)
      serializer = UserSerializer(user)
      return Response(serializer.data)