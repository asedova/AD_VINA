/*
A KBase module: AD_VINA
*/

module AD_VINA {
    typedef structure{
	string receptor;
	string ligand;
        string center;
	string size;
        string outname;
        string workspace;
    }InParams;

    typedef structure{
        string report_name;
	string report_ref;
    }OutParams;
    funcdef ad_vina(InParams inparams)
        returns (OutParams output) authentication required;
};
