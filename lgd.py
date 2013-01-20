# -*- coding: utf-8 -*-
"""
/***************************************************************************
 lgd
                                 A QGIS plugin
 A LinkedGeoData SPARQL query tool
                              -------------------
        begin                : 2013-01-20
        copyright            : (C) 2013 by Stepan Kuzmin
        email                : to.stepan.kuzmin@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
import sparql
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from lgddialog import lgdDialog


class lgd:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/lgd"
        # initialize locale
        localePath = ""
        locale = QSettings().value("locale/userLocale").toString()[0:2]

        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/lgd_" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = lgdDialog()

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/lgd/icon.png"),
            u"LinkedGeoData query tool", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&LinkedGeoData", self.action)
        QObject.connect(self.dlg.ui.queryPushButton, SIGNAL("clicked()"), self.runQuery)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&LinkedGeoData", self.action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            pass

    def runQuery(self):
      endpoint = str(self.dlg.ui.endpointLineEdit.text())
      query = str(self.dlg.ui.queryPlainTextEdit.toPlainText())
      result = sparql.query(endpoint, query)

      vl = QgsVectorLayer("Point", "temporary_points", "memory")
      pr = vl.dataProvider()
      vl.startEditing()

      pr.addAttributes([QgsField(result.variables[0], QVariant.String), QgsField(result.variables[1],  QVariant.String)])

      for row in result:
        values = sparql.unpack_row(row)
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromWkt(values[2]))
        fet.setAttributeMap({0 : QVariant(values[0]), 1 : QVariant(values[1])})
        pr.addFeatures([fet])
      
      vl.commitChanges()
      vl.updateExtents()
      QgsMapLayerRegistry.instance().addMapLayer(vl)
