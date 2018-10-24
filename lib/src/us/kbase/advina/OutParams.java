
package us.kbase.advina;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: OutParams</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "outname"
})
public class OutParams {

    @JsonProperty("outname")
    private String outname;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("outname")
    public String getOutname() {
        return outname;
    }

    @JsonProperty("outname")
    public void setOutname(String outname) {
        this.outname = outname;
    }

    public OutParams withOutname(String outname) {
        this.outname = outname;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((("OutParams"+" [outname=")+ outname)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
