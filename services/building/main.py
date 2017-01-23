# -*- coding: utf-8 -*-  # NOQA
from service_framework.plugin_module import Plugin_module as framework  # NOQA
from services.building.collectionviewer.restserver import config as colview  # NOQA
from services.building.collectioneditor.restserver import config as coledit  # NOQA
from services.building.entity.restserver import config as entity  # NOQA

framework([entity, colview, coledit])
