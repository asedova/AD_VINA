import pandas as pd
import numpy as np
import fileinput
import itertools


from .print import *
from .kbase_obj import *



pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 20)



class HTMLBuilder:

    html_template_filepath = '/kb/module/lib/AD_VINA/util/index.html'
    TAG_L = [tag + '_TAG' for tag in ['PROTEIN', 'WARNINGS', 'CMDS', 'JSON', 'COLUMNS']]
    

    def __init__(self, ps: ProteinStructure, cs: CompoundSet, cmd_l: list):

        self.ps = ps
        self.cs = cs
        self.cmd_l = cmd_l
    

        # html dir and file

        self.html_dir = os.path.join(
            VarStash.shared_folder, 
            'html_dir__CompoundSet[' + cs.name + ']_vs_ProteinStructure[' + ps.name + ']_'  + VarStash.suffix
            )
        os.mkdir(self.html_dir)
        self.html_filepath = os.path.join(self.html_dir, os.path.basename(self.html_template_filepath))
        
        shutil.copyfile(self.html_template_filepath, self.html_filepath)


        # html file content

        self._build()


    def _build(self):

        self.replacements = {}

        self._build_protein()
        self._build_cmds()
        self._build_table()
        self._build_warnings()


        for line in fileinput.input(self.html_filepath, inplace=True):
            tag_hit = None
            for tag in self.TAG_L:
                if tag in line and tag in self.replacements:
                    tag_hit = tag
            if tag_hit:
                print(line.replace(tag_hit, self.replacements[tag_hit]), end='')
            else:
                print(line, end='')



    def _build_protein(self):
        self.replacements['PROTEIN_TAG'] = self.ps.name


    def _build_cmds(self):
        if len(self.cmd_l) > 0:
            self.replacements['CMDS_TAG'] = '\n'.join([f"<p><code>{cmd}</code></p>" for cmd in self.cmd_l])
        else:
            self.replacements['CMDS_TAG'] = (
                "<p><i>No <code>vina</code> commands were run. "
                "This could be because no MOL2 files were found in ZINC for any of the compounds, "
                "no MOL2 files successfully converted to PDBQT, "
                "or there are no compounds in the CompoundSet object.</i></p>"
                )



    def _build_table(self):
        """
        (1) Build docking table
        (2) Merge with compound table
        (3) Dump
        """

        col_title_compound = ['(User Entered) Id', '(User Entered) Name', 'Formula', 'SMILES', 'InChIKey', 'Mass (g/mol)', 'Charge (C)', '&Delta;G<sub>f</sub>&deg; (kJ/mol)']
        col_title_dock = ['Mode', 'Affinity (kcal/mol)', 'RMSD L.B.', 'RMSD U.B.']
        

        #-------------------------------------------------------------------------------------------

        ##
        ## docking table

        attr_dock = ['mode', 'affinity', 'rmsd_lb', 'rmsd_ub']

        df_l = []

        for id, log_filepath in zip(self.cs.get_attr_l('id'), self.cs.get_attr_l('log_filepath')):

            if isinstance(log_filepath, float) and np.isnan(log_filepath):
                continue

            df = pd.DataFrame(columns=attr_dock)
            df = self._parse_log(log_filepath, df, id)

            df_l.append(df)


        df_dock = pd.concat(df_l)
        df_dock.index.name = 'id'

        dprint('df_dock', run=locals())
       

        ##
        ## merge compound and docking table

        df = pd.merge(self.cs.df, df_dock, how='left', on='id')

        dprint('df', run=locals())


        ##
        ## save full
        VarStash.df_full = df.copy()


        ##
        ## filter/rename columns

        keep = ['id', 'name', 'formula', 'mass', 'mode', 'affinity', 'rmsd_lb', 'rmsd_ub', 'smiles', 'modelseed_link']
        rename = ['(User Entered) Compound Id', '(User Entered) Name', 'Formula', 'Mass (g/mol)',
                    'Mode', 'Affinity (kcal/mol)', 'RMSD L.B.', 'RMSD U.B.', 'SMILES', 'ModelSEED']
        rename = {old: new for old, new in zip(keep, rename)}

        df = df.reset_index()[keep].rename(columns=rename)


        dprint('df', run=locals())


        ##
        ## dump to html

        self.replacements['JSON_TAG'] = df.to_json(orient='values').replace('null', '"-"')
        self.replacements['COLUMNS_TAG'] = json.dumps([{'title': column} for column in df.columns])





    @staticmethod
    def _parse_log(log_filepath, df, id):
        #TODO 0 modes -> same log format?
        parsing = False
        with open(log_filepath) as f:
            for i, line in enumerate(f):
                if parsing:
                    if line.startswith("Writing output ... done."):
                        parsing = False
                        end = i
                    else:
                        mode = line[:4].strip()
                        affinity = line[4:17].strip()
                        rmsd_lb = line[17:28].strip()
                        rmsd_ub = line[28:].strip()
                        df.loc[len(df)] = [mode, affinity, rmsd_lb, rmsd_ub]
                elif line.startswith("-----+------------+----------+----------"):
                    start = i
                    parsing = True
                elif line.startswith("Using random seed: "):
                    seed = line[19:-1]
                 
        if end == start + i:
            VarStash.warnings.append("Compound id: [{id}] did not generate any modes") # probably never going to happen

        df.set_index(itertools.repeat(id, len(df)), inplace=True)
        df['seed'] = [seed] * len(df)

        return df



    def _build_warnings(self):
        if len(VarStash.warnings) > 0:
            self.replacements['WARNINGS_TAG'] = '\n'.join([f"<p><code>{warning}</code></p>" for warning in VarStash.warnings])
        else:
            self.replacements['WARNINGS_TAG'] = '<p><i>No warnings about missing MOL2 files</i></p>'
