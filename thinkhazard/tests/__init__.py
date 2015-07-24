import unittest
import os
import ConfigParser
import transaction

from paste.deploy import loadapp

from ..models import (
    Base,
    DBSession,
    AdministrativeDivision,
    HazardCategory,
    HazardType,
    CategoryType,
    IntensityThreshold,
    TermStatus,
    AdditionalInformation,
    AdditionalInformationType,
    HazardCategoryAdditionalInformationAssociation,
    )

from shapely.geometry import (
    MultiPolygon,
    Polygon,
    )
from geoalchemy2.shape import from_shape

local_settings_path = 'local.tests.ini'

# raise an error if the file doesn't exist
with open(local_settings_path):
    pass

def populate_db():
    config = ConfigParser.ConfigParser()
    config.read(local_settings_path)
    db_url = config.get('app:main', 'sqlalchemy.url')

    from sqlalchemy import create_engine
    engine = create_engine(db_url)

    from ..scripts.initializedb import populate_db as populate
    populate(engine)

    with transaction.manager:

        shape = MultiPolygon([
            Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
        ])
        geometry = from_shape(shape, 3857)

        div_level_1 = AdministrativeDivision(**{
            'code': 10,
            'leveltype_id': 1,
            'name': u'Division level 1'
        })
        div_level_1.geom = geometry
        DBSession.add(div_level_1)

        div_level_2 = AdministrativeDivision(**{
            'code': 20,
            'leveltype_id': 2,
            'name': u'Division level 2'
        })
        div_level_2.parent_code = div_level_1.code
        div_level_2.geom = geometry
        DBSession.add(div_level_2)

        div_level_3 = AdministrativeDivision(**{
            'code': 30,
            'leveltype_id': 3,
            'name': u'Division level 3'
        })
        div_level_3.parent_code = div_level_2.code
        div_level_3.geom = geometry
        div_level_3.hazardcategories = []

        category_eq_hig = HazardCategory(**{
            'description': u'Earthquake high threshold 1',
        })
        category_eq_hig.hazardtype = DBSession.query(HazardType) \
            .filter(HazardType.mnemonic == u'EQ').one()
        category_eq_hig.intensitythreshold = DBSession.query(IntensityThreshold) \
            .filter(IntensityThreshold.mnemonic == u'EQ_IT_1').one()
        category_eq_hig.categorytype = DBSession.query(CategoryType) \
            .filter(CategoryType.mnemonic == u'HIG').one()
        category_eq_hig.status = DBSession.query(TermStatus) \
            .filter(TermStatus.mnemonic == u'VAL').one()
        div_level_3.hazardcategories.append(category_eq_hig)

        info = AdditionalInformation(**{
            'mnemonic': u'REC1_EQ',
            'title': u'Recommendation #1 for earthquake, applied to hazard' \
                'categories HIG, MED and LOW',
            'description': u'Recommendation #1 for earthquake, applied to' \
                ' hazard categories HIG, MED and LOW'
        })
        info.type = DBSession.query(AdditionalInformationType) \
            .filter(AdditionalInformationType.mnemonic == u'REC').one()
        info.status = DBSession.query(TermStatus) \
            .filter(TermStatus.mnemonic == u'VAL').one()
        association = HazardCategoryAdditionalInformationAssociation(order=1)
        association.hazardcategory = category_eq_hig
        info.hazardcategory_associations.append(association)
        DBSession.add(info)

        info = AdditionalInformation(**{
            'mnemonic': u'AVD1_EQ',
            'title': u'Educational web resources on earthquakes and seismic' \
                ' hazard',
            'description': u'Educational web resources on earthquakes and' \
                ' seismic hazard'
        })
        info.type = DBSession.query(AdditionalInformationType) \
            .filter(AdditionalInformationType.mnemonic == u'AVD').one()
        info.status = DBSession.query(TermStatus) \
            .filter(TermStatus.mnemonic == u'VAL').one()
        association = HazardCategoryAdditionalInformationAssociation(order=1)
        association.hazardcategory = category_eq_hig
        info.hazardcategory_associations.append(association)
        DBSession.add(info)

        category_fl_med = HazardCategory(**{
            'description': u'Flood med threshold 1',
        })
        category_fl_med.hazardtype = DBSession.query(HazardType) \
            .filter(HazardType.mnemonic == u'FL').one()
        category_fl_med.intensitythreshold = DBSession.query(IntensityThreshold) \
            .filter(IntensityThreshold.mnemonic == u'FL_IT_1').one()
        category_fl_med.categorytype = DBSession.query(CategoryType) \
            .filter(CategoryType.mnemonic == u'MED').one()
        category_fl_med.status = DBSession.query(TermStatus) \
            .filter(TermStatus.mnemonic == u'VAL').one()
        div_level_3.hazardcategories.append(category_fl_med)
        DBSession.add(div_level_3)

populate_db()


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        from .. import main
        from webtest import TestApp

        conf_dir = os.getcwd()
        config = 'config:tests.ini'

        app = loadapp(config, relative_to=conf_dir)
        self.testapp = TestApp(app)

    def tearDown(self):
        del self.testapp
