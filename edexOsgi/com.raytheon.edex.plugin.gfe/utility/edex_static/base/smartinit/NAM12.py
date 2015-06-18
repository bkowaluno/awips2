##
# This software was developed and / or modified by Raytheon Company,
# pursuant to Contract DG133W-05-CQ-1067 with the US Government.
# 
# U.S. EXPORT CONTROLLED TECHNICAL DATA
# This software product contains export-restricted data whose
# export/transfer/disclosure is restricted by U.S. law. Dissemination
# to non-U.S. persons whether in the United States or abroad requires
# an export license or other authorization.
# 
# Contractor Name:        Raytheon Company
# Contractor Address:     6825 Pine Street, Suite 340
#                         Mail Stop B8
#                         Omaha, NE 68106
#                         402.291.0100
# 
# See the AWIPS II Master Rights File ("Master Rights File.pdf") for
# further licensing information.
##
#
#  NAM12 SmartInit
#
#  Comments below for each algorithm.
#
#  Author: Tim Barker - SOO Boise, ID
#
#=============================================================================
#
#  C O N F I G U R A T I O N   S E C T I O N
#
#=============================================================================
#
#  USE_WETBULB=1 (Yes) or 0 (No).  Using wetbulb for calculating snow level
#  and precipitation type is probably more accurate - since it would be the
#  temperature that the atmosphere would be if you evaporated water into it
#  until saturation.  Thus...when the model is dry at low layers and you think
#  it might precip...then the temperature would likely be much cooler than what
#  the model says. However...the wetbulb calculation is VERY slow and you can
#  save yourself a lot of time by not doing it.  You could argue that if the
#  model isn't making precip - then you shouldn't be changing its temps, but
#  it really seesm to work well in areas of terrain and 'showery' precip -
#  where the model sounding is representative of the large-scale, but inside
#  the showers it is cooler.
#
#     SOFTWARE HISTORY
#    
#    Date            Ticket#       Engineer       Description
#    ------------    ----------    -----------    --------------------------
#    02/16/12        14439         jdynina        modified Haines calculation
#    03/04/13        15585         jzeng          Modified wxtype range in calcWx()
# 
##
USE_WETBULB = 1
#
#
#============================================================================
#
#  E N D   C O N F I G U R A T I O N  S E C T I O N
#
#============================================================================
from Init import *
class NAM12Forecaster(Forecaster):
    def __init__(self):
        Forecaster.__init__(self, "NAM12", "NAM12")
        self.BLcubeTime = (None, None)

    def levels(self):
        return ["MB1000", "MB975", "MB950", "MB925",
                 "MB900", "MB875", "MB850", "MB825",
                 "MB800", "MB775", "MB750", "MB725",
                 "MB700", "MB675", "MB650", "MB625",
                 "MB600", "MB575", "MB550", "MB525",
                 "MB500", "MB450", "MB400", "MB350"]

    #---------------------------------------------------------------------------
    # T - use model sounding to get temperature at real topography instead of
    #     model topography
    #
    # Where the topo is above the model topo - use the boundary
    #    layer temperature to interpolate a temperature...but in radiational
    #    inversions this is typically too warm because the free air
    #    temperature from the model is warmer than air near the ground on
    #    a mountain that sticks up higher than the model mountains.  So...
    #    if there is an inversion (i.e. the boundary layer temp at the
    #    desired height is warmer than the model surface temp) it only goes
    #    1/2 as warm as the raw inversion in the free model atmosphere would
    #    be.  Not sure if this is good for strong and persistent inversions
    #    like marine inversions - but works well for persistent radiational
    #    inversions in the intermountain west during the winter - and works
    #    well for nocturnal inversions all times of the year.
    # Where the topo is below the model topo - it uses the lapse rate between
    #    the two lowest boundary layer levels and extrapolates this downward -
    #    with the restriction that the lapse rate cannot be more than dry
    #    adiabatic and inversions are extrapolated at only 1/2 that lapse rate
    #    and also limited to no more than 1.5C decrease per km.  The 1.5C per km
    #    restriction is arbirary - further research may restrict it more or
    #    less.  The dry adiabatic restriction seems to work fine.
    #--------------------------------------------------------------------------
    def calcT(self, t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120, t_BL120150,
      rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120, rh_BL120150,
      wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090, wind_BL90120,
      wind_BL120150, p_SFC, stopo, topo, gh_c, t_c, rh_c, wind_c, ctime):

        self.setupBLCube(t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
          t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
          rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
          wind_BL90120, wind_BL120150, p_SFC, stopo, gh_c, t_c, rh_c,
          wind_c, ctime)

        BLT = self.BLT
        #self.printval("temp:",self.BLT,65,65)
        BLH = self.BLH

        st = (stopo * 0.0) - 1.0
        for i in range(1, BLH.shape[0]):
           tval = self.linear(BLH[i], BLH[i - 1], BLT[i], BLT[i - 1], topo)
           #
           # restrict the increase in areas where inversions present
           #
           tval=where(greater(tval,BLT[0]),BLT[0]+((tval-BLT[0])/2.0),tval)
           between = logical_and(greater_equal(topo, BLH[i - 1]), less(topo, BLH[i]))
           st=where(logical_and(less(st,0.0),between),tval,st)
        #
        #  restrict the lapse rates below the model surface
        #
        lapse = (BLT[1] - BLT[0]) / (BLH[1] - BLH[0])
        lapse=where(greater(lapse,0.0),lapse/2.0,lapse)
        maxinvert = 1.5 / 1000.0
        lapse=where(greater(lapse,maxinvert),maxinvert,lapse)
        drylapse = -9.8 / 1000.0
        lapse=where(less(lapse,drylapse),drylapse,lapse)
        tst = BLT[0] + ((topo - stopo) * lapse)
        st=where(less(st,0.0),tst,st)
        #
        #diff=t_FHAG2-st
        #maxdiff=maximum.reduce(maximum.reduce(diff))
        #mindiff=minimum.reduce(minimum.reduce(diff))
        #print "max/min temp change: %6.2f %6.2f"%(maxdiff,mindiff)
        #
        #  change to Fahrenheit
        #
        return self.KtoF(st)

    #--------------------------------------------------------------------------
    # Td - where topo is above the model topo - it interpolates the dewpoint
    #      from the model sounding.  This allows mountains sticking up into dry
    #      dry air during nighttime inversions to reflect the dry air aloft.
    #      Where the topo is below the model topo - it uses the model surface
    #      mixing ratio, and assumes that is constant to the real topo - and
    #      uses the temperature at the real topo calculated in calcT
    #---------------------------------------------------------------------------
    def calcTd(self, t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
      t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
      rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
      wind_BL90120, wind_BL120150, p_SFC, T, stopo, topo, gh_c, t_c,
      rh_c, wind_c, ctime):

        self.setupBLCube(t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
          t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
          rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
          wind_BL90120, wind_BL120150, p_SFC, stopo, gh_c, t_c, rh_c,
          wind_c, ctime)
        BLD = self.BLD
        BLH = self.BLH
        #
        #  for real topo above model topo - interpolate dewpoint from the
        #  model dewpoint sounding
        #
        sd = (stopo * 0.0) - 1.0
        for i in range(1, BLH.shape[0]):
           dval = self.linear(BLH[i], BLH[i - 1], BLD[i], BLD[i - 1], topo)
           between = logical_and(greater_equal(topo, BLH[i - 1]), less(topo, BLH[i]))
           sd=where(logical_and(less(sd,0.0),between),dval,sd)

        #
        #  for real topo below model topo - use model surface mixing ratio
        #  and use that mixing ratio with the surface temperature which
        #  was derived from the low-level lapse rate.
        #
        sfce = rh_FHAG2 / 100 * self.esat(t_FHAG2)
        w = (0.622 * sfce) / ((p_SFC + 0.0001) / 100 - sfce)
        tsfce = self.esat(self.FtoK(T))
        dpdz = 287.04 * t_FHAG2 / (p_SFC / 100 * 9.8) # meters / millibar
        newp = p_SFC / 100 + (stopo - topo) / dpdz
        ws = (0.622 * tsfce) / (newp - tsfce)
        rh = w / ws
        tsfcesat = rh * tsfce
        tsfcesat = clip(tsfcesat, 0.00001, tsfcesat)
        b = 26.66082 - log(tsfcesat)
        td = (b - sqrt(b * b - 223.1986)) / 0.0182758048
        sd=where(less(sd,0.0),td,sd)
        #
        #  change to Fahrenheit and make sure it is less than temp
        #
        td = self.KtoF(sd)
        td=where(greater(td,T),T,td)

        return td

    #-------------------------------------------------------------------------
    #  RH - simply calculate RH based on Temp and Dewpoint (both in degrees F)
    #-------------------------------------------------------------------------
    def calcRH(self, T, Td):
        Tc = .556 * (T - 32.0)
        Tdc = .556 * (Td - 32.0)
        Vt = 6.11 * pow(10, (Tc * 7.5 / (Tc + 237.3)))
        Vd = 6.11 * pow(10, (Tdc * 7.5 / (Tdc + 237.3)))
        RH = (Vd / Vt) * 100.0
        return RH

    def dewFromTandRH(self, T, RH):
        tc = (T - 32.0) * (5.0 / 9.0)
        rh = clip(RH, 0.001, 99.999) / 100.0
        x = (log(rh) / 17.67) + (tc / (tc + 243.5))
        tdc = (243.5 * x) / (1.0 - x)
        td = (tdc * 9.0 / 5.0) + 32.0
        return td

    #--------------------------------------------------------------------------
    #  Wx - uses a derivation of the Bourgouin algorithm to determin
    #   precip type.
    #
    #   Uses a sounding of wetbulb temperature (the temperature that it would
    #   be in the model sounding if precip were falling) and finds areas above
    #   and below freezing and figures precip phase based on empirical values.
    #
    #   Makes a simple guess at where it will be showers based on the model LI
    #    - making it showers when LI is less than 2.
    #
    #   Makes a simple guess at where there will be thunderstorms based on the
    #   model LI less than -1 (SChc), <-3 (Chc), <-5 (Lkly), <-8 (Def).
    #
    #   After determining precip type, it matches the probability part of the Wx
    #   grid to the existing PoP grid, removing Wx where the PoP grid is below
    #   15%.  Would love to only calculate the Wx Type here - and not have the
    #   PoP involved - but this is not the way most people understand it.
    #--------------------------------------------------------------------------
    def calcWx(self, t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
      t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
      rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
      wind_BL90120, wind_BL120150, p_SFC, PoP, T, RH, bli_BL0180, stopo,
      topo, gh_c, t_c, rh_c, wind_c, ctime):

        self.setupBLCube(t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
          t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
          rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
          wind_BL90120, wind_BL120150, p_SFC, stopo, gh_c, t_c, rh_c,
          wind_c, ctime)
        BLH = self.BLH
        #
        #  use temp or wetbulb
        #
        if USE_WETBULB == 1:
           TT = self.BLE
        else:
           TT = self.BLT
        #
        #  get temperatures (or wetbulb) at levels above the real topo
        #  not model topo
        #
        (BLH, TT) = self.getTopoE(topo, stopo, p_SFC, T, RH, BLH, TT)
        #
        #  calculate number of zero crossings, and areas above/below
        #  freezing of the wetbulb sounding
        #
        a1 = zeros(topo.shape)
        a2 = zeros(topo.shape)
        a3 = zeros(topo.shape)
        aindex = zeros(topo.shape)
        for i in xrange(1, BLH.shape[0]):
            a11, a22, cross = self.getAreas(BLH[i - 1], TT[i - 1], BLH[i], TT[i])
            topomask = greater(BLH[i], topo)
            a1 = where(logical_and(equal(aindex, 0), topomask),
                       a1 + a11, a1)
            a2 = where(logical_and(equal(aindex, 1), topomask),
                       a2 + a11, a2)
            a3 = where(logical_and(equal(aindex, 2), topomask),
                       a3 + a11, a3)
            topomask = logical_and(topomask, cross)
            aindex = where(topomask, aindex + 1, aindex)
            a1 = where(logical_and(equal(aindex, 0), topomask),
                       a1 + a22, a1)
            a2 = where(logical_and(equal(aindex, 1), topomask),
                       a2 + a22, a2)
            a3 = where(logical_and(equal(aindex, 2), topomask),
                       a3 + a22, a3)
        #
        #  The basic types we are choosing between
        #
        wxtypes = ['<NoCov>:<NoWx>:<NoInten>:<NoVis>:',
               "Def:S:-:<NoVis>:",
               "Def:R:-:<NoVis>:",
               "Def:S:-:<NoVis>:^Def:R:-:<NoVis>:",
               'Def:ZR:-:<NoVis>:',
               'Def:IP:-:<NoVis>:',
               'Def:ZR:-:<NoVis>:^Def:IP:-:<NoVis>:',
               "Def:SW:-:<NoVis>:",
               "Def:RW:-:<NoVis>:",
               "Def:SW:-:<NoVis>:^Def:RW:-:<NoVis>:",
               "Def:ZR:-:<NoVis>:",
               'Def:IP:-:<NoVis>:',
               'Def:ZR:-:<NoVis>:^Def:IP:-:<NoVis>:']

        #
        # Case d - no zero crossings.  All snow or all rain
        #
        snowmask = equal(aindex, 0)
        wx = where(logical_and(snowmask, greater(a1, 0)), 2, 0)
#        wx = where(logical_and(snowmask, less_equal(a1, 0)), 1, wx)
        wx[logical_and(snowmask, less_equal(a1, 0))] = 1
        #
        # Case c - one crossing. Snow if little area above freezing.
        #                        Rain if lots of area above freezing.
        #                        Mix if between
        #
        srmask = equal(aindex, 1)
#        wx = where(logical_and(srmask, less(a1, 5.6)), 1, wx)
#        wx = where(logical_and(srmask, greater(a1, 13.2)), 2, wx)
#        wx = where(logical_and(srmask,
#                               logical_and(greater_equal(a1, 5.6),
#                                           less(a1, 13.2))), 3, wx)
        wx[logical_and(srmask, less(a1, 5.6))] = 1
        wx[logical_and(srmask, greater(a1, 13.2))] = 2
        wx[logical_and(srmask,
                               logical_and(greater_equal(a1, 5.6),
                                           less(a1, 13.2)))] = 3

        #
        # Case a - two crossings. Either freezing rain or ice pellets
        #                         ice pellets when surface cold area is big
        #                         freezing rain when surface cold area is small
        #                         mix when between
        #
        ipmask = equal(aindex, 2)
        ipm = greater(a1, a2 * 0.66 + 66)
#        wx = where(logical_and(ipmask, ipm), 5, wx)
        wx[logical_and(ipmask, ipm)] = 5
        zrm = less(a1, a2 * 0.66 + 46)
#        wx = where(logical_and(ipmask, zrm), 4, wx)
        wx[logical_and(ipmask, zrm)] = 4
        zrm = logical_not(zrm)
        ipm = logical_not(ipm)
#        wx = where(logical_and(ipmask, logical_and(zrm, ipm)), 6, wx)
        wx[logical_and(ipmask, logical_and(zrm, ipm))] = 6
        #
        # Case b - three crossings. If not much in the top warm layer
        #                           then it acts like case c.
        #                           If enough to melt in that layer - then
        #                           see if cold layer is enough to re-freeze
        #                           and be ice pellets - or just remain rain.
        #
        cmask = greater_equal(aindex, 3)
        ipmask = logical_and(less(a3, 2), cmask)
#        wx = where(logical_and(ipmask, less(a1, 5.6)), 1, wx)
#        wx = where(logical_and(ipmask, greater(a1, 13.2)), 2, wx)
#        wx = where(logical_and(ipmask, logical_and(greater_equal(a1, 5.6),
#                                                   less_equal(a1, 13.2))),
#                   3, wx)

        wx[logical_and(ipmask, less(a1, 5.6))] = 1
        wx[logical_and(ipmask, greater(a1, 13.2))] = 2
        wx[logical_and(ipmask, logical_and(greater_equal(a1, 5.6),
                                                   less_equal(a1, 13.2)))] = 3

        ipmask = logical_and(greater_equal(a3, 2), cmask)
#        wx = where(logical_and(ipmask, greater(a1, 66 + 0.66 * a2)), 5, wx)
#        wx = where(logical_and(ipmask, less(a1, 46 + 0.66 * a2)), 4, wx)
#        wx = where(logical_and(ipmask,
#                               logical_and(greater_equal(a1, 46 + 0.66 * a2),
#                                           less_equal(a1, 66 + 0.66 * a2))),
#                   6, wx)
        wx[logical_and(ipmask, greater(a1, 66 + 0.66 * a2))] = 5
        wx[logical_and(ipmask, less(a1, 46 + 0.66 * a2))] = 4
        wx[logical_and(ipmask, logical_and(greater_equal(a1, 5.6),
                                                   less_equal(a1, 13.2)))] = 6
        #
        #  Where LI<2, make showers
        #
        bli_BL0180 = where(less(bli_BL0180, -18.0), 10.0, bli_BL0180)
        convecMask = less(bli_BL0180, 2)
        wx[convecMask] += 6
        #
        #  off the grid need no weather
        #
        wxgrid = zeros(self._empty.shape, dtype=byte)
        keys = ['<NoCov>:<NoWx>:<NoInten>:<NoVis>:', ]
#        wxgrid=where(less(bli_BL0180,-18.0),0,wxgrid)
        wxgrid[less(bli_BL0180, -18.0)] = 0
        #
        #  Match PoP, and remove non-occurring wx
        #
        poplimits = [15.0, 25.0, 55.0, 75.0, 101.0]
        popprobs = ["None", "SChc", "Chc", "Lkly", "Def"]
        for popcat in range(5):
           if popcat > 0:
              lowlimit = poplimits[popcat - 1]
           else:
              lowlimit = -1
           ispopcat = logical_and(greater(PoP, lowlimit),
             less(PoP, poplimits[popcat]))
           #
           #  If this pop category doesn't exist anywhere - then
           #  we don't have to worry about it.
           #
           some = logical_or.reduce(logical_or.reduce(ispopcat))
           if not some:
               continue
           #
           #  the no-pop case is easy - make it no weather
           #
           if popcat == 0:
#              wxgrid=where(ispopcat,0,wxgrid)
              wxgrid[ispopcat] = 0
              continue
           #
           #  for all others...see if any weather combinations exist
           #  and add those
           #
           prob = popprobs[popcat]
           for iwx in range(1, 13):
               wxstring = wxtypes[iwx]
               ispopwx = logical_and(ispopcat, equal(wx, iwx))
               some = logical_or.reduce(logical_or.reduce(ispopwx))
               if not some:
                  continue
               types = []
               types = string.split(wxstring, "^")
               for i in range(len(types)):
                   type = types[i]
                   pieces = string.split(type, ":")
                   pieces[0] = prob
                   types[i] = string.join(pieces, ":")
               wxstring = string.join(types, "^")
               keys.append(wxstring)
               keynum = len(keys) - 1
#               wxgrid=where(ispopwx,keynum,wxgrid)
               wxgrid[ispopwx] = keynum
        #
        # thunder is totally separate from PoP, only related to
        # the instability. SChc  for LI <-1, Chc for LI<-3,
        # Lkly for LI<-5, Def for LI<-8
        #
        thunder = where(less_equal(bli_BL0180, -1), 1, 0)
#        thunder=where(less_equal(bli_BL0180,-3),2,thunder)
#        thunder=where(less_equal(bli_BL0180,-5),3,thunder)
#        thunder=where(less_equal(bli_BL0180,-8),4,thunder)
        thunder[less_equal(bli_BL0180, -3)] = 2
        thunder[less_equal(bli_BL0180, -5)] = 3
        thunder[less_equal(bli_BL0180, -8)] = 4

        tprobs = ["None", "SChc", "Chc", "Lkly", "Def"]
        for ith in range(1, 5):
           tprob = equal(thunder, ith)
           some = logical_or.reduce(logical_or.reduce(tprob))
           if not some:
              continue
           needadd = where(tprob, wxgrid, 0)
           numkeys = len(keys)
           for i in range(1, numkeys):
              add = equal(needadd, i)
              some = logical_or.reduce(logical_or.reduce(add))
              if not some:
                 continue
              wxstring = keys[i]
              addstring = wxstring + "^" + tprobs[ith] + ":T:<NoInten>:<NoVis>:"
#              print "added thunder:",addstring
              keys.append(addstring)
              keynum = len(keys) - 1
#              wxgrid=where(add,keynum,wxgrid)
              wxgrid[add] = keynum
        return(wxgrid, keys)

    #--------------------------------------------------------------------------
    # QPF - simply take model QPF and change units to inches
    #---------------------------------------- ----------------------------------
    def calcQPF(self, tp_SFC):
        qpf = tp_SFC / 25.4   # convert from millimeters to inches
        return qpf

    #--------------------------------------------------------------------------
    # PoP - based strongly on QPF (since when model has one inch of precip the
    #   chance of getting 0.01 is pretty high).  However, there is a big
    #   difference between a place that model has 0.00 precip and is very
    #   close to precipitating - and those where model has 0.00 and is a
    #   thousand miles from the nearest cloud.  Thus, uses the average
    #   boundary layer RH to make an adjustment on the low end - adding
    #   to PoP where RH is high.  Ignores surface RH to try to ignore fog
    #   cases. Would also like to consider omega.
    #
    #   Uses hyperbolic tangent of QPF, so that it rises quickly as model
    #   QPF increases - but tapers out to nearly 100% as QPF gets high.
    #   Also uses hyperbolic tangent of QPF to reduce the impact of high RH
    #   as QPF gets higher (since avg RH will always be high when QPF is high)
    #
    #   Adjustable parameters:
    #     topQPF is QPF amount that would give 75% PoP if nothing else
    #       considered at half this amount, PoP is 45%, at double this
    #       amount PoP is 96%.  Default set at 0.40.
    #     RHexcess is amount of average BL RH above which PoP is adjusted
    #       upward. Default set to 60%
    #     adjAmount is maximum amount of adjustment if BL RH is
    #       totally saturated. Default set to 30%
    #
    #--------------------------------------------------------------------------
    def calcPoP(self, t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
      t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
      rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
      wind_BL90120, wind_BL120150, p_SFC, QPF, stopo, topo, gh_c, t_c,
      rh_c, wind_c, ctime):

        self.setupBLCube(t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
          t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
          rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
          wind_BL90120, wind_BL120150, p_SFC, stopo, gh_c, t_c, rh_c,
          wind_c, ctime)
        BLR = self.BLR

        topQPF = 0.40    # QPF value where raw PoP would be 75%
        RHexcess = 60.0  # RH above this can add to PoP and below will subtract
        adjAmount = 30.0 # amount of adjustment allowed
        #
        factor = tanh(QPF * (1.0 / topQPF))
        factor2 = tanh(QPF * (2.0 / topQPF))
        #
        #
        #
        rhcube = BLR[1:5]
        rhavg = add.reduce(rhcube) / 4.0
        rhmax = 100 - RHexcess
        dpop = rhavg - RHexcess
        dpop[less(dpop, 0.0)] = 0.0
        dpop = (dpop / rhmax) * (1.0 - factor2) * adjAmount
        #
        pop = (factor * 100.0) + dpop
        pop = clip(pop, 0, 100)
        #
        return pop

    #--------------------------------------------------------------------------
    #  Chance of Wetting Rain (0.1 inch).  Same algorithm as PoP, but requires
    #       more model QPF to get same chances, and higher boundary layer RH
    #       to get the adjustment (and maximum adjustment is less).
    #
    #       Adjustable parameters:
    #          topQPF should be higher than PoP topQPF
    #                 Default set at 0.60.
    #          RHexcess should be higher than PoP RHexcess
    #                 Default set to 80%
    #          adjAmount should be smaller than PoP adjAmount
    #                 Default set to 10%
    #
    #--------------------------------------------------------------------------
    def calcCWR(self, t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
      t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
      rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
      wind_BL90120, wind_BL120150, p_SFC, PoP, QPF, stopo, topo, gh_c,
      t_c, rh_c, wind_c, ctime):

        self.setupBLCube(t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
          t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
          rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
          wind_BL90120, wind_BL120150, p_SFC, stopo, gh_c, t_c, rh_c,
          wind_c, ctime)
        BLR = self.BLR
        #
        topQPF = 0.60    # QPF value where raw PoP would be 75%
        RHexcess = 70.0  # RH above this can add to PoP and below will subtract
        adjAmount = 15.0 # amount of adjustment allowed
        #
        factor = tanh(QPF * (1.0 / topQPF))
        factor2 = tanh(QPF * (2.0 / topQPF))
        #
        #
        #
        rhcube = BLR[1:5]
        rhavg = add.reduce(rhcube) / 4.0
        rhmax = 100 - RHexcess
        dpop = rhavg - RHexcess
        dpop[less(dpop, 0.0)] = 0.0
        dpop = (dpop / rhmax) * (1.0 - factor2) * adjAmount
        #
        cwr = (factor * 100.0) + dpop
        cwr = clip(cwr, 0, 100)
        cwr=where(greater(cwr,PoP),PoP,cwr)
        return cwr

    #----------------------------------------------------------------
    #  Sky - Calculates cloud percentage in each layer based on
    #        RH in that layer.  Then adds up the percentages in
    #        the layers. Model clouds seem too 'binary', and so
    #        they are not used.
    #
    #        We guess that it takes higher RH near the surface (say
    #        97%) to get a cloud, but less RH up high (say only 90%
    #        to get cirrus).  Transition width is wider up high, than
    #        it is near the surface.
    #
    #        Also weight high clouds less in the coverage than
    #        low clouds.
    #
    #        No downscaling is attempted since an observer can usually
    #        see MANY gridpoints - and judges clouds based on all of
    #        them - not just whether there is a cloud in the small
    #        gridpoint directly overhead.  Thus, cloud fields are
    #        rather smooth.
    #----------------------------------------------------------------
    #def calcSky(self, t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
    #  t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
    #  rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
    #  wind_BL90120, wind_BL120150, p_SFC, stopo, topo, gh_c, t_c, rh_c,
    #  wind_c, ctime):

    #    self.setupBLCube(t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
    #      t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
    #      rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
    #      wind_BL90120, wind_BL120150, p_SFC, stopo, gh_c, t_c, rh_c,
    #      wind_c, ctime)
    #    BLP=self.BLP
    #    BLR=self.BLR
    #    #
    #    #  create a 'sigma' pressure field
    #    #
    #    pp = BLP / BLP[0]
    #    pp = clip(pp, 0.1, 1.0)
    #    #
    #    #  remove surface level - so surface Fog does not count
    #    #
    #    pp=pp[1:]
    #    BLR=BLR[1:]
    #    #
    #    #  get weight based on pressure - high levels get counted little
    #    #  maxes out at 700mb, low levels count a little less
    #    #
    #    ftop=50    # max coverage at top
    #    maxlev=0.7 # sigma leve of max allowed coverage
    #    fmax=100   # max coverage at max level
    #    fbot=90    # max coverage at surface
    #    f100 = where(less(pp,maxlev), ((fmax-ftop)*(pp/maxlev))+ftop,
    #                 fbot+(1.0-pp)*(fmax-fbot)/(1.0-maxlev))
    #    #
    #    #  ramp-up functions from RH to coverage based on pressure
    #    #
    #    midbot=90.0
    #    midtop=80.0
    #    mid=(pp*(midbot-midtop))+midtop
    #    widbot=10.0
    #    widtop=20.0
    #    wid=(pp*(widbot-widtop))+widtop
    #    c=(0.5*tanh(((BLR-mid)*2.0)/wid))+0.5
    #    #
    #    #  coverage for each level based on RH
    #    #
    #    f = minimum(f100 * c, 100.0)/100.0
    #    #
    #    #  When level 1 has 50% coverage, then 50% coverage
    #    #  at level 2 covers 50% of the remaining clear sky,
    #    #  (so now 75%) and 50% coverage at level 3 covers
    #    #  50% of the remaining clear sky (now 87%), etc.
    #    #
#        if f.shape[0]:
    #    sky = f[0]
#        else:
#            sky = resize(f, f.shape[1:])
    #    for i in xrange(1, f.shape[0]):
    #        sky = sky + f[i] - sky * f[i]
    #    #
    #    #  Smooth it a little
    #    #
    #    pSFCmb=p_SFC/100.0
    #    sky=where(less(pSFCmb,500),-9999.0,sky)
    #    sky=self.smoothpm(sky,2)
    #    sky=clip(sky*100.0,0.0,100.0)
    #    return sky

    ##--------------------------------------------------------------------------
    ##  Calculates Sky condition (fractional cloud cover) from model RH at specific
    ##  pressure levels.  Uses reduced equations from Walcek, MWR June 1994.
    ##  Adds up the amount of fractional clouds calculated at each layer based on 
    ##  topography (i.e. no clouds below ground) then divides by a suggested number
    ##  of layers to produce an average sky.
    ##-----------------------------------------------------------------------------
    def calcSky(self, rh_c, gh_c, topo, p_SFC, rh_BL030, rh_BL3060, rh_BL6090,
                rh_BL90120, rh_BL120150):

        tmpP_SFC = p_SFC.copy()
        tmpP_SFC /= 100.0       # convert surfp to millibars
        x = 560.0               # delta x (85km - 850km)

        #  Define a percentage of f100 to use as a filter (0.0 - 1.0)
        #  Remember f100 is an exponential function, so changes will be more 
        #  pronounced in the 0.5-1.0 range than the 0.0-0.5 range.
        percent = 0.37

        #  Define a list of boundary layer levels to include
        BL_levels = ['BL030', 'BL3060', 'BL6090', 'BL90120', 'BL120150']

        #  Construct a boundary layer pressure and RH cube
        bl_Pcube = []
        bl_RHcube = []

        #  Place all BL RH levels into a cube
        bl_RHcube += [rh_BL030]
        bl_RHcube += [rh_BL3060]
        bl_RHcube += [rh_BL6090]
        bl_RHcube += [rh_BL90120]
        bl_RHcube += [rh_BL120150]
        bl_RHcube = array(bl_RHcube)


        #  Make a cube of boundary layer pressures 
        for lvl in BL_levels:
            if lvl == 'BL030':
                tmpP = tmpP_SFC - 15.0
            elif lvl == 'BL3060':
                tmpP = tmpP_SFC - 45.0
            elif lvl == 'BL6090':
                tmpP = tmpP_SFC - 75.0
            elif lvl == 'BL90120':
                tmpP = tmpP_SFC - 105.0
            elif lvl == 'BL120150':
                tmpP = tmpP_SFC - 135.0
            elif lvl == 'BL150180':
                tmpP = tmpP_SFC - 165.0
            bl_Pcube += [tmpP]
        bl_Pcube = array(bl_Pcube)


        # Make a model level pressure cube
        pmb = ones_like(gh_c)
        for i in xrange(gh_c.shape[0]):
            pmb[i] = self.pres[i]


        #  Convert BL pressures to sigma levels
        BL_sigma = bl_Pcube / tmpP_SFC
        del bl_Pcube
        BL_sigma = clip(BL_sigma, 0.1, 1.0)

        #  Convert model level pressure cube to sigma surfaces
        pp = pmb / tmpP_SFC
        del tmpP_SFC
        pp = clip(pp, 0.1, 1.0)


        #  Account for topography in the model cube, don't need to worry about
        #  this with the BL cube since those are guaranteed to be above ground
        tmpRH_c = where(less(gh_c, topo), 0.0, rh_c)

        #=======================================================================
        #  Create new RH and sigma cubes

        newRH_c = []
        newSigma_c = []

        #  See which boundary layer levels have pressures > lowest "signficant"
        #  model level pressure
        for bl_i in xrange(BL_sigma.shape[0]):

            #  Make a mask to identify which points from the boundary
            #  layer level have greater pressure than lowest "significant"
            #  model level
            BL_mask = greater(BL_sigma[bl_i], pp[0])

            #  See how many points we've found
            count = sum(sum(BL_mask, 1))

            #  If there are no points - don't include this BL level
            if count == 0:
                continue

            #  Compute a temporary RH grid where it is lower than the lowest 
            #  "significant" model level data
            tmpRH = where(BL_mask, bl_RHcube[bl_i], 0.0)


            #  Compute a temporary sigma grid for this boundary layer level
            #  where it is lower than the lowest "significant" model level
            tmpSigma = where(BL_mask, BL_sigma[bl_i], 0.0)

            #  Insert this level into the new RH and sigma cubes
            newRH_c += [tmpRH]
            newSigma_c += [tmpSigma]


        #  Add lowest "significant" model level to RH and sigma cubes
        newRH_c += [tmpRH_c[0]]
        newSigma_c += [pp[0]]


        #  Insert boundary layer RH into RH cube where appropriate
        for lvl in xrange(1, len(self.levels())):

            #  Look at each boundary layer level
            for bl_i in xrange(BL_sigma.shape[0]):

                #  Make a mask to identify which points from the boundary
                #  layer level fall between the surrounding "significant"
                #  model levels
                BL_mask = logical_and(greater(BL_sigma[bl_i], pp[lvl]),
                              less(BL_sigma[bl_i], pp[lvl - 1]))

                #  See how many points we've found
                count = sum(sum(BL_mask, 1))

                #  If there are no points - don't include this BL level
                if count == 0:
                    continue

                #  Compute a temporary RH grid where it is between the two 
                #  "significant" model level data
                tmpRH = where(BL_mask, bl_RHcube[bl_i], 0.0)


                #  Compute a temporary sigma grid for this boundary layer level
                #  where it is between the two "significant" model levels
                tmpSigma = where(BL_mask, BL_sigma[bl_i], 0.0)

                #  Insert this level into the new RH and sigma cubes
                newRH_c += [tmpRH]
                newSigma_c += [tmpSigma]


            #  Add top of layer we just examined to RH and sigma cube
            newRH_c += [tmpRH_c[lvl]]
            newSigma_c += [pp[lvl]]

        del bl_RHcube
        del BL_sigma
        del tmpRH_c
        
        #  Finish off the new cubes
        newRH_c = array(newRH_c)
        newSigma_c = array(newSigma_c)

        #  Determine maximum possible sky fraction 
        fmax = 78.0 + x / 15.5

        #  Compute sky fraction for both pressure cubes 
        f100 = where(less(newSigma_c, 0.7),
                     fmax * (newSigma_c - 0.1) / 0.6,
                     30.0 + (1.0 - newSigma_c) * (fmax - 30.0) / 0.3)

        #  Compute RH depression at 37% f100 [ (1-RHe) in Walcek ]              
        c = 0.196 + (0.76 - x / 2834.0) * (1.0 - newSigma_c)
        
        del newSigma_c

        #  Compute critical RH threshold to use as a filter
        #  Note (percent * f100)/f100 = percent
        try:
            rhCrit = log(percent) * c + 1.0
        except:
            rhCrit = 0.0

        #  Ensure "critical RH" is valid
        rhCrit = clip(rhCrit, 0.0, 1.0)

        #  Compute sky fraction for the model cube
        c = (newRH_c / 100.0 - 1.0) / c
        c = exp(c)
        f = minimum(f100 * c, 100.0)

        #  Where RH is less than the critical value, set it to 0 contribution
        f[less(newRH_c / 100.0, rhCrit)] = 0.0
        
        del newRH_c

        #  Compress cubes vertically
        f = self.squishZ(f, (f.shape[0] / 5) - 1)        #  was 5

        #  Convert sky fractions to an actual percentage
        if len(f) >= 5:
            f[4] *= 0.25
        else:
            LogStream.logEvent("WARNING: Sky data is missing some levels - calculation will be incomplete")
            ind = len(f) - 1
            f[ind] *= 0.25

        f /= 100.0

        sky = f[0]
        for i in xrange(1, f.shape[0]):
            sky = sky + f[i] - sky * f[i]

        grid = sky * 100.0

        return grid
    #=========================================================================
    #  Wind - uses boundary layer wind 'sounding' to get the wind at the
    #   real elevation rather than the model elevation. When real topo
    #   is below model topo,  just uses the lowest boundary layer wind field.
    #
    #   This typically gives ridgetops a bit too much wind speed - so if speed
    #   is above the model surface wind speed - it only uses 1/2 of the
    #   difference.  Direction is allowed to reflect the direction at the
    #   higher level. This gives the wind a 'topography' influenced look -
    #   with sharp mountains sticking up into 'stronger' wind speeds and
    #   different wind directions.
    #----------------------------------------------------------------
    def calcWind(self, t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
      t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
      rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
      wind_BL90120, wind_BL120150, p_SFC, stopo, topo, gh_c, t_c, rh_c,
      wind_c, ctime):

        self.setupBLCube(t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
          t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
          rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
          wind_BL90120, wind_BL120150, p_SFC, stopo, gh_c, t_c, rh_c,
          wind_c, ctime)
        BLH = self.BLH
        BLW = self.BLW
        BLMAG = BLW[0]
        BLDIR = BLW[1]

        smag = (stopo * 0.0) - 1.0
        sdir = smag

        smag=where(less(topo,BLH[0]),BLMAG[0],smag)
        sdir=where(less(topo,BLH[0]),BLDIR[0],sdir)

        for i in range(1, BLH.shape[0]):
           mval = self.linear(BLH[i], BLH[i - 1], BLMAG[i], BLMAG[i - 1], topo)
           dval = self.dirlinear(BLH[i], BLH[i - 1], BLDIR[i], BLDIR[i - 1], topo)
           #
           #  limit winds to be half as strong as wind in
           #  free atmosphere above the model surface would indicate
           #
           mval=where(greater(mval,BLMAG[0]),BLMAG[0]+((mval-BLMAG[0])/2.0),
             mval)
           between = logical_and(greater_equal(topo, BLH[i - 1]), less(topo, BLH[i]))
           smag=where(logical_and(less(smag,0.0),between),mval,smag)
           sdir=where(logical_and(less(sdir,0.0),between),dval,sdir)
        #
        #  Change to knots
        #
        mag = smag * 1.94
        mag=where(less(p_SFC/100.0,500.0),0.0,mag)
        dir = clip(sdir, 0, 359.5)
        return(mag, dir)

    #========================================================================
    #  MixHgt - the height to which a parcel above a 'fire' would rise
    #    (in height) above ground level (in feet).
    #
    #  Calculated by assuming a parcel above a fire is VERY hot - but the fire
    #  is very small - so that entrainment quickly makes it only a few degrees
    #  warmer than the environment.  Ideally would want to consider moisture
    #  and entrainment - but this is a very simple first guess.
    #
    #  This does NO downscaling - and even smooths the field a little at the
    #  end.  We have no observations of this - other than at sounding
    #  locations - so we have no idea what the spatial patterns should look
    #  like.
    #----------------------------------------------------------------
    def calcMixHgt(self, t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
      t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
      rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
      wind_BL90120, wind_BL120150, p_SFC, stopo, topo, gh_c, t_c, rh_c,
      wind_c, ctime):

        self.setupBLCube(t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
          t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
          rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
          wind_BL90120, wind_BL120150, p_SFC, stopo, gh_c, t_c, rh_c,
          wind_c, ctime)
        BLT = self.BLT
        BLP = self.BLP
        BLTheta = self.ptemp(BLT, BLP)
        BLH = self.BLH
        #
        #  Potential temp of fire 2 degrees warmer than surface parcel
        #
        fireHeat = 2.0
        pSFCmb = p_SFC / 100
        fireTheta = self.ptemp(t_FHAG2 + fireHeat, pSFCmb)
        #
        #  find height the fireTheta crosses the sounding theta
        #
        mixhgt = (stopo * 0.0) - 1.0
        for i in range(1, BLH.shape[0]):
           hcross = self.linear(BLTheta[i], BLTheta[i - 1], BLH[i], BLH[i - 1], fireTheta)
           cross = logical_and(greater(BLTheta[i], fireTheta), less(mixhgt, 0.0))
           mixhgt=where(cross,hcross,mixhgt)
        mixhgt=where(less(mixhgt,0.0),BLH[-1],mixhgt)
        #
        #  Change to height above the model topo (in feet)
        #  and smooth a little
        #
        final = (mixhgt - stopo) * 3.28
#        final=where(less(pSFCmb,500),-9999.0,final)
        final[less(pSFCmb, 500)] = -9999.0
        final = self.smoothpm(final, 2)
        final = clip(final, 0.0, 50000.0)
        return final

    #===========================================================================
    #  SnowAmt - simple snow ratio based on surface temperature - multiplied
    #            times the model QPF amount
    #---------------------------------------------------------------------------
    def calcSnowAmt(self, T, QPF):
        snowr = (T * -0.5) + 22.5
        snowr[less(T, 9.0)] = 20
        snowr[greater_equal(T, 30.0)] = 0
        snowamt = QPF * snowr
        return snowamt

    #==========================================================================
    # Many of the models have had a freezing level in the gh field.
    #==========================================================================
    def calcFzLevel(self, gh_FRZ):
        return gh_FRZ * 3.28

    #========================================================================
    # calcSnowLevel - takes sounding of the wetbulb temperature and finds the
    #   lowest elevation (above ground) where wetbulb crosses from
    #   above freezing to below freezing. When top wetbulb is above
    #   freezing - puts in height of top level.  When surface
    #   wetbulb is below freezing - assumes a simple dry-adiabtic
    #   lapse rate below ground (which is ludicrous for a wetbulb
    #   lapse rate - but who really cares what the snow level is
    #   when it is below ground anyway?).
    #
    #   This is almost always too noisy so we smooth it with a
    #   +/- 4 gridpoint average.  Note that this means that there
    #   may be gridpoints where the surface wetbulb is below
    #   freezing - but the snow level ends up being above
    #   ground.  If this bothers you - remove the smoothing.
    #------------------------------------------------------------------------
    def calcSnowLevel(self, t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
      t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
      rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
      wind_BL90120, wind_BL120150, p_SFC, T, RH, stopo, topo, gh_c, t_c,
      rh_c, wind_c, ctime):

        self.setupBLCube(t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
          t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
          rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
          wind_BL90120, wind_BL120150, p_SFC, stopo, gh_c, t_c, rh_c,
          wind_c, ctime)
        BLH = self.BLH
        #
        #
        #
        if USE_WETBULB == 1:
           TT = self.BLE
        else:
           TT = self.BLT
        #
        #  get wetbulb temperatures above topography
        #
        (BLH, TT) = self.getTopoE(topo, stopo, p_SFC, T, RH, BLH, TT)
        snowlvl = (stopo * 0.0) - 1.0
        #
        #  find the ones below ground
        #
        tk = TT[0]
        below = less(tk, 273.15)
        lapse = 9.8 / 1000.0
        tmsl = tk + (lapse * topo)
        hbot = topo * 0.0
        hcross = self.linear(tk, tmsl, topo, hbot, 273.15)
        hcross = where(less(hcross, 0.0), 0.0, hcross)

        snowlvl=where(below,hcross,snowlvl)
        #
        #  find the ones above the topo surface
        #
        tbot = tk
        hbot = topo
        for i in range(1, BLH.shape[0]):
           hcross = self.linear(TT[i], TT[i - 1], BLH[i], BLH[i - 1], 273.15)
           cross = logical_and(less_equal(TT[i], 273.15), greater(TT[i - 1], 273.15))
           add = logical_and(cross, less(snowlvl, -0.5))
           snowlvl=where(add,hcross,snowlvl)
        #
        #  when still above freezing at the top of the BL layer - just
        #  put in that height (best we can do without more data)
        #
        snowlvl=where(less(snowlvl,-0.5),BLH[-1],snowlvl)
        #
        #  Change to feet and subtract 500 feet if not using the wetbulb method
        #
        final = snowlvl * 3.28
        if USE_WETBULB != 1:
           snowlvl = snowlvl - 500.0
        #
        #  Take care of any missing data points
        #
        pSFCmb = p_SFC / 100.0
#        final=where(less(pSFCmb,500.0),-9999.0,final)
        final[less(pSFCmb, 500.0)] = -9999.0
        #
        #  Smooth a little to reduce noise
        #
        final = self.smoothpm(final, 4)
        final = clip(final, 0.0, 50000.0)
        return final

    #==========================================================================
    #  TransWind - the average winds in the layer between the surface
    #              and the mixing height.
    #--------------------------------------------------------------------------
    def calcTransWind(self, t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
      t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
      rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
      wind_BL90120, wind_BL120150, p_SFC, MixHgt, stopo, topo, gh_c, t_c,
      rh_c, wind_c, ctime):

        self.setupBLCube(t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
          t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
          rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
          wind_BL90120, wind_BL120150, p_SFC, stopo, gh_c, t_c, rh_c,
          wind_c, ctime)
        BLW = self.BLW
        BLH = self.BLH
        BLM = BLW[0]
        BLD = BLW[1]
        nmh = stopo + (MixHgt * 0.3048) # convert MixHt from feet -> meters

        pSFCmb = p_SFC / 100.0
        (utot, vtot) = self._getUV(BLM[0], BLD[0])
        numl = (stopo * 0.0) + 1.0

        for i in range(1, BLH.shape[0]):
           use = less(BLH[i], nmh)
           (u, v) = self._getUV(BLM[i], BLD[i])
           utot=where(use,utot+u,utot)
           vtot=where(use,vtot+v,vtot)
           numl=where(use,numl+1,numl)

        #
        #  calculate average
        #
        u = utot / numl
        v = vtot / numl
        #
        #  Smooth a little
        #
#        u=where(less(pSFCmb,500.0),-9999.0,u)
#        v=where(less(pSFCmb,500.0),-9999.0,v)
        u[less(pSFCmb, 500.0)] = -9999.0
        v[less(pSFCmb, 500.0)] = -9999.0
        u = self.smoothpm(u, 1)
        v = self.smoothpm(v, 1)
        #
        # convert u, v to mag, dir
        #
        (tmag, tdir) = self._getMD(u, v)
        tdir = clip(tdir, 0, 359.5)
        tmag = tmag * 1.94  # convert to knots
        tmag = clip(tmag, 0, 125)  # clip speed to 125 knots
        return(tmag, tdir)

    #--------------------------------------------------------------------------
    # LAL - Based mainly on lifted index.  Adds more when RH at top of BL is
    #       high, but RH at bottom of BL is low.
    #--------------------------------------------------------------------------
    def calcLAL(self, t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
      t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
      rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
      wind_BL90120, wind_BL120150, p_SFC, tp_SFC, bli_BL0180, stopo, topo,
      gh_c, t_c, rh_c, wind_c, ctime):

        self.setupBLCube(t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
          t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120,
          rh_BL120150, wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090,
          wind_BL90120, wind_BL120150, p_SFC, stopo, gh_c, t_c, rh_c,
          wind_c, ctime)
        lal = ones_like(self._empty)
        BLR = self.BLR
        #
        #  only thing we have is boundary layer lifted index
        #  set LAL to 2 if LI<0, 3 if LI<-3, 4 if LI<-5
        #
        lal=where(less(bli_BL0180, 0), lal+1, lal)
        lal=where(less(bli_BL0180, -3), lal+1, lal)
        lal=where(less(bli_BL0180, -5), lal+1, lal)

        #
        #  Add more when RH at top of BL is greater than
        #  than 70% and RH at bottom of BL is less than 30
        #
        V = logical_and(greater(BLR[5], 70), less(BLR[0], 30))
        lal=where(V,lal+1,lal)
        #
        #  Add even more where RH at top of BL is greater than
        #  80% and RH at bottom of BL is less than 20%
        #
        V = logical_and(greater(BLR[5], 80), less(BLR[0], 20))
        lal=where(V,lal+1,lal)
        lal=where(less(bli_BL0180,-18.0),1,lal)
        return lal

    ##--------------------------------------------------------------------------
    ##  Calculate the Haines index based on the temp and RH cubes
    ##  Define self.whichHainesIndex to be "HIGH", "MEDIUM", or "LOW".
    ##  Default is "HIGH".
    ##--------------------------------------------------------------------------
    def calcHaines(self, t_c, rh_c):
        return self.hainesIndex(self.whichHainesIndex, t_c, rh_c)

    #=======================================================================
    #
    #  Calculate Haines Index
    #  type is "LOW", "MEDIUM", "HIGH"
    #  NOTE, the default haines index calcaulation is defined by:
    #  self.whichHainesIndex, which can be set to "LOW", "MEDIUM", "HIGH".
    #  Commented out below calc for DR14439 (A1 DR21354)
    #=======================================================================
 ##   def hainesIndex(self, type, t_c, rh_c):
 ##       dict = {}
 ##       dict['LOW'] = {'t1Level': 950, 't2Level': 850, 'mLevel': 850,
 ##          'stabThresh': [3, 8], 'moiThresh': [5, 10]}
 ##       dict['MEDIUM'] = {'t1Level': 850, 't2Level': 700, 'mLevel': 850,
 ##          'stabThresh': [5, 11], 'moiThresh': [5, 13]}
 ##       dict['HIGH'] = {'t1Level': 700, 't2Level': 500, 'mLevel': 700,
 ##          'stabThresh': [17, 22], 'moiThresh': [14, 21]}
 ##       dd = dict[type]   # proper dictionary for the level
 ##
 ##       # get the needed data, calc dewpoint
 ##       pres = self.pres
 ##       t1 = t_c[pres.index(dd['t1Level'])]  #  t1 level
 ##       t2 = t_c[pres.index(dd['t2Level'])]  #  t2 level
 ##       tMois = t_c[pres.index(dd['mLevel'])] - 273.15  #  mLevel t , in C.
 ##       rhMois = rh_c[pres.index(dd['mLevel'])] / 100.0  # mLevel rh
 ##       rhMois = where(less_equal(rhMois, 0), 0.00001, rhMois)
 ##
 ##       a = log10(rhMois) / 7.5 + (tMois / (tMois + 237.3))
 ##       dpMois = (a * 237.3) / (1.0 - a)
 ##
 ##       hainesT = t1 - t2
 ##       hainesM = tMois - dpMois
 ##
 ##       # now make the categories
 ##       slope = 1.0 / (dd['stabThresh'][1] - dd['stabThresh'][0])
 ##       intercept = 1.5 - ((dd['stabThresh'][0] + 0.5) * slope)
 ##       hainesTi = (slope * hainesT) + intercept
 ##       hainesT = clip(hainesTi, 1.0, 3.0)
 ##
 ##       slope = 1.0 / (dd['moiThresh'][1] - dd['moiThresh'][0])
 ##       intercept = 1.5 - ((dd['moiThresh'][0] + 0.5) * slope)
 ##       hainesMi = (slope * hainesM) + intercept
 ##       hainesM = clip(hainesMi, 1.0, 3.0)
 ##
 ##       return hainesT + hainesM

    #---------------------------------------------------------------------------
    # MaxT simply maximum of any T grids during the period
    #--------------------------------------------------------------------------
    def calcMaxT(self, T, MaxT):
        if MaxT is None:
            return T
        return maximum(MaxT, T)

    #---------------------------------------------------------------------------
    # MinT simply minimum of any T grids during the period
    #--------------------------------------------------------------------------
    def calcMinT(self, T, MinT):
        if MinT is None:
            return T
        return minimum(MinT, T)

    #-------------------------------------------------------------------------
    #  MaxRH is simply maximum of all RH grids during period
    #--------------------------------------------------------------------------
    def calcMaxRH(self, RH, MaxRH):
        if MaxRH is None:
            return RH
        return maximum(MaxRH, RH)

    #-------------------------------------------------------------------------
    #  MinRH is simply minimum of all RH grids during period
    #--------------------------------------------------------------------------
    def calcMinRH(self, RH, MinRH):
        if MinRH is None:
            return RH
        return minimum(MinRH, RH)

    #==========================================================================
    #  Calculate Wetbulb (K) based on temperature (C) and RH (%)
    #  (all algorithms straight out of GEMPAK - converted to numeric python)
    #
    def Wetbulb(self, tc, rh, pres):
       dpc = self.RHDP(tc, rh)
       thte = self.THTE(pres, tc, dpc)
       wetbk = self.TMST(thte, pres, 0)
       return wetbk

    #=======================================================================
    #  Calculate parcel temp (K) given thetae (K) pressure (mb) and guess
    #                                  temperature (K)  (must be 3d cubes)
    #
    def TMST(self, thte, pres, tguess):
       tg = ones(thte.shape) * tguess
       teclip = clip(thte - 270.0, 0.0, 5000.0)
       #
       #  if guess temp is 0 - make a more reasonable guess
       #
       tg=where(less(tg,1),(thte-0.5*teclip**1.05)*(pres/1000.0)**0.2,tg)

       epsi = 0.01
       tgnu = tg - 273.15
       #
       #  Correct the temp up to 100 times.  Typically this takes
       #  less than 5 iterations
       #
       for i in range(1, 100):
           tgnup = tgnu + 1.0
           tenu = self.THTE(pres, tgnu, tgnu)
           tenup = self.THTE(pres, tgnup, tgnup)
           cor = (thte - tenu) / (tenup - tenu)
           tgnu = tgnu + cor
           #
           #  get the maximum correction we made this time
           #  and if it is less than epsi - then we are close
           #  enough to stop.
           #
           acor = abs(cor)
           mcor = maximum.reduce(maximum.reduce(maximum.reduce(acor)))
           if (mcor < epsi):
              #print "parcel temp in %d iterations"%i
              return (tgnu + 273.15)
       return tgnu + 273.15

    #=======================================================================
    #  Calculate Dewpoint (C) based on Temperature (C) and RH (%)
    #
    def RHDP(self, tc, rh):
       log1 = log(6.112)
       vaps = self.VAPR(tc)
       lvapr = log(rh * vaps / 100.0 + 0.0001)
       dpc = ((243.5 * (log1 - lvapr)) / (lvapr - log1 - 17.67))
       return dpc

    #=======================================================================
    #  Calculate Theta-E given Pressure (mb) Temperature (C) and Dewpoint (C)
    #
    def THTE(self, pres, tc, dpc):
       rmix = self.MIXR(dpc, pres)
       tk = tc + 273.15
       e = (2.0 / 7.0) * (1.0 - (0.00028 * rmix))
       thtam = tk * (1000.0 / pres) ** e
       tlcl = self.TLCL(tc, dpc)
       e = ((3.376 / tlcl) - 0.00254) * (rmix * (1.0 + 0.00081 * rmix))
       return (thtam * exp(e))

    #=======================================================================
    #  Calculate temperature at LCL (K) given Temperature (C) and Dewpoint (C)
    #
    def TLCL(self, tc, dpc):
       tk = tc + 273.15
       dk = dpc + 273.15
       return((1.0 / (1.0 / (dk - 56.0) + log(tk / dk) / 800.0)) + 56.0)

    #=======================================================================
    #  Calculate Mixing Ratio (g/kg) given Dewpoint (C) and pressure (mb)
    #
    def MIXR(self, dpc, pres):
       vapr = self.VAPR(dpc)
       corr = (1.001 + ((pres - 100.) / 900.) * 0.0034)
       e = corr * vapr
       mixr = 0.62197 * (e / (pres - e)) * 1000.0
       return mixr

    #=======================================================================
    #  Calculate Vapor Pressure (mb) from Dewpoint (C)
    #  or Saturation Vapor Pressure (mb) from Temperature (C)
    #
    def VAPR(self, tc):
       vapr = 6.112 * (exp((17.67 * tc) / (tc + 243.5)))
       return vapr

    #==========================================================================
    #  Get boundary layer cube - cube of values above model surface
    #  adds in pressure level data above the boundary layer fields
    #     creates:
    #        BLT - temperatures (K)
    #        BLR - relative humidity (% 0-100)
    #        BLH - height (m)
    #        BLP - pressure (mb)
    #        BLW - wind (magnitude kts, direction)
    #        BLD - dewpoint (K)
    #        BLE - wetbulb (K) [if desired]
    #
    def setupBLCube(self, t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120,
                    t_BL120150, rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090,
                    rh_BL90120, rh_BL120150, wind_FHAG10, wind_BL030,
                    wind_BL3060, wind_BL6090, wind_BL90120, wind_BL120150,
                    p_SFC, stopo, gh_c, t_c, rh_c, wind_c, ctime):
        #
        #  check to see if already set up for this time
        #
        if self.BLcubeTime == ctime:
           return
        #
        #  split pressure level wind cube into magnitude and direction
        #
        mag_c = wind_c[0]
        dir_c = wind_c[1]
        dew_c = self.RHDP(t_c - 273.15, rh_c) + 273.15
        #
        tbl = [t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120, t_BL120150]
        rbl = [rh_FHAG2, rh_BL030, rh_BL3060, rh_BL6090, rh_BL90120, rh_BL120150]
        wbl = [wind_FHAG10, wind_BL030, wind_BL3060, wind_BL6090, wind_BL90120,
          wind_BL120150]
        pdiff = [0, 30, 60, 90, 120, 150]

        pSFCmb = p_SFC / 100.0
        pSFCmb = where(less(pSFCmb, 500.0), 1013.0, pSFCmb)

        p_list = [pSFCmb]
        hbot = stopo
        h_list = [hbot]
        t_list = [t_FHAG2]
        r_list = [clip(rh_FHAG2, 0.0001, 99.999)]
        m_list = [wind_FHAG10[0]]
        d_list = [wind_FHAG10[1]]
        w_list = [self.RHDP(t_FHAG2 - 273.15, r_list[0]) + 273.15]

        for i in range(1, len(tbl)):
           tavg = tbl[i]
           tavgc = tavg - 273.15
           ravg = clip(rbl[i], 0.0001, 99.999)
           davgc = self.RHDP(tavgc, ravg)
           ptop = clip(pSFCmb - pdiff[i], 1.0, 1050.0)
           pbot = clip(pSFCmb - pdiff[i - 1], 1.0, 1050.0)
           htop = self.MHGT(tavgc, davgc, ptop, pbot, hbot)

           t_list.append(tavg)
           h_list.append((hbot + htop) / 2.0)
           wind = wbl[i]
           m_list.append(wind[0])
           d_list.append(wind[1])
           p_list.append((pbot + ptop) / 2.0)
           r_list.append(ravg)
           w_list.append(davgc + 273.15)

           hbot = htop
        #
        #  above the boundary layer...add levels in pressure
        #  cube
        #
        numplevs = gh_c.shape[0]
        levstoadd = stopo * 0.0
        for i in range(numplevs):
            levstoadd = where(greater(gh_c[i], hbot), levstoadd + 1, levstoadd)

        maxtoadd = maximum.reduce(maximum.reduce(levstoadd))
        for j in range(int(maxtoadd)):
           found = stopo * 0.0
           hlev = found
           tlev = found
           mlev = found
           dlev = found
           plev = found
           rlev = found
           wlev = found
           for i in range(numplevs):
              usethislev = logical_and(less(found, 0.5), greater(gh_c[i], hbot))
              hlev=where(usethislev,gh_c[i],hlev)
              plev=where(usethislev,self.pres[i],plev)
              tlev=where(usethislev,t_c[i],tlev)
              mlev=where(usethislev,mag_c[i],mlev)
              dlev=where(usethislev,dir_c[i],dlev)
              rlev=where(usethislev,rh_c[i],rlev)
              wlev=where(usethislev,dew_c[i],wlev)
              found=where(usethislev,1.0,found)

              numNotFound = add.reduce(add.reduce(less(found, 0.5)))
              if numNotFound < 1:
                 break
           if numNotFound > 0:
              hlev=where(less(found,0.5),gh_c[numplevs-1],hlev)
              plev=where(less(found,0.5),self.pres[numplevs-1],plev)
              tlev=where(less(found,0.5),t_c[numplevs-1],tlev)
              mlev=where(less(found,0.5),mag_c[numplevs-1],mlev)
              dlev=where(less(found,0.5),dir_c[numplevs-1],dlev)
              rlev=where(less(found,0.5),rh_c[numplevs-1],rlev)
              wlev=where(less(found,0.5),dew_c[numplevs-1],wlev)

           h_list.append(hlev)
           t_list.append(tlev)
           p_list.append(plev)
           m_list.append(mlev)
           d_list.append(dlev)
           r_list.append(rlev)
           w_list.append(wlev)
           hbot = hlev

        self.BLH = array(h_list)
        self.BLP = array(p_list)
        self.BLT = array(t_list)
        self.BLR = array(r_list)
        #mags=array(m_list)
        #dirs=array(d_list)
        #self.BLW=(mags,dirs)
        self.BLW = (m_list, d_list)
        self.BLD = array(w_list)
        if USE_WETBULB == 1:
           self.BLE = self.Wetbulb(self.BLT - 273.15, self.BLR, self.BLP)
        self.BLcubeTime = ctime
        return

    #---------------------------------------------------------------------------
    #  Calculate the hydrostatic height (m) at the top of the layer, given an
    #  average temp (C) and average dewpoint (C) in the layer, the pressure (mb)
    #  at the top and bottom of the layer, and the height (m) at the bottom
    #  of the layer.  Intended to be used in an integration of hydrostatic
    #  heights given a starting surface height and temp/dewpoint values in
    #  pressure levels above
    #
    def MHGT(self, tmpc, dwpc, ptop, pbot, hbot):
        pavg = (ptop + pbot) / 2.0
        scale = self.SCLH(tmpc, dwpc, pavg)
        mhgt = hbot + (scale * log(pbot / ptop))
        return mhgt

    #---------------------------------------------------------------------------
    #  Calculate Virtual temperature (C) given temp(C), dewpoint (C)
    #  and pressure(mb)
    #
    def TVRT(self, tmpc, dwpc, pres):
       mixrscale = self.MIXR(dwpc, pres) * 0.001
       tmpk = tmpc + 273.15
       tvrk = tmpk * (1.0 + (mixrscale / 0.62197)) / (1.0 + mixrscale)
       tvrt = tvrk - 273.15
       return tvrt

    #---------------------------------------------------------------------------
    #  Calculate Scale Height (m) given temp(C), dewpoint(C) and pressure(mb)
    #
    def SCLH(self, tmpc, dwpc, pres):
       rdgas = 287.04
       gravty = 9.80616
       sclh = (rdgas / gravty) * (self.TVRT(tmpc, dwpc, pres) + 273.15)
       return sclh

    #--------------------------------------------------------------------------
    #  calculate area above/below freezing in J/kg (m2/s2)
    #
    def getArea(self, hbot, tbot, htop, ttop):
        tavg = (ttop + tbot) / 2.0
        e1 = (ttop - 273.15) / 273.15
        e2 = (tbot - 273.15) / 273.15
        area = 9.8 * ((e1 + e2) / 2.0) * (htop - hbot)
        return area

    #--------------------------------------------------------------------------
    #  calculate areas above/below freezing, and include a flag if it crosses
    #  in this layer
    #
    def getAreas(self, hbot, tbot, htop, ttop):
        maxm = maximum(tbot, ttop)
        minm = minimum(tbot, ttop)
        freeze = self._empty + 273.15
        crosses = logical_and(less(minm, freeze), greater(maxm, freeze))
        crossh = self.linear(tbot, ttop, hbot, htop, freeze)
        crosst = freeze
        crossh = where(crosses, crossh, htop)
        crosst = where(crosses, crosst, ttop)

        a1 = self.getArea(hbot, tbot, crossh, crosst)
        a2 = self.getArea(crossh, crosst, htop, ttop)
        return a1, a2, crosses

    #========================================================================
    # Get a cube of wetbulb temperatures above the real topo - not above the
    #     model topo.  Returns the wetbulb temps and heights
    #
    def getTopoE(self, topo, stopo, p_SFC, T, RH, BLH, BLE):

        pSFCmb = p_SFC / 100.0
        pSFCmb = where(less(pSFCmb, 500.0), 1013.0, pSFCmb)

        tmpc = self.FtoK(T) - 273.15
        hlist = [topo]
        if USE_WETBULB == 1:
           dwpc = self.RHDP(tmpc, RH)
           scale = self.SCLH(tmpc, dwpc, pSFCmb)
           ptopo = pSFCmb * exp((stopo - topo) / scale)
#           ptopo=where(less(ptopo,500.0),1013.0,ptopo)
           ptopo[less(ptopo, 500.0)] = 1013.0
           at = array([tmpc])
           ar = array([RH])
           ap = array([ptopo])
           te = self.Wetbulb(at, ar, ap)
           te_SFC = te[0]
           tlist = [te_SFC]
        else:
           tlist = [tmpc + 273.15]


        numplevs = BLH.shape[0]
        levstoadd = topo * 0.0
        for i in range(numplevs):
           levstoadd=where(greater(BLH[i],topo),levstoadd+1,levstoadd)
        maxtoadd = maximum.reduce(maximum.reduce(levstoadd))

        hbot = topo
        for j in range(int(maxtoadd)):
           tlev = topo * 0.0
           hlev = topo * 0.0 - 5000
           use = topo * 0.0
           for i in range(BLH.shape[0]):
              thislev = logical_and(less(use, 0.5), greater(BLH[i], hbot))
              tlev=where(thislev,BLE[i],tlev)
              hlev=where(thislev,BLH[i],hlev)
              use=where(thislev,1.0,use)

           tlev=where(less(tlev,0.5),BLE[-1],tlev)
           hlev=where(less(hlev,-2500),BLH[-1],hlev)

           tlist.append(tlev)
           hlist.append(hlev)
           hbot = hlev
        newH = array(hlist)
        newE = array(tlist)

        return(newH, newE)

    #===============================================================
    #  smooths array by averaging over +/- k gridpoints in each
    #  direction.  At the edges, only averages over the points that
    #  fit within this "averaging area".  If k is zero or negative
    #  it just returns the original array
    #
    def smoothpm(self, array, k):
        if k > 0:
           a = array * 0.0
           n = array * 0.0
           for x in range(-k, k + 1):
              for y in range(-k, k + 1):
                array1 = self.offset(array, x, y)
                ok = greater(array1, -9000)
                a=where(ok,a+array1,a)
                n=where(ok,n+1,n)
           a=where(less(n,1),array,a)
           n=where(less(n,1),1,n)
           arraysmooth = a / n
        else:
           arraysmooth = array
        return arraysmooth

    #=======================================================================
    #  Gets a copy of array that is shifted x,y gridpoints.  The edge
    #  points that are unknown are set to -9999.0.  Used in smoothing
    #
    def offset(self, a, x, y):
        sy1, sy2 = self.getindicies(y, a.shape[0])
        sx1, sx2 = self.getindicies(x, a.shape[1])
        b = zeros(a.shape, a.dtype) - 9999.0
        b[sy1, sx1] = a[sy2, sx2]
        return b

    #==============================================================
    #  getindicies - used in slicing array
    #
    def getindicies(self, o, l):
        if o > 0:
            a = slice(o, l); b = slice(0, l - o)
        elif o < 0:
            a = slice(0, l + o); b = slice(-o, l)
        else:
            a = slice(0, l); b = slice(0, l)
        return a, b

    #==========================================================================
    #   A linear interpolation that can be used for directions, where the
    #   values should never get higher than 360 degrees.  We want
    #   interpolations that cross this 360 degree barrier to "go the
    #   right way" rather than flip back in the opposite direction
    #
    def dirlinear(self, xmax, xmin, ymax, ymin, we):
        ydif = ymax - ymin
        ydif=where(less(ydif,0.0),-ydif,ydif)
        rotate = greater(ydif, 180.0)
        upper = greater(ymin, 180.0)
        lower = less(ymin, 180.0)
        ymax=where(logical_and(rotate,upper),ymax+360.0,ymax)
        ymax=where(logical_and(rotate,lower),ymax-360.0,ymax)
        slope = (ymax - ymin) / (xmax - xmin + .0000001)
        intercept = ymin - slope * xmin
        value = slope * we + intercept
        value=where(greater(value,360),value-360,value)
        value=where(less(value,0.0),value+360,value)
        return value

    def gvar2T(self, ir):
        t = where(ir < 177, (660 - ir) / 2.0, (418 - ir))
        t = t - 273
        return t

    def calcIR11(self, SBT124_NTAT):
        return self.gvar2T(SBT124_NTAT)

    def calcIR13(self, SBT125_NTAT):
        return self.gvar2T(SBT125_NTAT)

    def calcIR39(self, SBT122_NTAT):
        return self.gvar2T(SBT122_NTAT)

    def calcWaterVapor(self, SBT123_NTAT):
        return self.gvar2T(SBT123_NTAT)

    def calcFog(self, IR11, IR39):
        return IR11 - IR39

def main():
    NAM12Forecaster().run()
