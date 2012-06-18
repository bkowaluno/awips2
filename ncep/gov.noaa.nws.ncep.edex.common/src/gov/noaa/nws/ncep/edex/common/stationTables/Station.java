//
// This file was generated by the JavaTM Architecture for XML Binding(JAXB) Reference Implementation, vJAXB 2.1.3 in JDK 1.6 
// See <a href="http://java.sun.com/xml/jaxb">http://java.sun.com/xml/jaxb</a> 
// Any modifications to this file will be lost upon recompilation of the source schema. 
// Generated on: 2009.06.08 at 02:36:43 PM EDT 
//


package gov.noaa.nws.ncep.edex.common.stationTables;

import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlRootElement;
import javax.xml.bind.annotation.XmlType;


/**
 * <p>Java class for anonymous complex type.
 * 
 * <p>The following schema fragment specifies the expected content contained within this class.
 * 
 * <pre>
 * &lt;complexType>
 *   &lt;complexContent>
 *     &lt;restriction base="{http://www.w3.org/2001/XMLSchema}anyType">
 *       &lt;sequence>
 *         &lt;element ref="{}stid" minOccurs="0"/>
 *         &lt;element ref="{}stnnum" minOccurs="0"/>
 *         &lt;element ref="{}stnname" minOccurs="0"/>
 *         &lt;element ref="{}state" minOccurs="0"/>
 *         &lt;element ref="{}country" minOccurs="0"/>
 *         &lt;element ref="{}latitude" minOccurs="0"/>
 *         &lt;element ref="{}longitude" minOccurs="0"/>
 *         &lt;element ref="{}elevation" minOccurs="0"/>
 *         &lt;element ref="{}priority" minOccurs="0"/>
 *         &lt;element ref="{}location" minOccurs="0"/>
 *         &lt;element ref="{}wfo" minOccurs="0"/>
 *       &lt;/sequence>
 *     &lt;/restriction>
 *   &lt;/complexContent>
 * &lt;/complexType>
 * </pre>
 * 
 * 
 */
@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "", propOrder = {
    "stid",
    "stnnum",
    "stnname",
    "state",
    "country",
    "latitude",
    "longitude",
    "elevation",
    "priority",
    "location",
    "wfo"
})
@XmlRootElement(name = "station")
public class Station {

    protected String stid;
    protected String stnnum;
    protected String stnname;
    protected String state;
    protected String country;
    protected Float latitude;
    protected Float longitude;
    protected Integer elevation;
    protected Integer priority;
    protected String location;
    protected String wfo;

    /**
     * Gets the value of the stid property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getStid() {
        return stid;
    }

    /**
     * Sets the value of the stid property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setStid(String value) {
        this.stid = value;
    }

    /**
     * Gets the value of the stnnum property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getStnnum() {
        return stnnum;
    }

    /**
     * Sets the value of the stnnum property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setStnnum(String value) {
        this.stnnum = value;
    }

    /**
     * Gets the value of the stnname property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getStnname() {
        return stnname;
    }

    /**
     * Sets the value of the stnname property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setStnname(String value) {
        this.stnname = value;
    }

    /**
     * Gets the value of the state property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getState() {
        return state;
    }

    /**
     * Sets the value of the state property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setState(String value) {
        this.state = value;
    }

    /**
     * Gets the value of the country property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getCountry() {
        return country;
    }

    /**
     * Sets the value of the country property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setCountry(String value) {
        this.country = value;
    }

    /**
     * Gets the value of the latitude property.
     * 
     * @return
     *     possible object is
     *     {@link Float }
     *     
     */
    public Float getLatitude() {
        return latitude;
    }

    /**
     * Sets the value of the latitude property.
     * 
     * @param value
     *     allowed object is
     *     {@link Float }
     *     
     */
    public void setLatitude(Float value) {
        this.latitude = value;
    }

    /**
     * Gets the value of the longitude property.
     * 
     * @return
     *     possible object is
     *     {@link Float }
     *     
     */
    public Float getLongitude() {
        return longitude;
    }

    /**
     * Sets the value of the longitude property.
     * 
     * @param value
     *     allowed object is
     *     {@link Float }
     *     
     */
    public void setLongitude(Float value) {
        this.longitude = value;
    }

    /**
     * Gets the value of the elevation property.
     * 
     * @return
     *     possible object is
     *     {@link Integer }
     *     
     */
    public Integer getElevation() {
        return elevation;
    }

    /**
     * Sets the value of the elevation property.
     * 
     * @param value
     *     allowed object is
     *     {@link Integer }
     *     
     */
    public void setElevation(Integer value) {
        this.elevation = value;
    }

    /**
     * Gets the value of the priority property.
     * 
     * @return
     *     possible object is
     *     {@link Integer }
     *     
     */
    public Integer getPriority() {
        return priority;
    }

    /**
     * Sets the value of the priority property.
     * 
     * @param value
     *     allowed object is
     *     {@link Integer }
     *     
     */
    public void setPriority(Integer value) {
        this.priority = value;
    }

    /**
     * Gets the value of the location property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getLocation() {
        return location;
    }

    /**
     * Sets the value of the location property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setLocation(String value) {
        this.location = value;
    }

    /**
     * Gets the value of the wfo property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getWfo() {
        return wfo;
    }

    /**
     * Sets the value of the wfo property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setWfo(String value) {
        this.wfo = value;
    }

}
