from ..models import Worker, Crew, Flight, Plane
from rest_framework import routers, serializers, viewsets

from .workers import WorkerSerializer

class CrewSerializer(serializers.ModelSerializer):

  worker_set = WorkerSerializer(many=True)

  class Meta:
    model = Crew
    fields = [ 'id', 'crew_id', 'flight_set', 'worker_set' ]

class CrewList(viewsets.ModelViewSet):
  serializer_class = CrewSerializer
  
  def get_queryset(self):
      crew_id = None
      if 'crew_id' in self.kwargs:
        crew_id = self.kwargs['crew_id']
      
      crews = Crew.objects.all()
      if crew_id:
        crews = crews.filter(crew_id__contains=crew_id)
        
      return crews
