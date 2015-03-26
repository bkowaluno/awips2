/**
 * This software was developed and / or modified by Raytheon Company,
 * pursuant to Contract DG133W-05-CQ-1067 with the US Government.
 *
 * U.S. EXPORT CONTROLLED TECHNICAL DATA
 * This software product contains export-restricted data whose
 * export/transfer/disclosure is restricted by U.S. law. Dissemination
 * to non-U.S. persons whether in the United States or abroad requires
 * an export license or other authorization.
 *
 * Contractor Name:        Raytheon Company
 * Contractor Address:     6825 Pine Street, Suite 340
 *                         Mail Stop B8
 *                         Omaha, NE 68106
 *                         402.291.0100
 *
 * See the AWIPS II Master Rights File ("Master Rights File.pdf") for
 * further licensing information.
 **/
package com.raytheon.uf.viz.drawing.polygon;

import org.eclipse.swt.graphics.RGB;
import org.opengis.referencing.crs.CoordinateReferenceSystem;

import com.raytheon.uf.viz.core.DrawableCircle;
import com.raytheon.uf.viz.core.IDisplayPaneContainer;
import com.raytheon.uf.viz.core.IGraphicsTarget;
import com.raytheon.uf.viz.core.IGraphicsTarget.LineStyle;
import com.raytheon.uf.viz.core.drawables.IShadedShape;
import com.raytheon.uf.viz.core.drawables.IWireframeShape;
import com.raytheon.uf.viz.core.drawables.PaintProperties;
import com.raytheon.uf.viz.core.exception.VizException;
import com.raytheon.uf.viz.core.map.MapDescriptor;
import com.raytheon.uf.viz.core.rsc.AbstractResourceData;
import com.raytheon.uf.viz.core.rsc.AbstractVizResource;
import com.raytheon.uf.viz.core.rsc.IResourceDataChanged.ChangeType;
import com.raytheon.uf.viz.core.rsc.LoadProperties;
import com.raytheon.uf.viz.core.rsc.capabilities.ColorableCapability;
import com.raytheon.uf.viz.core.rsc.capabilities.EditableCapability;
import com.raytheon.uf.viz.core.rsc.capabilities.OutlineCapability;
import com.raytheon.viz.ui.input.EditableManager;
import com.vividsolutions.jts.geom.Coordinate;
import com.vividsolutions.jts.geom.LineString;
import com.vividsolutions.jts.geom.LinearRing;
import com.vividsolutions.jts.geom.Polygon;

/**
 * A layer for displaying a filled polygon on a map and altering it through
 * mouse interactions. This layer only supports an exterior ring, ie a polygon
 * without holes/interior rings.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 *
 * Date         Ticket#    Engineer    Description
 * ------------ ---------- ----------- --------------------------
 * Jan 19, 2015  3974      njensen     Initial creation
 * Mar 31, 2015  3977      nabowle     Require non-empty coordinates in resetPolygon
 *
 * </pre>
 *
 * @author njensen
 * @version 1.0
 * @param <T>
 */

public class PolygonLayer<T extends AbstractResourceData> extends
        AbstractVizResource<T, MapDescriptor> {

    protected static final double VERTEX_RADIUS = 7.0;

    protected PolygonInputAdapter uiInput = new PolygonInputAdapter(this);

    /** the polygon as represented in latlon coordinates **/
    protected Polygon polygon;

    protected IWireframeShape wireframeShape;

    protected IShadedShape shadedShape;

    protected Object shapeLock = new Object();

    public PolygonLayer(T resourceData, LoadProperties loadProperties) {
        super(resourceData, loadProperties);
        getCapability(EditableCapability.class).setEditable(true);
        getCapability(OutlineCapability.class).setOutlineWidth(2);
    }

    @Override
    protected void initInternal(IGraphicsTarget target) throws VizException {
        EditableManager.makeEditable(this,
                getCapability(EditableCapability.class).isEditable());
        IDisplayPaneContainer container = getResourceContainer();
        if (container != null) {
            container.registerMouseHandler(uiInput);
        }
    }

    @Override
    protected void paintInternal(IGraphicsTarget target,
            PaintProperties paintProps) throws VizException {
        if (polygon == null) {
            return;
        }

        // prepare to create lines of the polygon
        LinearRing ring = (LinearRing) polygon.getExteriorRing();
        Coordinate[] c = polygon.getCoordinates();
        RGB color = getCapability(ColorableCapability.class).getColor();
        OutlineCapability lineCap = getCapability(OutlineCapability.class);
        float width = lineCap.getOutlineWidth();
        LineStyle style = lineCap.getLineStyle();

        synchronized (shapeLock) {
            if (wireframeShape == null) {
                wireframeShape = target.createWireframeShape(true, descriptor);
            }
            if (shadedShape == null) {
                shadedShape = target.createShadedShape(false,
                        descriptor.getGridGeometry());
            }

            if (!wireframeShape.isDrawable() || !shadedShape.isDrawable()) {
                wireframeShape.addLineSegment(c);
                shadedShape.addPolygon(new LineString[] { ring }, color);
            }

            target.drawWireframeShape(wireframeShape, color, width, style);
            target.drawShadedShape(shadedShape, 0.5f);
        }

        // only show the vertices if in editable mode
        if (getCapability(EditableCapability.class).isEditable()) {
            DrawableCircle[] vertices = new DrawableCircle[c.length - 1];
            double[] origCoord = new double[2];
            double[] pxCoord = new double[2];
            for (int i = 0; i < c.length - 1; i++) {
                DrawableCircle circle = new DrawableCircle();
                origCoord[0] = c[i].x;
                origCoord[1] = c[i].y;
                if (uiInput.draggedVertexIndex == i) {
                    // they're dragging, replace this circle with mouse position
                    pxCoord = descriptor.getRenderableDisplay().screenToGrid(
                            uiInput.lastX, uiInput.lastY, 0, target);
                } else {
                    pxCoord = this.descriptor.worldToPixel(origCoord);
                }
                circle.setCoordinates(pxCoord[0], pxCoord[1]);
                circle.screenRadius = VERTEX_RADIUS;
                circle.basics.color = color;
                circle.filled = true;
                vertices[i] = circle;
            }
            target.drawCircle(vertices);
        }
    }

    @Override
    protected void disposeInternal() {
        IDisplayPaneContainer container = getResourceContainer();
        if (container != null) {
            container.unregisterMouseHandler(uiInput);
        }

        synchronized (shapeLock) {
            if (wireframeShape != null) {
                wireframeShape.dispose();
                wireframeShape = null;
            }
            if (shadedShape != null) {
                shadedShape.dispose();
                shadedShape = null;
            }
        }
    }

    /**
     * Creates a new polygon based on the coordinates and makes that the
     * internal polygon.
     *
     * @param coords
     */
    public void resetPolygon(Coordinate[] coords) {
        synchronized (shapeLock) {
            if (coords != null && coords.length > 0) {
                polygon = PolygonUtil.FACTORY.createPolygon(coords);
            }
            if (wireframeShape != null) {
                wireframeShape.reset();
            }
            if (shadedShape != null) {
                shadedShape.reset();
            }
        }
        issueRefresh();
    }

    @Override
    protected void resourceDataChanged(ChangeType type, Object updateObject) {
        if (type.equals(ChangeType.CAPABILITY)) {
            resetPolygon(null);
        }
    }

    @Override
    public void project(CoordinateReferenceSystem crs) throws VizException {
        synchronized (shapeLock) {
            if (wireframeShape != null) {
                wireframeShape.dispose();
                wireframeShape = null;
            }
            if (shadedShape != null) {
                shadedShape.dispose();
                shadedShape = null;
            }
            resetPolygon(null);
        }
    }

    public Polygon getPolygon() {
        return polygon;
    }

    public void setPolygon(Polygon polygon) {
        resetPolygon(polygon.getExteriorRing().getCoordinates());
    }
}
