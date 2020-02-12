/*
A KBase module: AD_VINA
*/

module AD_VINA {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef ad_vina(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
