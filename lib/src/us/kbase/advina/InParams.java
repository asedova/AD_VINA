
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
 * <p>Original spec-file type: InParams</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "receptor",
    "ligand",
    "center",
    "size"
})
public class InParams {

    @JsonProperty("receptor")
    private String receptor;
    @JsonProperty("ligand")
    private String ligand;
    @JsonProperty("center")
    private String center;
    @JsonProperty("size")
    private String size;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("receptor")
    public String getReceptor() {
        return receptor;
    }

    @JsonProperty("receptor")
    public void setReceptor(String receptor) {
        this.receptor = receptor;
    }

    public InParams withReceptor(String receptor) {
        this.receptor = receptor;
        return this;
    }

    @JsonProperty("ligand")
    public String getLigand() {
        return ligand;
    }

    @JsonProperty("ligand")
    public void setLigand(String ligand) {
        this.ligand = ligand;
    }

    public InParams withLigand(String ligand) {
        this.ligand = ligand;
        return this;
    }

    @JsonProperty("center")
    public String getCenter() {
        return center;
    }

    @JsonProperty("center")
    public void setCenter(String center) {
        this.center = center;
    }

    public InParams withCenter(String center) {
        this.center = center;
        return this;
    }

    @JsonProperty("size")
    public String getSize() {
        return size;
    }

    @JsonProperty("size")
    public void setSize(String size) {
        this.size = size;
    }

    public InParams withSize(String size) {
        this.size = size;
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
        return ((((((((((("InParams"+" [receptor=")+ receptor)+", ligand=")+ ligand)+", center=")+ center)+", size=")+ size)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
