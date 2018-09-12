# Copyright (c) 2018 fieldOfView
# The PrinterSettingsPlugin is released under the terms of the AGPLv3 or higher.

import os, json, re
from collections import OrderedDict

from UM.Extension import Extension
from UM.Application import Application
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Logger import Logger

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
            "nozzle_disallowed_areas", "machine_head_polygon", "machine_head_with_fans_polygon", "gantry_height", "machine_nozzle_id",
            "extruders_enabled_count", "machine_gcode_flavor", "machine_heated_bed", "machine_buildplate_type"
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
            category_dict["children"] = OrderedDict()

            for setting in machine_settings_category.children:
                if setting.key not in self._hidden_settings:
                    setting_dict = setting.serialize_to_dict()
                    # Some settings values come out of serialize_to_dict with a = prepended, which does not deserialize nicely
                    for key in ["value", "enabled", "minimum_value", "maximum_value", "minimum_value_warning", "maximum_value_warning"]:
                        if key in setting_dict and setting_dict[key][0] == "=":
                            setting_dict[key] = setting_dict[key][1:]
                    # Boolean values are deserialised as string
                    for (key, value) in setting_dict.items():
                        if value == "True":
                            setting_dict[key] = True
                        if value == "False":
                            setting_dict[key] = False
                    category_dict["children"][setting.key] = setting_dict

            printer_settings_category.deserialize(category_dict)
            container.addDefinition(printer_settings_category)

            container._updateRelations(printer_settings_category)

    def _onEngineCreated(self):
        # Fix preferences
        preferences = self._application.getPreferences()
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
