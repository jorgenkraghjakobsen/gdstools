#!/usr/bin/python3

# -*- coding: utf-8 -*-

import gdstk as gdspy

# open a gds file
#gdsii = gdspy.GdsLibrary(infile='sg13g2_stdcell.gds')
gdsii = gdspy.gds_info('sg13g2_stdcell.gds')

# get the cell names
#cell_names = gdsii.cells.keys()
cell_names = list(gdsii.values())[0]

# print the cell names
for cell_name in cell_names:
    print(cell_name)
    




