/*
 * gov.noaa.nws.ncep.ui.pgen.attrDialog.AttrDlg
 * 
 * 20 February 2009
 *
 * This code has been developed by the NCEP/SIB for use in the AWIPS2 system.
 */

package gov.noaa.nws.ncep.ui.pgen.attrDialog;

import java.util.ArrayList;
import java.awt.Color;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.dialogs.IDialogConstants;

import com.raytheon.uf.viz.core.exception.VizException;

import gov.noaa.nws.ncep.ui.pgen.PgenUtil;
import gov.noaa.nws.ncep.ui.pgen.rsc.PgenResource;
import gov.noaa.nws.ncep.ui.pgen.elements.AbstractDrawableComponent;
import gov.noaa.nws.ncep.ui.pgen.elements.DECollection;
import gov.noaa.nws.ncep.ui.pgen.elements.DrawableElement;
import gov.noaa.nws.ncep.ui.pgen.display.IAttribute;
import gov.noaa.nws.ncep.ui.pgen.elements.Jet;
import gov.noaa.nws.ncep.viz.ui.display.NCMapEditor;
import gov.noaa.nws.ncep.ui.pgen.sigmet.*;
import gov.noaa.nws.ncep.ui.pgen.attrDialog.vaaDialog.*;

/**
 * This class is the abstract class that all PGEN attribute dialogs
 * extend from.
 * 
 * <pre>
 * SOFTWARE HISTORY
 * Date       	Ticket#		Engineer	Description
 * ------------	----------	-----------	--------------------------
 * 02/09					B. Yin   	Initial Creation.
 * 04/09        #72      	S. Gilbert  Added IText
 * 04/09        #89      	J. Wu  		Added IArc
 * 05/09        #111     	J. Wu  		Added IVector
 * 05/09		#116		B. Yin		Override open() to set dialog location
 * 07/09        #104        S. Gilbert  Added IAvnText methods
 * 08/09		#135		B. Yin		Modified okPressed method to handle jet barbs
 * 08/09		#149		B. Yin		Modified okPressed method to handle MultiSelect
 * 09/09        #169        Greg Hull   NCMapEditor
 * 01/10		#182		G. Zhang	Added DrawableElement and mousehandlerName for CONVSIGMET
 * 10/10		#?			B. Yin		Changed DrawableElement de to AbstractDrawableComponent
 * 04/11		#?			B. Yin		Re-factor IAttribute
 *
 * </pre>
 * 
 * @author	B. Yin
 */

//public abstract class AttrDlg extends CaveJFACEDialog implements IAttribute {
public abstract class AttrDlg extends Dialog implements IAttribute {
	
	/**
	 * A handler to the current PGEN drawing layer, which is used to
	 * get the selected element.
	 */
	protected PgenResource 	drawingLayer = null;
	
	/**
	 * A handler to the current map editor. The map editor is used to 
	 * redraw the drawing layer when user click on 'OK'.
	 */
	protected NCMapEditor	mapEditor = null;
	protected String pgenCategory = null;
	protected String pgenType = null; 
	protected static final int CHK_WIDTH = 16;
	protected static final int CHK_HEIGHT = 28;
	
	protected static String mouseHandlerName = null;
	protected static AbstractDrawableComponent de = null;
	
	protected Point shellLocation;
	
	/**
	 * AttrDlg constructor
	 * @param parShell
	 * @throws VizException
	 */
	public AttrDlg(Shell parShell) throws VizException {
		
        super(parShell);
        this.setShellStyle(SWT.TITLE | SWT.MODELESS | SWT.CLOSE );
                
	}

	@Override
	public void createButtonsForButtonBar(Composite parent){
		super.createButtonsForButtonBar(parent);
  		this.getButton(IDialogConstants.CANCEL_ID).setEnabled(false);
  		this.getButton(IDialogConstants.OK_ID).setEnabled(false);
	}

	@Override
	public Control createButtonBar(Composite parent){
		
		Control bar = super.createButtonBar(parent);
		GridData gd = new GridData(SWT.CENTER, SWT.DEFAULT, true, false);
		bar.setLayoutData(gd);
		return bar;
		
	}
	
	/*
	 * Called when "X" button on window is clicked.
	 * @see org.eclipse.jface.window.Window#handleShellCloseEvent()
	 */
	@Override
	public void handleShellCloseEvent() {
		super.handleShellCloseEvent();
		PgenUtil.setSelectingMode();
	}
	   
	public abstract void setAttrForDlg(IAttribute ia);

	/**
	 * Sets the PGEN drawing layer
	 * @param dl
	 */
	public void setDrawingLayer( PgenResource dl ){
		
		this.drawingLayer = dl;
		
	}
	
	/**
	 * Sets the map editor
	 * @param me
	 */
	public void setMapEditor( NCMapEditor me ){
		this.mapEditor = me;
	}
	
	/**
	 * Updates the selected element and redraws the PGEN layer.
	 */
	public void okPressed(){

		/*
		 * JetBarb/Jet/Hash/JetText cannot be multi-selected and they are
		 * separated from those that can be multi-selected. 
		 */
		DrawableElement de = drawingLayer.getSelectedDE();
		if ( de != null && 
				( de instanceof Jet.JetBarb || 
						de instanceof Jet.JetHash ||
						de instanceof Jet.JetText ||
						de instanceof Jet.JetLine ) ){

			DrawableElement newEl = (DrawableElement)de.copy();

			//for jet barb, we need replace the whole jet for undo working
			if ( de instanceof Jet.JetBarb ){
				DECollection wind = (DECollection) de.getParent();
				if (  wind != null && wind.getCollectionName().equalsIgnoreCase("WindInfo")){
					DECollection parent = (DECollection) wind.getParent();
					if( parent != null && parent.getCollectionName().equalsIgnoreCase("jet")){
						Jet oldJet = (Jet)parent;
						Jet newJet = oldJet.copy();
						DECollection newWind = wind.copy();
						newJet.replace(newJet.getNearestComponent(((Jet.JetBarb)de).getLocation()), newWind);
						drawingLayer.replaceElement(oldJet, newJet);

						newWind.replace(newWind.getNearestComponent(((Jet.JetBarb)de).getLocation()), newEl);
						if (newEl instanceof Jet.JetBarb ){
							newEl.update(this);
							((Jet.JetBarb) newEl).setSpeed(((Jet.JetBarb)newEl).getSpeed());
						}
					}
				}
			}
			else {
				newEl.update(this);
				drawingLayer.replaceElement(de, newEl);
				
				//reset the jet line attributes
				if ( de instanceof Jet.JetLine){
					AbstractDrawableComponent adc = AttrSettings.getInstance().getSettings().get( "JET" );
					if ( adc instanceof Jet ){
						((Jet)adc).getJetLine().update(this);
					}
        		}
        		
			}
			
			drawingLayer.removeSelected();
			drawingLayer.setSelected(newEl);
		}
		else {

			ArrayList<AbstractDrawableComponent> adcList = null;
			ArrayList<AbstractDrawableComponent> newList = new ArrayList<AbstractDrawableComponent>() ;

			// get the list of selected elements
			if ( drawingLayer != null ) {
				adcList = (ArrayList<AbstractDrawableComponent>) drawingLayer.getAllSelected();
			}

			if ( adcList != null && !adcList.isEmpty() ){
				DrawableElement newEl = null;
				//loop through the list and update attributes
				for ( AbstractDrawableComponent adc : adcList){
										
					DrawableElement el = adc.getPrimaryDE();

					if ( el != null ){

					    // Create a copy of the currently selected element
						newEl = (DrawableElement)el.copy();

						// Update the new Element with these current attributes
						newEl.update(this);
						newList.add(newEl);
					}
				}
				
				if ( newEl != null ){
					AttrSettings.getInstance().setSettings( newEl );
				}
				
				ArrayList<AbstractDrawableComponent> oldList = new ArrayList<AbstractDrawableComponent>(adcList);
				drawingLayer.replaceElements(oldList, newList);
			}

			drawingLayer.removeSelected();

			//set new elements as selected
			for ( AbstractDrawableComponent adc : newList ){
				drawingLayer.addSelected(adc);
			}

		}

		if ( mapEditor != null ) {
			mapEditor.refresh();
		}

	}
	
	/**
	 * Removes ghost line, handle bars, and closes the dialog
	 */
	public void cancelPressed(){
		
		drawingLayer.removeSelected();
		drawingLayer.removeGhostLine();
		super.cancelPressed();
		
	}
	
	/**
	 * Set the location of the dialog
	 */
	public int open(){

		if ( this.getShell() == null ){
			this.create();
		}
		if(shellLocation == null){
	   	    this.getShell().setLocation(this.getShell().getParent().getLocation());
		} else {
			getShell().setLocation(shellLocation);
		}
		
   	    return super.open();
		
	}
	
	/** 
	 * Save location of the dialog.
	 */
	public boolean close() {
		if(getShell() != null){
			Rectangle bounds = getShell().getBounds();
			shellLocation = new Point(bounds.x, bounds.y);
		}
		return super.close();
	}
	
	/**
	 * Enables the 'OK' button and the 'Cancel' button
	 */
	public void enableButtons(){
		
		this.getButton(IDialogConstants.CANCEL_ID).setEnabled(true);
  		this.getButton(IDialogConstants.OK_ID).setEnabled(true);
  		
	}
	
	/**
	 * Sets the Pgen type, which will be used when creating an new
	 * element from the 'Place symbol' button
	 * @param pgenType
	 */
	public void setPgenType( String pgenType ){
		
		this.pgenType = pgenType;
		
	}
	
	/**
	 * Sets the Pgen type, which will be used when creating an new
	 * element from the 'Place symbol' button
	 * @param pgenType
	 */
	public void setPgenCategory( String pgenCategory ){
		
		this.pgenCategory = pgenCategory;
		
	}
	/**
	 *  Common interface for ISinglePoint and IMultiPoint.
	 */
	public Color[] getColors(){
		return null;
	}
	
    public float getLineWidth(){
    	return 1.0f;
    }
    
    public double getSizeScale(){
    	return 1.0;
    }
    
 	public String getType(){
		return null;
	}
 	
 	//to be override by subclasses
 	public void setType(String type){	
 		
 	}

	/**
     * Add a horizontal separator to the display.
     */
    public static void addSeparator(Composite top ) {
        GridData gd = new GridData(GridData.FILL_HORIZONTAL);
        Label sepLbl = new Label(top, SWT.SEPARATOR | SWT.HORIZONTAL);
        sepLbl.setLayoutData(gd);
    }
    
    public void setMouseHandlerName(String name){
    	mouseHandlerName = name;
    }
    
    public void setDrawableElement(AbstractDrawableComponent adc){
    	if ( adc instanceof DrawableElement ){
    		DrawableElement de = (DrawableElement)adc;
    		if("INTL_SIGMET".equals(pgenType)){ 
    			((SigmetAttrDlg)this).setSigmet(de);
    			((SigmetAttrDlg)this).copyEditableAttrToSigmetAttrDlg((Sigmet)de);
    		}else if("VOLC_SIGMET".equals(pgenType)){
    			((VolcanoVaaAttrDlg)this).setVolcano(de);
    		}else if("VACL_SIGMET".equals(pgenType)){ 
    			((VaaCloudDlg)this).setSigmet(de); 
    		} else if("SIGMET".equalsIgnoreCase(pgenCategory)){

    			if("CCFP_SIGMET".equals(pgenType)) {
    				((gov.noaa.nws.ncep.ui.pgen.attrDialog.vaaDialog.CcfpAttrDlg)this).setAbstractSigmet(de); 
    				return;
    			}			

    			((SigmetCommAttrDlg)this).setAbstractSigmet(de);
    			((SigmetCommAttrDlg)this).copyEditableAttrToSigmetAttrDlg((AbstractSigmet)de);
    		} 
    		else {
    			AttrDlg.de = de;
    		}
    	}
    	else {
    		AttrDlg.de = adc;
    	}
    }
    
    public AbstractDrawableComponent getDrawableElement(){
    	return de;
    }

	/**
	 * Set default attributes for the current pgen type.
	 */    
    public void setDefaultAttr(){

           	AbstractDrawableComponent adc = AttrSettings.getInstance().getSettings().get( pgenType );
       	    if ( adc != null ) {
        	    setAttr( adc );
       	    }

    }
    
    /**
	 *	Set dialog attributes with values of adc.
	 */
    public void setAttr( AbstractDrawableComponent adc ){
    	if ( adc instanceof IAttribute ){
    		setAttrForDlg( (IAttribute)adc);
    	}
    }

    /**
     * check if it is in 'add line' mode (for labeled lines)
     * @return
     */
    public boolean isAddLineMode(){
    	return false;
    }
    
    /**
     * reset toggle buttons for labeled line dialog
     */
    public void resetLabeledLineBtns(){
    	
    }
}
