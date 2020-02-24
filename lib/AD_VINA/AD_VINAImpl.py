# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os, sys, shutil
import uuid

from installed_clients.WorkspaceClient import Workspace
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.ProteinStructureUtilsClient import ProteinStructureUtils
from installed_clients.CompoundSetUtilsClient import CompoundSetUtils
from installed_clients.DataFileUtilClient import DataFileUtil

from .util.KBaseObjUtil import *
from .util.PrintUtil import *
from .util.HTMLUtil import *


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
    GIT_COMMIT_HASH = "7c7740cd7d0b5516ad02880b1440b7e97cb59349"

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

        cls.suffix = '_' + str(uuid.uuid4())

        ws = Workspace(self.workspace_url)
        dfu = DataFileUtil(self.callback_url)
        psu = ProteinStructureUtils(self.callback_url)
        csu = CompoundSetUtils(self.callback_url)

        warnings = []

        attr_d = {
            'ws': ws,
            'dfu': dfu,
            'psu': psu,
            'csu': csu,
            'callback_url': cls.callback_url,
            'workspace_url': cls.workspace_url,
            'shared_folder': cls.shared_folder,
            'testData_dir': cls.testData_dir,
            'suffix': cls.suffix,
            'warnings': warnings
            }

        VarStash.update(attr_d)

        dprint("sys.path", "os.environ", run=globals())
        dprint('config', run=locals())

        
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            level=logging.INFO)

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

        ctx_censored = ctx.copy()
        ctx_censored.pop('token')
        

        dprint('params', 'ctx_censored', run=locals())


        ##
        ####
        ###### param validation
        ###### and defaulting
        ####
        ##


        params_search_space = params['search_space']


        ##
        ## if center specified, must be completely specified

        key_center_l = ['center_' + ch for ch in list('xyz')]
        center_xyz = [params_search_space[key] for key in key_center_l]

        if any(center_xyz) and not all(center_xyz):
            raise ValueError(
                'INPUT ERROR: '
                'If any of center (i.e., center_x, center_y, center_z) is specified, all of center must be specified. '
                'Please try again'
                )


        ##
        ## if center specified, fill in default size

        size_default = 30 # Angstroms

        key_size_l = ['size_' + ch for ch in list('xyz')]
        size_xyz = [params_search_space[key] for key in key_size_l]

        if all(center_xyz) and not all(size_xyz):
            for key_size in key_size_l:
                if not params_search_space.get(key_size):
                    params_search_space[key_size] = size_default



        ##
        ####
        ###### dl
        ####
        ##

        get_file = 'from_cache' if params.get('skip_dl') else 'load'

        ps = ProteinStructure(params['pdb_ref'], get_file=get_file)
        ps.calc_center_size()
        ps.convert_to_pdbqt()

        cs = CompoundSet(params['ligand_list_ref'], get_file=get_file)
        cs.split_multiple_models()




        ##
        ####
        ###### params
        ###### run
        ####
        ##

        run_dir = os.path.join(VarStash.shared_folder, 'vina' + VarStash.suffix)
        os.mkdir(run_dir)


        ##

        params_static = {
            'cpu': 4
            }

        params_default = {
            'num_modes': 1000,
            'energy_range': 10,
            'exhaustiveness': 20,
            }

        ##

        key_search_space_l = key_center_l + key_size_l
        key_misc_l = ['num_modes', 'energy_range', 'seed', 'exhaustiveness']


        ## collectables

        id_l = []
        out_pdbqt_filename_l = []
        log_filename_l = []
        cmd_l = []


        ##
        ## for each compound

        for id, pdbqt_filepath in zip(cs.get_attr_l('id'), cs.get_attr_l('pdbqt_filepath')):

            if params.get('skip_vina'):
                break

            if isinstance(pdbqt_filepath, float) and np.isnan(pdbqt_filepath): # no mol2 -> no pdbqt -> skip
                continue
            else:
                id_l.append(id)

            run_name = f'compoundID[' + id.replace('/', '-') + ']_vs_protein[' + ps.name + ']'

            out_pdbqt_filename_l.append(run_name + '.pdbqt')
            log_filename_l.append(run_name + '.log')

            ##
            ## set up default params

            params_vina = {
                'receptor': ps.pdbqt_filepath,
                'ligand': pdbqt_filepath,
                'log': run_name + '.log',
                'out': run_name + '.pdbqt',
                **params_static,
                **params_default
            }

            for space_coords_name in ['center', 'size']:
                space_coords = getattr(ps, space_coords_name)
                for k, v in zip(list('xyz'), space_coords):
                    params_vina[space_coords_name + '_' + k] = v

            ##
            ## check for search_space and misc params

            for key in key_misc_l:
                if params.get(key):
                    params_vina[key] = params[key]

            for key in key_search_space_l:
                if params_search_space.get(key):
                    params_vina[key] = params_search_space[key]


            ##
            ##

            cmd = 'vina'

            for param, arg in params_vina.items():
                cmd += ' --' + param + ' ' + str(arg)

            cmd_l.append(cmd)

            retcode, stdout, stderr = dprint(cmd, run='cli', subproc_run_kwargs={'cwd': run_dir})
            
            if retcode != 0:
                raise RuntimeError(
                        f"AutoDock terminated abnormally with error message: "
                        f"[{stderr}] "
                        "You can check logs (click 'Job Status' tab in upper right of cell) for more information"
                        )

            if params.get('skip_most_vina'):
                break

        log_filepath_l = [os.path.join(run_dir, f) for f in log_filename_l]
        cs.df.loc[id_l, 'log_filepath'] = log_filepath_l


        dprint('cs.df', run=locals())

        ##
        ####
        ###### html
        ####
        ##

        hb = HTMLBuilder(ps, cs, cmd_l)



        ##
        ####
        ###### return directories
        ####
        ##


        def dir_to_shock(dir_path, name, description):
            '''
            For regular directories or html directories
            
            name - for regular directories: the name of the flat (zip) file returned to ui
                   for html directories: the name of the html file
            '''
            dfu_fileToShock_ret = VarStash.dfu.file_to_shock({
                'file_path': dir_path,
                'make_handle': 0,
                'pack': 'zip',
                })

            dir_shockInfo = {
                'shock_id': dfu_fileToShock_ret['shock_id'],
                'name': name,
                'description': description
                }

            return dir_shockInfo
        ##
        ## return files

        dir_retFiles = os.path.join(self.shared_folder, 'pdbqt_log_dir')
        os.mkdir(dir_retFiles)

        #

        full_table_filepath = os.path.join(dir_retFiles, 'full.csv')
        VarStash.df_full.to_csv(full_table_filepath)

        #

        for filename in out_pdbqt_filename_l + log_filename_l:
            shutil.copyfile(os.path.join(run_dir, filename), os.path.join(dir_retFiles, filename))

        # so DataFileUtil doesn't crash over zipping an empty folder
        if len(os.listdir(dir_retFiles)) == 0:
            dprint(rf"touch {os.path.join(dir_retFiles, 'Sorry_no_files_were_generated')}", run='cli')

        dir_retFiles_shockInfo = dir_to_shock(dir_retFiles, 'pdbqt_log.zip', 'Generated .pdbqt and log files, as well as a full .csv')



        # html

        html_shockInfo = dir_to_shock(hb.html_dir, 'index.html', 'HTML report for AutoDock Vina')
            


        ##
        ####
        ###### report
        ####
        ##

        report_params = {
            'warnings': VarStash.warnings,
            'direct_html_link_index': 0,
            'html_links': [html_shockInfo],
            'file_links': [dir_retFiles_shockInfo],
            'report_object_name': 'autodock_vina' + self.suffix,
            'workspace_name': params['workspace_name'],
            }

        kbr = KBaseReport(self.callback_url)
        report_output = kbr.create_extended_report(report_params)

        output = {
            'report_name': report_output['name'],
            'report_ref': report_output['ref'],
        }



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
