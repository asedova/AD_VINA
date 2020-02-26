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
test_compound_set = "38376/3/29"



params_input = {
    'pdb_ref': _3dnf_clean_pdb,
    'ligand_list_ref': test_compound_set,
    }


params_misc_vinaDefault = {
    'exhaustiveness': '8',
    'num_modes': 9,
    'energy_range': 3
    }

params_misc_quick = {
    'exhaustiveness': 2,
    'num_modes': 2,
    'energy_range': 3
    }

params_local = {
    #'skip_dl': True,
    #'skip_most_vina' : True,
    }

params_search_space_default = {space_type + '_' + ch: None for space_type in ['center', 'size'] for ch in list('xyz')}


class AD_VINATest(unittest.TestCase):

    def test(self):
        params = {
            **params_input,
            'search_space': params_search_space_default,
            **params_misc_quick,
            **params_local,
            **self.params_ws,
            }
        ret = self.serviceImpl.ad_vina(self.ctx, params)
        dprint('ret', run=locals())


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
        cls.params_ws = {
            'workspace_id': cls.wsId,
            'workspace_name': cls.wsName,
            }
        dprint('cls.wsId', run=locals())
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
        tag = '!!!!!!!!!!!!!!!!!!!!!!!!!!' * 40
        dprint(tag + ' DO NOT FORGET TO GRAB HTML(S) ' + tag)



########################### quick tests ############################################################

    def test_incomplete_center(self):
        params_search_space = params_search_space_default.copy()
        params_search_space['center_x'] = 0
        params = {
            **params_input,
            'search_space': params_search_space,
            **params_misc_quick,
            **params_local,
            **self.params_ws
            }
        self.assertRaises(ValueError, self.serviceImpl.ad_vina, self.ctx, params)


