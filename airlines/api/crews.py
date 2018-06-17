from ..models import Worker, Crew, Flight, Plane
from rest_framework import routers, serializers, viewsets
from django.db.models import Count, CharField, Value as V
from django.db.models.functions import Concat

from .workers import WorkerSerializer


class CrewSerializer(serializers.ModelSerializer):
    worker_set = WorkerSerializer(many=True)
    capitain = WorkerSerializer(many=False)
    crew_name = serializers.SerializerMethodField()

    def get_crew_name(self, obj):
        return obj.capitain.getFullName()

    class Meta:
        model = Crew
        fields = ['id', 'crew_name', 'capitain', 'flight_set', 'worker_set']


class CrewList(viewsets.ModelViewSet):
    serializer_class = CrewSerializer

    def get_queryset(self):
        crew_name = None
        if 'crew_name' in self.kwargs:
            crew_name = self.kwargs['crew_name']

        crews = Crew.objects.all()
        crews = crews.annotate(
            crew_name=Concat('capitain__name', V(' '), 'capitain__surname', output_field=CharField())
        )

        if crew_name:
            crews = crews.filter(crew_name__contains=crew_name)

        return crews
