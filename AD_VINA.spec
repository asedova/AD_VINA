/*
A KBase module: AD_VINA
*/

module AD_VINA {
    typedef structure{
        string report_name;
	string report_ref;
    }OutParams;

    funcdef ad_vina(mapping<string,UnspecifiedObject> params)
        returns (OutParams output) authentication required;
};
