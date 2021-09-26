#import python interface to OrcaFlex
import OrcFxAPI as Orc
model = Orc.Model()

#set unit system
model.general.UnitsSystem = 'User'
model.general.MassUnits = 'kg'
model.general.ForceUnits = 'kN'

# General data
def general()
    stagecount = model.general.StageCount = 2 # assign stage count
    model.general.StageDuration = 7.0,35.0 # build up from -7s to 0 to 35s
    print('stage count=',len(model.general.StageDuration)) # stage count
    print('build-up duration=',model.general.StageDuration[0])
    print('final stage duration=',model.general.StageDuration[-1])
    Timestep = model.general.ImplicitConstantTimeStep = 0.1 # same as above
    Max_No_iterations = model.general.ImplicitConstantMaxNumOfIterations = 100 # get max no.of iterations
    return stagecount,model.general.StageDuration,Timestep,Max_No_iterations
general()

# Environmental data
def environment():
    #Environment data
    #water depth
    WaterDepth = model.environment.WaterDepth = 100  # m
    SeaTemperature = model.SeaTemperature = 4   # oC

    #wave
    NumberOfWaveTrains = model.NumberOfWaveTrains =1
    WaveName = model.WaveName = 'wave1'
    WaveType = model.environment.WaveType ='JONSWAP' 
    WaveDirection = model.environment.WaveDirection = 180 
    Hs = model.environment.WaveHs = 6.0
    Tz = model.environment.WaveTz = 7.0

    #current reference speed
    RefCurrentSpeed = model.environment.RefCurrentSpeed = 0.0
    RefCurrentDirection = model.environment.RefCurrentDirection = 180

    #current speed vs. waterdepth profile
    NumberOfCurrentLevels = model.environment.NumberOfCurrentLevels = 3
    CurrentDepth = model.environment.CurrentDepth = 0.0,70.0,100.0   # waterdepth at 0m, 70m, 100m
    CurrentFactor = model.environment.CurrentFactor = 1.0,0.9,0.3 # current value at 1.0,0.9,0.3
    return WaterDepth,SeaTemperature,NumberOfWaveTrains,WaveName,WaveType,WaveDirection,Hs,Tz,
    RefCurrentSpeed,RefCurrentDirection,NumberOfCurrentLevels,CurrentDepth,CurrentFactor
environment()   
    
# Variable data ,set drag coefficient of the line as Variable data items (CD vs.Re)
def dragcoeff():
    CD = model.CreateObject(Orc.otDragCoefficient)# Create a new object
    # drag coeffcient
    CD.DependentValue = 1.2,1.2,1.19,1.16,1.05,0.8,0.42,0.4,0.42,0.48,0.57,0.68,0.7,0.7,0.
    # Reynold number
    CD.IndependentValue = 10e3,50e3,240e3,255e3,300e3,340e3,380e3,425e3,510e3,
                          600e3,675e3,850e3,1.3e6,1.7e6,8.5e6,25e6
    return CD,CD.DependentValue,CD.IndependentValue
dragcoeff()

# vessel model
def vessel():
    vessel = model.CreateObject(OrcFxAPI.otVessel,'FPSO')# create new vessel object called FPSO 
    vessel.Length = 150 
    vessel.VesselType = 'Vessel type1' #set vessel type
    vessel.Connection = 'Free'
    vessel.InitialX,vessel.InitialY,vessel.InitialZ = -35.0,0.0,0.0
    vessel.InitialHeel,vessel.InitialTrim,vessel.InitialHeading= 0.0,0.0,0.0
    return vessel,vessel.Length,vessel.VesselType,vessel.Connection,vessel.InitialX,vessel.InitialY,vessel.InitialZ,
    vessel.InitialHeel,vessel.InitialTrim,vessel.InitialHeading
vessel()

# line model
def line():
    line = model.CreateObject(otLine, 'riser') # Create a new line object assigned as 'riser'
    line.NumberOfSections = 3
    line.Length = [90.0, 30.0, 20.0]
    print(line.Length[0],line.Length[1],line.Length[2])
    line.TargetSegmentLength = 3.0,0.5,3.0
    print(line.TargetSegmentLength[0],line.TargetSegmentLength[1],line.TargetSegmentLength[2])
    line.EndAConnection = vessel.Name
    line.EndBConnection = "Anchored"
    line.EndAX,line.EndAY,line.EndAZ = 37.0,0.0,-7.5
    line.EndBX,line.EndBY,line.EndBZ = line.EndAX + 50, 0.0,0.0
    line.EndAAzmuth,line.EndADeclination,line.EndAGamma = 0.0,171.5,0.0
    line.EndBAzmuth,line.EndBDeclination,line.EndBGamma = 0.0,90.0,0.0
    line.EndBHeightAboveSeabed = 0.0
    return line,line.NumberOfSections,line.Length,line.TargetSegmentLength,line.EndAConnection,
    line.EndBConnection,line.EndAX,line.EndAY,line.EndAZ,line.EndBX,line.EndBY,line.EndBZ,
    line.EndAAzmuth,line.EndADeclination,line.EndAGamma,line.EndBHeightAboveSeabed  
line()

def lineType():
    riserType = model.CreateObject(OrcFxAPI.otLineType) # create linetype
    riserType.Name ='SCR Riser'
    riserType.Category = 'General'
    riserType.WizardCalculation = "Homogenous pipe"  # Homogenous pipe type
    riserType.PipeMaterial = "Steel"           
    riserType.APIRP1111S = 450e3                     # specified minimum yield strength,kPa
    riserType.PipeOuterDiameter = 0.405              # m
    riserType.PipeWallThickness = 0.027              # m
    riserType.ContentsDensity  = 600                 # kg/m3
    riserType.InvokeWizard()
    return riserType,riserType.Name,riserType.Category,riserType.WizardCalculation,riserType.PipeMaterial,
    riserType.PipeOuterDiameter,riserType.PipeWallThickness,riserType.ContentsDensity,riserType.InvokeWizard()
lineType()   
    
# APIRP1111 code design factors to be used for calculating loads
def APIRP1111_designFactors():
    Fa = riserType.APIRP1111Fa = 0.9   # allowable load factor =0.9,0.96,0.96 for functional,extreme and hydrotest respectively
    Fc = riserType.APIRP1111Fc = 0.7   # collapse factor =0.7,0.6 for smls/erw pipe,DSAW respectively
    Fbs = riserType.APIRP1111Fbs = 2.0 # bending safety factor
    return Fa,Fc,Fbs
APIRP1111_designFactors()    

model.save('basecase.dat')  # save model data as a  binary file
model.save('basecase.yml')  # save model data as a text file