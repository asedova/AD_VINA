# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os, sys

from installed_clients.WorkspaceClient import Workspace
from installed_clients.ProteinStructureUtilsClient import ProteinStructureUtils
from installed_clients.CompoundSetUtilsClient import CompoundSetUtils

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
    GIT_COMMIT_HASH = "c01d599812cc938267e4222eb02dedf55b51183c"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR        
        ws = Workspace(self.workspace_url)
        psu = ProteinStructureUtils(self.callback_url)
        csu = CompoundSetUtils(self.calback_utl)
       
        cls = self.__class__

        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        cls.workspace_url = config['workspace-url']
        cls.shared_folder = config['scratch']
        cls.testData_dir = '/kb/module/test/data'
        cls.config = config

        cls.suffix = str(uuid.uuid4())

        attr_d = {
            'ws': ws,
            'psu': psu,
            'csu': csu,
            'callback_url': cls.callback_url,
            'workspace_url': cls.workspace_url,
            'shared_folder': cls.shared_folder,
            'testData_dir': cls.testData_dir,
            'suffix': cls.suffix
            }

        VarStash.update(attr_d)

        dprint("sys.path", run=globals())
        dprint('os.environ', run=globals())
        dprint('config', run=locals())

        #END_CONSTRUCTOR


    def ad_vina(self, ctx, inparams):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "OutParams" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output

        #BEGIN ad_vina

        
        #####
        ####### 
        #########
        #########
        ######### dl pdb
        #########
        #########
        #######
        #####

        for upa in inparams['pdb_refs']

            ProteinStructure(upa)


            

       
        
        


        (cx, cy, cz)=map(lambda x: float(x), inparams["center"].split(','))
        (sx, sy, sz)=map(lambda x: float(x), inparams["size"].split(','))
        cmd = "vina --receptor %s --ligand %s --cpu 4 --center_x %f --center_y %f  --center_z %f --size_x %f --size_y %f --size_z %f --out %s" % (inparams["receptor"], inparams["ligand"], cx, cy, cz, sx, sy, sz, inparams["outname"])
        print(cmd+"\n")
        os.system(cmd)
        output = {}
#        print(cmd)
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
