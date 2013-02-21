/*
* The following software products were developed by Raytheon:
*
* ADE (AWIPS Development Environment) software
* CAVE (Common AWIPS Visualization Environment) software
* EDEX (Environmental Data Exchange) software
* uFrame™ (Universal Framework) software
*
* Copyright (c) 2010 Raytheon Co.
* All rights reserved. This program and the accompanying materials
* are made available under the terms of the Eclipse Public License v1.0
* which accompanies this distribution, and is available at
* http://www.eclipse.org/org/documents/epl-v10.php
*
*
* Contractor Name: Raytheon Company
* Contractor Address:
* 6825 Pine Street, Suite 340
* Mail Stop B8
* Omaha, NE 68106
* 402.291.0100
*
*
* SOFTWARE HISTORY
*
* Date         Ticket#    Engineer    Description
* ------------ ---------- ----------- --------------------------
* Mar 30, 2012            bclement     Initial creation
*
*/ 
package com.raytheon.uf.edex.wms.styling;

import java.awt.image.BufferedImage;
import java.util.Map;

import org.geotools.data.memory.MemoryFeatureCollection;

import com.raytheon.uf.edex.ogc.common.StyleLookup;
import com.raytheon.uf.edex.wms.WmsException;
import com.raytheon.uf.edex.wms.reg.WmsImage;

/**
 *
 * @author bclement
 * @version 1.0	
 */
public interface IFeatureStyleProvider extends StyleLookup {

	public WmsImage styleData(MemoryFeatureCollection coll, String layer,
			String style, boolean defaultStyle) throws WmsException;

	public BufferedImage getLegend(String layer, String style,
			Map<String, String> dimensions, Map<String, String> levelUnits,
			Integer width, Integer height) throws WmsException;

}
