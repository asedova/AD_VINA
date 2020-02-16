
import pandas as pd
import numpy as np


from .PrintUtil import *
from .KBaseObjUtil import *


class HTMLBuilder:

    html_filepath = '/kb/module/lib/AD_VINA/util/index.html'
    TAGS = [tag + '_TAG' for tag in ['PROTEIN', 'WARNINGS', 'CMDS', 'JSON', 'COLUMNS']]
    

    def __init__(self, ps: ProteinStructure, cs: CompoundSet):
        self.ps = ps
        self.cs = cs
    
        self.replacements = {}

        self._build()


    def _build(self):

        #self._build_protein()
        #self._build_warnings()
        #self._build_cmds()
        self._build_table()


    def _build_protein(self):
        self.replacements['PROTEIN_TAG'] = self.ps.name

    def _build_table():


        col_comp_info = ['Compound', 'Formula', 'ModelSEED ID', 'SMILES', 'Exact Mass', 'Charge', 'mol2 Source']
        col_dock_info = ['Mode', 'Affinity (kcal/mol)', 'RMSD l.b.', 'RMSD u.b.']
        
        columns = col_comp_info[:3] + col_dock_info + col_comp_info[3:]


    







