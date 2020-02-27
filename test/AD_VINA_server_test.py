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

from AD_VINA.util.print import *



_3dnf_clean_pdb = "38305/2/1"
test_compound_set = "38305/4/6"
test_compounds_1cpd_noMOL2 = "38305/9/1"
test_compounds_1cpd_wMOL2_lineWJustTabs = "38305/7/1"
test_compounds_justHeader = "38305/8/1"




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

params_shortcut = {
    #'skip_dl': True,
    #'skip_most_vina' : True,
    #'skip_save': True,
    }

params_search_space_default = {space_type + '_' + ch: None for space_type in ['center', 'size'] for ch in list('xyz')}


class AD_VINATest(unittest.TestCase):

    def _test(self):
        params = {
            **params_input,
            'search_space': params_search_space_default,
            **params_misc_quick,
            **self.params_ws,
            **params_shortcut,
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
        dprint(
            tag + 
            ' DO NOT FORGET TO GRAB HTML(S) ' + 
            tag +
            ' DO NOT FORGET TO GRAB RETURN FILES ' +
            tag
            )



########################### input tests ############################################################

    def _test_incomplete_center(self):
        params_search_space = params_search_space_default.copy()
        params_search_space['center_x'] = 0
        params = {
            **params_input,
            'search_space': params_search_space,
            **params_misc_quick,
            **params_shortcut,
            **self.params_ws
            }
        with self.assertRaises(Exception) as cm:
            self.serviceImpl.ad_vina(self.ctx, params)
            self.assertEquals(
                str(cm.exception),
                'INPUT ERROR: '
                'If any of center (i.e., center_x, center_y, center_z) are specified, '
                'all of center must be specified. '
                'Please try again'
                )


    def _test_empty_compound_set(self):
        params_input_ = params_input.copy()
        params_input_['ligand_list_ref'] = '38305/8/1'
        params = {
            **params_input_,
            'search_space': params_search_space_default,
            **params_misc_quick,
            **params_shortcut,
            **self.params_ws
            }
        with self.assertRaises(Exception) as cm:
            self.serviceImpl.ad_vina(self.ctx, params)
            self.assertEquals(
                str(cm.exception),
                'INPUT ERROR: '
                'Please input a CompoundSet object that has greater than 0 compounds in it'
                )
            

    def _test_cs_1cpd_noMOL2(self):
        params_input_ = params_input.copy()
        params_input_['ligand_list_ref'] = '38305/9/1'
        params = {
            **params_input_,
            'search_space': params_search_space_default,
            **params_misc_quick,
            **self.params_ws
            }
        with self.assertRaises(Exception) as cm:
            self.serviceImpl.ad_vina(self.ctx, params)
            self.assertEquals(
                str(cm.exception),
                f"Sorry, none of the compounds in the input CompoundSet with name test_compounds_1cpd_noMOL2 "
                "had associated MOL2 files, whether user-entered or looked up on ZINC. "
                "There are no ligand files to run AutoDock Vina on"
                )


    def test_cs_1cpd_wMOL2(self):
        params_input_ = params_input.copy()
        params_input_['ligand_list_ref'] = '38491/7/1'
        params = {
            **params_input_,
            'search_space': params_search_space_default,
            **params_misc_quick,
            **self.params_ws
            }
        ret = self.serviceImpl.ad_vina(self.ctx, params)


