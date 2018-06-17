from tests import *


class TestValidatorBasic(unittest.TestCase):

    # @transaction.atomic

    def test_user_empty_name(self):
        models = getModels()
        expectSimpleSaveToFail(models.User, name='', surname='asdASDSADAasd')

    def test_user_empty_surname(self):
        models = getModels()
        expectSimpleSaveToFail(models.User, name='asdaASDSDsd', surname='')

    def test_user_empty_name_and_surname(self):
        models = getModels()
        expectSimpleSaveToFail(models.User, name='', surname='')

    def test_user_ok(self):
        models = getModels()
        expectSimpleSaveToSucceed(models.Worker, name='MichałASDASD', surname='JędżejewskiASDDW')

    def test_worker_empty_name(self):
        models = getModels()
        expectSimpleSaveToFail(models.Worker, name='', surname='asdSSSDasd')

    def test_worker_empty_surname(self):
        models = getModels()
        expectSimpleSaveToFail(models.Worker, name='asdasASDSDAd', surname='')

    def test_worker_empty_name_and_surname(self):
        models = getModels()
        expectSimpleSaveToFail(models.Worker, name='', surname='')

    def test_worker_ok(self):
        models = getModels()
        expectSimpleSaveToSucceed(models.Worker, name='JanAXXXZZZ32', surname='KowalskiZZZ888737UJ')

    def test_plane_too_low_seats_count(self):
        models = getModels()
        expectSimpleSaveToFail(models.Plane, reg_id='ACBX13022222222', seats_count=2, service_start='1992-10-11')

    def test_plane_no_reg(self):
        models = getModels()
        expectSimpleSaveToFail(models.Plane, seats_count=250, service_start='1992-10-11')

    def test_plane_ok(self):
        models = getModels()
        expectSimpleSaveToSucceed(models.Plane, reg_id='K313LCBA1111111', seats_count=250, service_start='1992-10-11')