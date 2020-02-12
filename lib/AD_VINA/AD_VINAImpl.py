# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os, sys
import uuid

from installed_clients.WorkspaceClient import Workspace
from installed_clients.ProteinStructureUtilsClient import ProteinStructureUtils
from installed_clients.CompoundSetUtilsClient import CompoundSetUtils
from installed_clients.DataFileUtilClient import DataFileUtil

from .util.KBaseObjUtil import *
from .util.PrintUtil import *


#END_HEADER


class AD_VINA:
    '''
    Module Name:
    AD_VINA

    Module Description:
    A KBase module: AD_VINA
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/n1mus/AD_VINA"
    GIT_COMMIT_HASH = "0ca1d536cbb7bbc4ef6ef8ea585f5d93c1b48469"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        cls = self.__class__

        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        cls.workspace_url = config['workspace-url']
        cls.shared_folder = config['scratch']
        cls.testData_dir = '/kb/module/test/data'
        cls.config = config

        cls.suffix = str(uuid.uuid4())
        
        ws = Workspace(self.workspace_url)
        dfu = DataFileUtil(self.callback_url)
        psu = ProteinStructureUtils(self.callback_url)
        csu = CompoundSetUtils(self.callback_url)
       

        attr_d = {
            'ws': ws,
            'dfu': dfu,
            'psu': psu,
            'csu': csu,
            'callback_url': cls.callback_url,
            'workspace_url': cls.workspace_url,
            'shared_folder': cls.shared_folder,
            'testData_dir': cls.testData_dir,
            'suffix': cls.suffix
            }

        VarStash.update(attr_d)

        dprint("sys.path", "os.environ", run=globals())
        dprint('config', run=locals())

        #END_CONSTRUCTOR
        pass


    def ad_vina(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN ad_vina


        VarStash.update({
            'ctx': ctx,
            'workspace_id': params['workspace_id']
            })

        dprint('ctx', 'params', run={**locals(), **globals()})
        

        ##
        ### 
        ####
        #####
        ###### default params
        #####
        ####
        ###
        ##

        params_default = {
            'num_modes': 1000,
            'energy_range': 10,
            'exhaustiveness': 20,
            }



        ##
        ### 
        ####
        #####
        ###### seed
        #####
        ####
        ###
        ##




        ##
        ### 
        ####
        #####
        ###### dl
        #####
        ####
        ###
        ##

        for upa in params['pdb_refs']:

            ps = ProteinStructure(upa)
            ps.calc_center_size()
            ps.convert_to_pdbqt()

        cs = CompoundSet(params['ligand_list_ref'])


        ##
        ### 
        ####
        #####
        ###### run
        #####
        ####
        ###
        ##



        for ps in ProteinStructure.created_instances:
            for ligand_name, ligand_pdbqt_filepath in zip(cs.pdbqt_compound_l, cs.pdbqt_filepath_l):
     
                run_name = ligand_name + '_vs_' + ps.name

                cmd = ( f"vina --receptor {ps.pdbqt_filepath} --ligand {ligand_pdbqt_filepath} "
                        f"--cpu 4 --log {run_name + '.log'} "
                        f"--center_x {ps.center[0]} --center_y {ps.center[1]} --center_z {ps.center[2]} "
                        f"--size_x {ps.size[0]} --size_y {ps.size[1]} --size_z {ps.size[2]} "
                        f"--out {run_name + '.pdbqt'}" )
                
                dprint(cmd, run='cli', subproc_run_kwargs={'cwd': VarStash.shared_folder})

        
        
        """

        (cx, cy, cz)=[float(x) for x in params["center"].split(',')]
        (sx, sy, sz)=[float(x) for x in params["size"].split(',')]
        cmd = "vina --receptor %s --ligand %s --cpu 4 --center_x %f --center_y %f  --center_z %f --size_x %f --size_y %f --size_z %f --out %s" % (params["receptor"], params["ligand"], cx, cy, cz, sx, sy, sz, params["outname"])
        print((cmd+"\n"))
        os.system(cmd)
        output = {}
        print(cmd)

        """
        return None
        #END ad_vina

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method ad_vina return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
