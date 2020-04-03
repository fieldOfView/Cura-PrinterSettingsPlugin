# Copyright (c) 2018 fieldOfView
# The PrinterSettingsPlugin is released under the terms of the AGPLv3 or higher.

from . import PrinterSettingsPlugin


def getMetaData():
    return {}

def register(app):
    return {"extension": PrinterSettingsPlugin.PrinterSettingsPlugin()}
