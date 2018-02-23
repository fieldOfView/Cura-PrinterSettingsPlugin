# Copyright (c) 2018 fieldOfView
# The PrinterSettingsPlugin is released under the terms of the AGPLv3 or higher.

from . import PrinterSettingsPlugin
from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("PrinterSettingsPlugin")

def getMetaData():
    return {}

def register(app):
    return {"extension": PrinterSettingsPlugin.PrinterSettingsPlugin()}
