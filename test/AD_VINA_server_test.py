# -*- coding: utf-8 -*-
import unittest
import os, sys  # noqa: F401
import json  # noqa: F401
import time
import requests
import uuid
from os import environ
from configparser import ConfigParser  # py3



from biokbase.workspace.client import Workspace as workspaceService
from AD_VINA.AD_VINAImpl import AD_VINA
from AD_VINA.AD_VINAServer import MethodContext
from AD_VINA.authclient import KBaseAuth as _KBaseAuth

from AD_VINA.util.PrintUtil import *



_3dnf_clean_pdb = "37778/2/1"
test_compound_set = "37778/4/3"



defaults = {
    'exhaustiveness': '8',
    'num_modes': 9,
    'energy_range': 3
    }

defaults_quick = {
    'exhaustiveness': 1,
    'num_modes': 2,
    'energy_range': 3
    }

params_local = {
    'skip_most_vina' : True
    }

defaults_search_space = {space_type + '_' + ch: None for space_type in ['center', 'size'] for ch in list('xyz')}


class AD_VINATest(unittest.TestCase):

    def test(self):
        params = {
            "pdb_ref": _3dnf_clean_pdb,
            'ligand_list_ref': test_compound_set,
            'workspace_id': self.wsId,
            'workspace_name': self.wsName,
            'search_space': defaults_search_space,
            **defaults_quick,
            **params_local,
            }
        ret = self.serviceImpl.ad_vina(self.ctx, params)

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('AD_VINA'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'AD_VINA',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL)
        cls.wsName = 'AD_VINA_' + str(uuid.uuid4())
        cls.wsId = cls.wsClient.create_workspace({'workspace': cls.wsName})[0]
        dprint(cls.wsId, type(cls.wsId))
        cls.serviceImpl = AD_VINA(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']

        cmd = f"rm -rf /kb/module/work/tmp/*"
        dprint(cmd, run='cli')


    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def _test_static_AD_VINA(self):
        inparams = {
            "receptor" : "lck_small.pdbqt",
            "ligand" : "lck-active-26.pdbqt",
            "center" :  "18.273, 44.681, 80.351",
            "size" : "50, 50, 50",
            "outname" : "out.pdbqt"
        }
        ret = self.getImpl().ad_vina(self.getContext(), inparams)[0]

    def _test_mol2_to_pdbqt(self):

        mol2_file_path = os.path.join('data', 'cpd00094.mol2')
        compound_id = 'cpd00094'

        pdbqt_file_path = self.serviceImpl.mol2_to_pdbqt(self.ctx,
                                                         mol2_file_path=mol2_file_path,
                                                         compound_id=compound_id)[0]

        self.assertEqual(os.path.basename(pdbqt_file_path), compound_id + '.pdbqt')
        self.assertTrue(os.path.exists(pdbqt_file_path))
        self.assertTrue(os.path.getsize(pdbqt_file_path) > 0)
