import OrcFxAPI as Orc
import pandas as pd
import numpy as np

# identifies the basecase file and key objects within it
model = Orc.model('basecase.dat')  
line = model['riser']
vessel = model['FPSO']
riserType = model[line.LineType[0]] # assume that the first section line type is the pipe line type

# load/stress allowable limits
SMYS = riserType.APIRP1111S                        # get the specified minimum yield strength from model 
A = (np.pi/4)*(riserType.OD**2 - riserType.ID**2)  # cross-sectional area of riser pipe
maxTensionlimit = 0.6*SMYS*A                       # effective tension limit defined by APIRP1111
minTensionlimit = 0                                # assuming no compression is allowed
stressLimit_APIRP1111 = 0.9 *riserType.APIRP1111S/1000 # in MPa, derived automatically from the OrcaFlex model

# obtain results from orcaflex
model.CalculateStatics()                                                     # perform static calculation
topTension = line.StaticResult('Effective Tension', OrcFxAPI.oeEndA)         # tension at topside
bottomTension = line.StaticResult('Effective Tension', OrcFxAPI.oeTouchdown) # tension at touchdown 
lineTension = (line.RangeGraph('Effective Tension', OrcFxAPI.pnStaticState)).Mean # tension from top to bottom
minLineTension = min(lineTension)
topBendMoment = line.StaticResult('Bend Moment', OrcFxAPI.oeEndA)
maxcombinedload = (line.RangeGraph('API RP 1111 Max Combined', OrcFxAPI.pnStaticState)).Mean
maxVonMisesstress = (line.RangeGraph('Max von Mises Stress', OrcFxAPI.pnStaticState)).Mean


# checks results against the allowable limit
def toptensionlimit():
    if topTension <= maxTensionlimit:
        return 'pass'
    else:
        return 'fail'
toptensionlimit()

def minLineTensionlimit():
    if minLineTension >= minTensionlimit:
        return 'pass'
    else:
        return 'fail'
minLineTensionlimit()

def max_combinedload_unity_check():
    if maxcombinedload <= 1.0:   # APIRP1111 combined load unity check due to axial load,bending and external pressure
        return 'pass'
    else:
        return 'fail'
max_combinedload_unity_check()

def codestress_check():
    if maxVonMisesstress/1000 <= stressLimit_APIRP1111:
        return 'pass'
    else:
        return 'fail'
codestress_check()

# write out results
data = pd.DataFrame({'topTension[kN]': [[topTension,toptensionlimit()]]
                     'bottomTension[kN]': [[bottomTension]],
                     'minLineTension[kN]': [[minLineTension, minLineTensionlimit()]],
                     'topBendMoment[kNm]': [[topBendMoment]],
                     'maxcombinedload[kNm]':[[maxcombinedload,max_combinedload_unity_check()]],
                     'maxVonMisesstress[MPa]':[[maxVonMisesstress],codestress_check()]] })
print(data)
