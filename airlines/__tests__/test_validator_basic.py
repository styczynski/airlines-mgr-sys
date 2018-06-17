from tests import *


class TestValidatorBasic(unittest.TestCase):

    # @transaction.atomic

    def test_user_empty_name(self):
        models = getModels()
        expectSimpleSaveToFail(models.User, name='', surname='asdasd')

    def test_user_empty_surname(self):
        models = getModels()
        expectSimpleSaveToFail(models.User, name='asdasd', surname='')

    def test_user_empty_name_and_surname(self):
        models = getModels()
        expectSimpleSaveToFail(models.User, name='', surname='')

    def test_user_ok(self):
        models = getModels()
        expectSimpleSaveToSucceed(models.Worker, name='Michał', surname='Jędżejewski')

    def test_worker_empty_name(self):
        models = getModels()
        expectSimpleSaveToFail(models.Worker, name='', surname='asdasd')

    def test_worker_empty_surname(self):
        models = getModels()
        expectSimpleSaveToFail(models.Worker, name='asdasd', surname='')

    def test_worker_empty_name_and_surname(self):
        models = getModels()
        expectSimpleSaveToFail(models.Worker, name='', surname='')

    def test_worker_ok(self):
        models = getModels()
        expectSimpleSaveToSucceed(models.Worker, name='Jan', surname='Kowalski')

    def test_plane_too_low_seats_count(self):
        models = getModels()
        expectSimpleSaveToFail(models.Plane, reg_id='ACBX1302', seats_count=2, service_start='1992-10-11')

    def test_plane_no_reg(self):
        models = getModels()
        expectSimpleSaveToFail(models.Plane, seats_count=250, service_start='1992-10-11')

    def test_plane_ok(self):
        models = getModels()
        expectSimpleSaveToSucceed(models.Plane, reg_id='K313LCBA', seats_count=250, service_start='1992-10-11')