from ..models import Worker, Crew, Flight, Plane
from rest_framework import routers, serializers, viewsets


class WorkerSerializer(serializers.ModelSerializer):
  crew = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

  class Meta:
    model = Worker
    fields = [ 'name', 'surname', 'crew' ]

class WorkerViewSet(viewsets.ModelViewSet):
  queryset = Worker.objects.all()
  serializer_class = WorkerSerializer
  