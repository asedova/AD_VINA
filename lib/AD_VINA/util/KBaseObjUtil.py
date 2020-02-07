import tarfile
import os


from .PrintUtil import *
from AD_VINAImpl import AD_VINA

#from installed_clients.WorkspaceClient import Workspace
#from installed_clients.ProteinStructureUtilsClient import ProteinStructureUtils
#from installed_clients.CompoundSetUtilsClient import CompoundSetUtils




class VarStash:

    @classmethod
    def update(cls, d: dict):

        for attr_name, attr in d.items():
            setattr(cls, attr_name, attr)





class ProteinStructure:

    def __init__(self, upa, get_file='load'):
        self.upa = upa

        if get_file == 'load': load()


    def load(self):
        
        output = psu.structure_to_pdb_file({
            "input_ref": self.upa, 
            "destination_dir": VarStash.shared_folder
            }
        ); dprint('output', run=locals())
        
        self.pdb_filepath = output["file_path"]
 





class CompoundSet:

    def __init__(self, upa, get_file='load'):
        self.upa = upa

    def load(self):

        output = csu.compound_set_to_file({
            "compound_set_ref": self.upa,
            "output_format": "mol2"
            }
        ); dprint('output', run=locals())

        dprint(f"ls {shared_folder}", run=globals())

        self.mol2_tarball_filepath = output["packed_mol2_files_path"]


    def untargz(self):
        with tarfile.open(self.mol2_tarball_filepath) as tar:
            tar.extractall(path=VarStash.shared_folder)

        dprint(f"ls {VarStash.shared_folder}", run=globals())
        
        


