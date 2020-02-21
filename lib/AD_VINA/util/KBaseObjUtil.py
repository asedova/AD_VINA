import tarfile
import os
import subprocess
import pandas as pd
import numpy as np
import uuid
import logging
import zipfile
import shutil
import json
from subprocess import Popen, PIPE

from .PrintUtil import *


####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################

class VarStash:

    @classmethod
    def update(cls, d: dict):

        for attr_name, attr in list(d.items()):
            setattr(cls, attr_name, attr)








####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################

class ChemKBaseObj:

    AUTODOCK_UTIL_DIR = '/usr/local/lib/mgltools_x86_64Linux2_1.5.6/MGLToolsPckgs/AutoDockTools/Utilities24'








####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################

class ProteinStructure(ChemKBaseObj):

    created_instances = []
    saved_instances = []



    def __init__(self, upa, get_file='load'):
        self.created_instances.append(self)
        self.upa = upa

        if get_file == 'load': 
            self._load()
        if get_file == 'from_cache':
            self._from_cache()
        else: 
            raise NotImplementedError()

        self._get_obj_data()


    def _load(self):

        out_psu_s2pf = VarStash.psu.structure_to_pdb_file({
            "input_ref": self.upa,
            "destination_dir": VarStash.shared_folder
            }
        )

        dprint('out_psu_s2pf', run=locals())

        self.pdb_filepath = out_psu_s2pf["file_path"]



    def _from_cache(self):
        self.pdb_filepath = '/kb/module/test/data/3dnf_clean.pdb'



    def _get_obj_data(self):

        self.objData = VarStash.dfu.get_objects({
            'object_refs': [self.upa]
            })['data'][0]['data']

        self.name = self.objData['name']
        if self.name.endswith('.pdb'): self.name = self.name[:-4]

        self.sequence = self.objData['protein']['sequence']



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

        dprint('min_l', 'max_l', run=locals())

        self.center = (min_l + max_l) / 2
        self.size = max_l - min_l

        dprint('self.center', 'self.size', run=locals())


    def convert_to_pdbqt(self):

        prepare_receptor4_filepath = os.path.join(self.AUTODOCK_UTIL_DIR, 'prepare_receptor4.py')
        self.pdbqt_filepath = self.pdb_filepath + 'qt'

        cmd = f"python2.5 {prepare_receptor4_filepath} -r {self.pdb_filepath} -o {self.pdbqt_filepath}"

        dprint(cmd, run='cli')










####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################


class CompoundSet(ChemKBaseObj):

    created_instances = []
    saved_instances = []



    def __init__(self, upa, get_file='load'):
        self.created_instances.append(self)
        self.upa = upa

        if get_file == 'load':
            self._fetch_mol2()
            self._convert_to_pdbqt()
        elif get_file == 'from_cache':
            self._from_cache()
        elif get_file == 'do_nothing':
            return
        else:
            raise NotImplementedError()

        self._get_obj_data()
        self._to_data_frame()



    def _fetch_mol2(self):
        out_csu_fmffz = VarStash.csu.fetch_mol2_files_from_zinc({
            'workspace_id': VarStash.workspace_id,
            'compoundset_ref': self.upa
            })

        dprint('out_csu_fmffz', run=locals())

        self.upa_old = self.upa
        self.upa = out_csu_fmffz['compoundset_ref']



    def _convert_to_pdbqt(self):

        ##
        ## convert

        out_csu_ccmt2p = VarStash.csu.convert_compoundset_mol2_files_to_pdbqt({
            'input_ref': self.upa
            })

        dprint('out_csu_ccmt2p', run=locals())
 

        ##
        ## filepaths

        packed_pdbqt_files_path = out_csu_ccmt2p['packed_pdbqt_files_path']
        self.pdbqt_dir = os.path.dirname(packed_pdbqt_files_path)

        with zipfile.ZipFile(packed_pdbqt_files_path) as zip_file:
            for member in zip_file.namelist():
                filename = os.path.basename(member)
                if not filename:
                    continue

                source = zip_file.open(member)
                target = open(os.path.join(self.pdbqt_dir, filename), "wb")
                with source, target:
                    shutil.copyfileobj(source, target)


        self.id_to_pdbqt_filepath_d = {id: os.path.join(self.pdbqt_dir, filename) 
                for id, filename in out_csu_ccmt2p['comp_id_pdbqt_file_name_map'].items()}



    def _from_cache(self):
        '''
        This skips the fetching mol2 from zinc (and conversion) step ,
        so the objData *may* be from a CompoundSet with no mol2 files
        '''

        self.pdbqt_dir = '/kb/module/test/data/compound_pdbqt'

        with open('/kb/module/test/data/id_to_pdbqt') as f:
            d = f.read()
        d = json.loads(d)
        
        self.id_to_pdbqt_filepath_d = {id: os.path.join(self.pdbqt_dir, f) for id, f in d.items()}
       
        dprint('self.id_to_pdbqt_filepath_d', run=locals())



    def _get_obj_data(self):
        self.objData = VarStash.dfu.get_objects({
            'object_refs': [self.upa]
            })['data'][0]['data']



    def _to_data_frame(self):

        objData_compound_l = self.objData['compounds']
        attr_l = ['smiles', 'inchikey', 'name', 'charge', 'mass', 'mol2_source', 'deltag', 'formula', 'id'] # id is actually user-entered

        df = pd.DataFrame(columns=attr_l)

        ##
        ## objData
        for objData_compound in objData_compound_l:
            df.loc[len(df)] = [objData_compound.get(key) for key in attr_l]

        ##
        ## pdbqt filepath
        id_l = list(self.id_to_pdbqt_filepath_d.keys())
        pdbqt_filepath_l = list(self.id_to_pdbqt_filepath_d.values())

        df.set_index('id', inplace=True)
        df.loc[id_l, 'pdbqt_filepath'] = pdbqt_filepath_l


        ##
        ## ModelSEED id
        inchikey_2_cpd_filepath = '/kb/module/data/Inchikey_IDs.json'
        with open(inchikey_2_cpd_filepath) as fp:
            d = json.load(fp)

        df['cpd'] = [d.get(inchikey) if d.get(inchikey) else np.nan for inchikey in df['inchikey']]
        df['modelseed_link'] = [f'<a href="modelseed.org/biochem/compounds/{cpd_id}">{cpd_id}</a>' if not(isinstance(cpd_id, float) and np.isnan(cpd_id)) else np.nan for cpd_id in df['cpd']]


        dprint('df', run=locals())

        self.df = df




    #def update_data_frame(self, col_name: str, col: list):
    #    self.df[col_name] = col



    def get_attr_l(self, attr: str, rm_nan=False):
        '''
        If get attributes from here,
        convenient and preserves order
        '''
        if attr not in self.df.columns and attr != self.df.index.name:
            raise ValueError('CompoundSet.get_attr_l: attr not in column or index names')

        if attr in self.df.columns:
            l = self.df[attr].tolist()
        elif attr == self.df.index.name:
            l = self.df.index.tolist()
        else:
            raise Exception()

        if rm_nan:
            l = [e for e in l if not (isinstance(e, float) and np.isnan(e))]

        return l



    def split_multiple_models(self):

        pdbqt_multiple_model_filepath_l = []

        # find multiple models

        for filepath in self.get_attr_l('pdbqt_filepath', rm_nan=True):
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
        # copy first model as pdbqt_filepath
        for pdbqt_filepath in pdbqt_multiple_model_filepath_l:
            pdbqt_filename = os.path.basename(pdbqt_filepath)

            splitting_dir = os.path.join(VarStash.shared_folder, uuid.uuid4())
            os.mkdir(splitting_dir)

            cmd = f"vina_split --input {pdbqt_filepath} --ligand 0"
            dprint(cmd, run='cli', subproc_run_kwargs={'cwd': splitting_dir})

            keep_filename = sorted(os.listdir(splitting_dir))[0]
            cmd = f"cp {os.path.join(splitting_dir, keep_filename)} {pdbqt_filepath}"
            dprint(cmd, run='cli')





####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################

    def mol2_to_pdbqt(self, mol2_file_path, shared_folder, compound_id):

        logging.info('start converting mol2 to pdbqt')

        pdbqt_temp_dir = "{}/{}".format(shared_folder, uuid.uuid4())
        os.mkdir(pdbqt_temp_dir)

        pdbqt_file_path = os.path.join(pdbqt_temp_dir, compound_id + '.pdbqt')

        prepare_ligand4_filepath = os.path.join(self.AUTODOCK_UTIL_DIR, 'prepare_ligand4.py')

        command = ['python2.5', prepare_ligand4_filepath, '-l', mol2_file_path, '-o', pdbqt_file_path]

        process = Popen(command, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        logging.info('completed prepare_ligand4\nstdout:{}\nstderr:{}\n'.format(stdout, stderr))

        if not os.path.exists(pdbqt_file_path):
            pdbqt_file_path = ''
            logging.warning('failed to convert mol2 to pdbqt format')
        else:
            file_size = os.path.getsize(pdbqt_file_path)
            if file_size == 0:
                logging.warning('generated empty pdbqt file')

        return pdbqt_file_path
