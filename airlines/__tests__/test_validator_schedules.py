from tests import *


def dbCleanup(models):
    with transaction.atomic():
        models.Flight.objects.all().delete()
        models.Worker.objects.all().delete()
        models.Crew.objects.all().delete()
        models.Plane.objects.all().delete()


class TestValidatorSchedules(unittest.TestCase):

    def test_flights_with_same_time_plane_and_crew(self):
        models = getModels()
        dbCleanup(models)

        with transaction.atomic():
            planeA = createTestPlane(models, 'PlaneA', 250)
            crewA = createTestCrew(models, 'CrewA', 10)

        try:
            with transaction.atomic():
                flightA = models.Flight(
                    src='Source',
                    dest='Destination',
                    start=createTime(hour=12),
                    end=createTime(hour=20),
                    plane=planeA,
                    crew=crewA
                )
                flightA.save()

            with transaction.atomic():
                flightB = models.Flight(
                    src='Source',
                    dest='Destination',
                    start=createTime(hour=12),
                    end=createTime(hour=20),
                    plane=planeA,
                    crew=crewA
                )
                flightB.save()

        except ValidationError:
            return True

        # Should throw
        assert False

    def test_flights_with_conflicting_time_for_crew(self):
        models = getModels()
        dbCleanup(models)

        with transaction.atomic():
            planeA = createTestPlane(models, 'PlaneA', 250)
            planeB = createTestPlane(models, 'PlaneB', 250)
            crewA = createTestCrew(models, 'CrewA', 10)

        try:
            with transaction.atomic():
                flightA = models.Flight(
                    src='Source',
                    dest='Destination',
                    start=createTime(hour=12),
                    end=createTime(hour=20),
                    plane=planeA,
                    crew=crewA
                )
                flightA.save()

            with transaction.atomic():
                flightB = models.Flight(
                    src='Source',
                    dest='Destination',
                    start=createTime(hour=18),
                    end=createTime(hour=21),
                    plane=planeB,
                    crew=crewA
                )
                flightB.save()

        except ValidationError:
            return True

        # Should throw
        assert False

    def test_flights_with_conflicting_time_for_plane(self):
        models = getModels()
        dbCleanup(models)

        with transaction.atomic():
            planeA = createTestPlane(models, 'PlaneA', 250)
            crewA = createTestCrew(models, 'CrewA', 10)
            crewB = createTestCrew(models, 'CrewB', 18)

        try:
            with transaction.atomic():
                flightA = models.Flight(
                    src='Source',
                    dest='Destination',
                    start=createTime(hour=12),
                    end=createTime(hour=20),
                    plane=planeA,
                    crew=crewA
                )
                flightA.save()

            with transaction.atomic():
                flightB = models.Flight(
                    src='Source',
                    dest='Destination',
                    start=createTime(hour=18),
                    end=createTime(hour=21),
                    plane=planeA,
                    crew=crewB
                )
                flightB.save()

        except ValidationError:
            return True

        # Should throw
        assert False

    def test_flight_without_crew(self):
        models = getModels()
        dbCleanup(models)

        with transaction.atomic():
            planeA = createTestPlane(models, 'PlaneA', 250)

        try:
            with transaction.atomic():
                flightA = models.Flight(
                    src='Source',
                    dest='Destination',
                    start=createTime(hour=12),
                    end=createTime(hour=20),
                    plane=planeA
                )
                flightA.save()

        except ValidationError:
            return True

        # Should throw
        assert False

    def test_flight_with_time_shorter_than_30_mins(self):
        models = getModels()
        dbCleanup(models)

        with transaction.atomic():
            planeA = createTestPlane(models, 'PlaneA', 250)
            crewA = createTestCrew(models, 'CrewA', 10)

        try:
            with transaction.atomic():
                flightA = models.Flight(
                    src='Source',
                    dest='Destination',
                    start=createTime(hour=12),
                    end=createTime(hour=12, minute=29),
                    plane=planeA,
                    crew=crewA
                )
                flightA.save()

        except ValidationError:
            return True

        # Should throw
        assert False

    def test_flight_ok(self):
        models = getModels()
        dbCleanup(models)

        with transaction.atomic():
            planeA = createTestPlane(models, 'PlaneA', 250)
            crewA = createTestCrew(models, 'CrewA', 10)

        try:
            with transaction.atomic():
                flightA = models.Flight(
                    src='Source',
                    dest='Destination',
                    start=createTime(hour=12, minute=0),
                    end=createTime(hour=12, minute=34),
                    plane=planeA,
                    crew=crewA
                )
                flightA.save()

        except ValidationError:
            # Should not throw
            assert False
