# Copyright (c) 2018 fieldOfView
# The PrinterSettingsPlugin is released under the terms of the AGPLv3 or higher.

import os, json, re

from UM.Extension import Extension
from UM.Application import Application
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Logger import Logger
from UM.Preferences import Preferences

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("PrinterSettingsPlugin")

class PrinterSettingsPlugin(Extension):
    def __init__(self):
        super().__init__()

        self._i18n_catalog = None
        self._application = Application.getInstance()

        self._category_key = "printer_settings"
        self._category_dict = {
            "label": "Printer Settings",
            "description": "Machine specific settings.",
            "type": "category",
            "icon": "category_machine"
        }
        self._hidden_settings = [
            "machine_show_variants", "machine_start_gcode", "machine_end_gcode", "material_guid", "material_print_temp_prepend", "material_bed_temp_prepend",
            "machine_width", "machine_depth", "machine_shape", "machine_height", "machine_center_is_zero", "machine_extruder_count", "machine_disallowed_areas",
            "nozzle_disallowed_areas", "machine_head_polygon", "machine_head_with_fans_polygon", "gantry_height", "machine_nozzle_id"
        ]

        self._application.engineCreatedSignal.connect(self._onEngineCreated)
        ContainerRegistry.getInstance().containerLoadComplete.connect(self._onContainerLoadComplete)


    def _onContainerLoadComplete(self, container_id):
        container = ContainerRegistry.getInstance().findContainers(id = container_id)[0]
        if not isinstance(container, DefinitionContainer):
            # skip containers that are not definitions
            return
        if container.getMetaDataEntry("type") == "extruder":
            # skip extruder definitions
            return

        machine_settings_category = container.findDefinitions(key="machine_settings")
        printer_settings_category = container.findDefinitions(key=self._category_key)
        if machine_settings_category and not printer_settings_category:
            # this machine doesn't have a printer_settings category yet
            machine_settings_category = machine_settings_category[0]
            printer_settings_category = SettingDefinition(self._category_key, container, None, self._i18n_catalog)

            category_dict = self._category_dict
            category_dict["children"] = {}


            for setting in machine_settings_category.children:
                if setting.key not in self._hidden_settings:
                    category_dict["children"][setting.key] = setting.serialize_to_dict()
                    #setting._parent = printer_settings_category
                    #setting._updateAncestors()
                    #printer_settings_category._children.append(setting)

            printer_settings_category.deserialize(category_dict)
            container.addDefinition(printer_settings_category)

            container._updateRelations(printer_settings_category)

    def _onEngineCreated(self):
        # Fix preferences
        preferences = Preferences.getInstance()
        visible_settings = preferences.getValue("general/visible_settings")
        if not visible_settings:
            # Wait until the default visible settings have been set
            return

        visible_settings_changed = False
        if self._category_key not in visible_settings:
            visible_settings += ";%s" % self._category_key
            visible_settings_changed = True

        if not visible_settings_changed:
            return

        preferences.setValue("general/visible_settings", visible_settings)
