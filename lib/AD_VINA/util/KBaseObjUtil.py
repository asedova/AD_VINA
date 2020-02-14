import tarfile
import os
import subprocess
import numpy as np

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
        
        out_psu_stpf = VarStash.psu.structure_to_pdb_file({
            "input_ref": self.upa, 
            "destination_dir": VarStash.shared_folder
            }
        )
        
        dprint('out_psu_stpf', run=locals())
        
        self.pdb_filepath = out_psu_stpf["file_path"]
        
        pdb_filename = os.path.basename(self.pdb_filepath)
        if pdb_filename.endswith('.pdb'):
            self.name = pdb_filename[:-4]
        else:
            self.name = pdb_filename


    def calc_center_size(self):
        coords_filepath = os.path.join(VarStash.shared_folder, 'atom_coords_' + self.name + VarStash.suffix)

        cmd = rf"sed -n '/^ATOM/p' {self.pdb_filepath} | cut -c 31-54 > {coords_filepath}"
        dprint(cmd, run='cli')

        with open(coords_filepath) as f:
            min_l = np.array([np.inf, np.inf, np.inf])
            max_l = np.array([-np.inf, -np.inf, -np.inf])
            for line in f:
                coords = np.array([float(tok.strip()) for tok in [line[:8], line[8:16], line[16:24]]])
                min_l[coords < min_l] = coords[coords < min_l]
                max_l[coords > max_l] = coords[coords > max_l]


        self.center = (min_l + max_l) / 2
        self.size = max_l - min_l

        dprint('self.center', 'self.size', run=locals())


    def convert_to_pdbqt(self):

        prepare_receptor4_filepath = '/usr/local/bin/mgltools_x86_64Linux2_1.5.6/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_receptor4.py'
        self.pdbqt_filepath = self.pdb_filepath + 'qt'

        cmd = f"python2.5 {prepare_receptor4_filepath} -r {self.pdb_filepath} -o {self.pdbqt_filepath}"

        subprocess.run(cmd)
       



class CompoundSet:

    created_instances = []

    def __init__(self, upa, get_file='load'):
        self.created_instances.append(self)
        self.upa = upa

        if get_file == 'load': self.load()
        else: raise NotImplementedError()

    @where_am_i
    def load(self):

        out_csu_fmffz = VarStash.csu.fetch_mol2_files_from_zinc({
            'workspace_id': VarStash.workspace_id,
            'compoundset_ref': self.upa
            })


        compoundset_objData = VarStash.dfu.get_objects({
            'object_refs': [out_csu_fmffz['compoundset_ref']]
            })['data'][0]['data']

        self.comp_id_l = [compound['id'] for compound in compoundset_objData['compounds']]


        ##
        ## compound names

        self.comp_id_to_name = {compound['id']: compound['name'] for compound in compoundset_objData['compounds']}


        ###
        ### compounds with/without mol2


        self.comp_id_to_mol2_handle_ref = {compound['id']: compound.get('mol2_handle_ref') for compound in compoundset_objData['compounds']}

        self.comp_id_w_mol2 = [comp_id for comp_id in self.comp_id_l if self.comp_id_to_mol2_handle_ref[comp_id]]
        self.comp_id_wo_mol2 = [comp_id for comp_id in self.comp_id_l if comp_id not in self.comp_id_w_mol2]

        assert sorted(self.comp_id_w_mol2 + self.comp_id_wo_mol2) == sorted(self.comp_id_l)

        ###
        ### filepaths

        dprint('out_csu_fmffz', run=locals())
        
        out_csu_ccmftp = VarStash.csu.convert_compoundset_mol2_files_to_pdbqt({
            'input_ref': out_csu_fmffz['compoundset_ref']
            })

        dprint('out_csu_ccmftp', run=locals())

        self.pdbqt_dir = os.path.dirname(out_csu_ccmftp['packed_pdbqt_files_path'])
        self.comp_id_to_pdbqtFileName_d = out_csu_ccmftp['comp_id_pdbqt_file_name_map']

        self.pdbqt_filepath_l = [os.path.join(self.pdbqt_dir, filename) for filename in self.comp_id_to_pdbqtFileName_d.values()]
        self.pdbqt_compound_l = [compound for compound in self.comp_id_to_pdbqtFileName_d.keys()]


        
    def split_multiple_models(self):

        pdbqt_multiple_model_filepath_l = []

        # find multiple models

        for filepath in self.pdbqt_filepath_l:
            with open(filepath) as f:
                for line in f:
                    if line.strip() == '':
                        continue
                    elif line.startswith('MODEL'):
                        if line.strip().endswith('1'):
                            pdbqt_multiple_model_filepath_l.append(filepath)
                            break
                        else:
                            raise Exception("Unknown pdbqt format")
                    else:
                        break

        # for each
        # split in splitting dir
        # copy first model into self.pdbqt_dir
        for pdbqt_filepath in pdbqt_multiple_model_filepath_l:
            pdbqt_filename = os.path.basename(pdbqt_filepath)
            
            splitting_dir = 'split_' + pdbqt_filename + VarStash.suffix
            os.mkdir(splitting_dir)
            
            cmd = f"vina_split --input {pdbqt_filepath} --ligand 0"
            dprint(cmd, run='cli', subproc_run_kwargs={'cwd': splitting_dir})
            
            keep_filename = sorted(os.listdir(splitting_dir))[0]
            cmd = f"cp {os.path.join(splitting_dir, keep_filename)} {pdbqt_filepath}"
            dprint(cmd, run='cli')


        

