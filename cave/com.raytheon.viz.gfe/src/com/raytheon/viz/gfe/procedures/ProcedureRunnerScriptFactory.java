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
package com.raytheon.viz.gfe.procedures;

import jep.JepException;

import com.raytheon.viz.gfe.core.DataManager;

/**
 * Script factory for {@code ProcedureRunnerController} instances.
 * 
 * <pre>
 * 
 * SOFTWARE HISTORY
 * 
 * Date         Ticket#    Engineer    Description
 * ------------ ---------- ----------- --------------------------
 * Jul 25, 2015  #4263     dgilling     Initial creation
 * 
 * </pre>
 * 
 * @author dgilling
 * @version 1.0
 */

public final class ProcedureRunnerScriptFactory extends
        ProcedureFactory<ProcedureRunnerController> {

    /*
     * These constants that are passed to the super constructor only matter if
     * procedure execution gets hooked into our python concurrent execution
     * framework. Since it isn't we use dummy values for now...
     */
    private static final String SCRIPT_EXECUTOR_NAME = "procedure-runner";

    private static final int EXECUTOR_NUM_THREADS = 0;

    public ProcedureRunnerScriptFactory(final DataManager dataMgr) {
        super(SCRIPT_EXECUTOR_NAME, EXECUTOR_NUM_THREADS, dataMgr);
    }

    /*
     * (non-Javadoc)
     * 
     * @see
     * com.raytheon.uf.common.python.concurrent.AbstractPythonScriptFactory#
     * createPythonScript()
     */
    @Override
    public ProcedureRunnerController createPythonScript() throws JepException {
        return new ProcedureRunnerController(buildScriptPath(),
                buildIncludePath(), getClass().getClassLoader(), dataMgr);
    }
}
