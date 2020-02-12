import tarfile
import os


from .PrintUtil import *

#from installed_clients.WorkspaceClient import Workspace
#from installed_clients.ProteinStructureUtilsClient import ProteinStructureUtils
#from installed_clients.CompoundSetUtilsClient import CompoundSetUtils




class VarStash:

    @classmethod
    def update(cls, d: dict):

        for attr_name, attr in list(d.items()):
            setattr(cls, attr_name, attr)





class ProteinStructure:

    created_instances = []

    def __init__(self, upa, get_file='load'):
        self.created_instances.append(self)
        self.upa = upa

        if get_file == 'load': self.load()
        else: raise NotImplementedError()


    def load(self):
        
        output = VarStash.psu.structure_to_pdb_file({
            "input_ref": self.upa, 
            "destination_dir": VarStash.shared_folder
            }
        )
        
        dprint('output', run=locals())
        dprint(f"ls {VarStash.shared_folder}", run='cli')
        
        self.pdb_filepath = output["file_path"]
 
        




class CompoundSet:

    created_instances = []

    def __init__(self, upa, get_file='load'):
        self.created_instances.append(self)
        self.upa = upa

        if get_file == 'load': self.load()
        else: raise NotImplementedError()

    @where_am_i
    def load(self):

        dprint(f'ls -R {VarStash.shared_folder}', run='cli')

        out_csu_fmffz = VarStash.csu.fetch_mol2_files_from_zinc({
            'workspace_id': VarStash.workspace_id,
            'compoundset_ref': self.upa
            })

        #compoundset_obj = VarStash.dfu.get_objects({
        #    'object_refs': [output['compoundset_ref']]
        #    })['data'][0]

        #dprint('compoundset_obj', run=locals())

        #dprint("[i.get('mol2_handle_ref') for i in compoundset_obj['data']['compounds']]", run=locals())

        dprint('out_csu_fmffz', run=locals())
        dprint(f'ls -R {VarStash.shared_folder}', run='cli')
        
        out_csu_ccmftp = VarStash.csu.convert_compoundset_mol2_files_to_pdbqt({
            'input_ref': out_csu_fmffz['compoundset_ref']
            })


        dprint('out_csu_ccmftp', run=locals())
        dprint(f"ls -R {VarStash.shared_folder}", run='cli')

        self.pdbqt_dir = os.path.dirname(out_csu_ccmftp['packed_pdbqt_files_path']
        self.compound_to_pbdqtFileName_d = out_csu_ccmftp['comp_id_pdbqt_file_name_map']

        '''
        output = VarStash.csu.compound_set_to_file({
            "compound_set_ref": self.upa,
            "output_format": "mol2"
            }
        )
        
        self.mol2_tarball_filepath = output["packed_mol2_files_path"]

        ###############

        packed_pdbqt_files_path, comp_id_pdbqt_file_name_map = VarStash.csu._covert_mol2_files_to_pdbqt(self.upa)

        dprint('packed_pdbqt_files_path', 'comp_id_pdbqt_file_name_map', run=locals())

        '''


    def untargz(self):
        with tarfile.open(self.mol2_tarball_filepath) as tar:
            tar.extractall(path=VarStash.shared_folder)

        dprint(f"ls {VarStash.shared_folder}", run=globals())
        
        

