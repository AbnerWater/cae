#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    © Ihor Mirzov, UJV Rez, June 2019.
    Distributed under GNU General Public License, version 2.

    CalculiX CAE
    Main window application
"""


import sys, os, argparse, vtk
from PyQt5 import QtWidgets, uic, QtCore, QtGui
import ccx_mesh, ccx_dom, ccx_tree, ccx_log, ccx_vtk, ccx_inp


class CAE(QtWidgets.QMainWindow):

    # Create main window
    def __init__(self):

        # Create main window
        QtWidgets.QMainWindow.__init__(self)

        # Load form
        uic.loadUi('ccx_cae.ui', self)

        # Configure logging
        self.logger = ccx_log.logger(self.textEdit)

        # Create VTK widget
        self.VTK = ccx_vtk.VTK(self.textEdit) # create everything for model visualization
        self.vl.addWidget(self.VTK.widget) # add vtk_widget to the form
        self.frame.setLayout(self.vl) # apply layout: it will expand vtk_widget to the frame size

        # Generate empty CalculiX model and treeView items
        self.tree = ccx_tree.tree(self.treeView, self.textEdit)

        # Default start model could be chosen with command line parameter
        parser = argparse.ArgumentParser()
        parser.add_argument("--mesh", "-mesh",
                            help="Mesh .inp file",
                            type=str, default='test.inp')
        args = parser.parse_args()

        # Creates VTK widget with default ugrid, adds it to the form
        self.importINP(args.mesh)

        # Actions
        self.actionImportINP.triggered.connect(self.importINP)
        self.actionCameraFitView.triggered.connect(self.VTK.cameraFitView)
        self.actionSelectNodes.triggered.connect(self.VTK.selectNodes)
        self.actionSelectElements.triggered.connect(self.VTK.selectElements)
        self.actionClearSelection.triggered.connect(self.VTK.clearSelection)


    # Import mesh and display it in the VTK widget
    def importINP(self, file_name=None):

        if not file_name:
            file_name = QtWidgets.QFileDialog.getOpenFileName(self,\
                'Import .inp mesh', '', 'Input files (*.inp);;All Files (*)')[0]

        self.logger.info('Loading ' + file_name + '.')

        if file_name:
            # Generate empty CalculiX model (DOM) and treeView items
            self.tree = ccx_tree.tree(self.treeView, self.textEdit)

            # Parse model from INP - it will modify DOM
            with open(file_name, 'r') as f:
                INP_code = f.readlines()
                model = ccx_inp.Parse(self.tree.DOM, self.textEdit, INP_code)

            # Regenerate treeView items to account for modifications in DOM
            self.tree.generateTreeView()

            # Parse mesh and transfer it to VTK
            mesh = ccx_mesh.Parse(file_name, self.textEdit) # parse mesh, textEdit passed for logging
            try:
                points = vtk.vtkPoints()
                for n in mesh.nodes.keys(): # create VTK points from mesh nodes
                    points.InsertPoint(n-1, mesh.nodes[n]) # node numbers should start from 0!
                self.ugrid = vtk.vtkUnstructuredGrid() # create empty grid in VTK
                self.ugrid.Allocate(len(mesh.elements)) # allocate memory fo all elements
                self.ugrid.SetPoints(points) # insert all points to the grid
                for e in mesh.elements.keys():
                    vtk_element_type = ccx_mesh.Parse.convert_elem_type(mesh.types[e])
                    node_numbers = [n-1 for n in mesh.elements[e]] # list of nodes in the element: node numbers should start from 0!
                    self.ugrid.InsertNextCell(vtk_element_type, len(node_numbers), node_numbers) # create VTK element

                self.VTK.mapper.SetInputData(self.ugrid) # ugrid is our mesh data
                self.VTK.cameraFitView() # reset camera

                self.logger.info('Rendering OK.')
            except:
                self.logger.error('Can\'t render INP mesh.')


if __name__ == '__main__':

    # Clean cached files before start
    os.system('py3clean .')

    app = QtWidgets.QApplication(sys.argv)
    window = CAE()
    window.show() # window.showMaximized() or window.show()
    sys.exit(app.exec_())
