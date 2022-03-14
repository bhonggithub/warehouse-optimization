#Angel Consulting -- FreshDirect
#Model Implementation v1.0
# CAA 8 Apr 2016
#   Benjamin Hong for Angel Consulting

# Explanation: We need to account for 3 different types of products; 
# High velocity, seasonal, and new products (that replace current products 
# slated for discontinuation). We also need to keep aside a certain amount of 
# empty bins in order to have the flexibility to deal with uncertain situations.

# Each of the product classifications is handled differently in this code, as
# explained later on. 

#Changelog 
#28 Feb 2016 1259hrs: Fixed how regular products and overlaps are handled
#28 Feb 2016 1609hrs: Added skeleton for how hi-v and seasonal products fit into the code
#29 Feb 2016 0122hrs: Added code for how hi-v and super hi-v products are handled + scoring
#29 Feb 2016 1218hrs: Added code for readability and fixed a bug where we weren't decrementing the empty bins correctly
#29 Feb 2016 1532hrs: Added code to add new seasonal products based on whether the schedule can accommodate
#1 Mar 2016 0042hrs: Added code to update seasonal products, potential MVP
#1 Mar 2016 0107hrs: Tidied up print statements and commented out some debugging statements
#1 Mar 2016 1415hrs: fixed minor bug where sProd schedule was not decremented
#1 Mar 2016 1542hrs: added code to run each run multiple times and across multiple empty percentages
#1 Mar 2016 2227hrs: fixed bug where seasonal products weren't clearing correctly

# What we need at the end of each period:
# (scores are arbitrary for now)

# Arrival situation
# 1.High velocity products DONE
# - number of super-high velocity products that need to be double binned (high priority) 
# --> for each product, if binned, score = 10, otherwise score = -10 

# - number of high velocity products that need to be double binned (mid priority) 
# --> for each product, if binned, score = 5, otherwise score = -5

# 2. Regular products (overlapping) 
# - number of overlapping products (outprod not out yet, inprod comes in) 
# --> for each product, if binned, score = 6, otherwise score = -6

# 3. Seasonal products
# - number of seasonal products coming in --> for each product, if binned, score = 9, otherwise score = -9

# Number of empty bins = x 
# --> priority: 1) seasonal, 2) super-high velocity, 3) overlapping regular, 4) high velocity (is there a way to code this?)
# --> Score = sum across all products binned and not binned

# Warehouse Situation
# --> after binning all the products --> number of empty bins at the end of period --> Score = -5*number of empty bins

# Decision process
# Seasonal products:
# - number of seasonal product requests approved (based on expected number of available bins)
# --> Score = 8*number of approvals 
# --> Score = -8*number of rejections

# [- Assume: number of bins shelly allocates to seasonal products = 2     
# & shelf life of seasonal products = 6 weeks (basically assume no uncertainty in discontinuing/lead time)
# - need to track: expected number of bins (out of the 2) available in period i+10 (assume fixed lead time) 
# - we may need a vector (that is updated at the end of each period) to track this: at any one point in time, know how many seasonal products there will be in i+1, i+2, i+3..., i+9]

# *for regular products there is no decision process because as long as merchant discontinues an existing product, shelly will approve.

import random
import sys
from randomVars import *
###################################################################
### Global Variables (for tweaking)
####################################################################

#TODO 8 Apr: DECIDED each period is 1 day, but sProd and regular products are only requested and approved every 7 days. HVel are still done on a daily basis
#TODO: refactor code to make it easy to run in 9 instances with different params, sum the total score for display


#TODO: insert uncertainty into lifetime to sProd + see how we can include lifetime ot HVel prod?
# at what rate do you accept new HVel prods?
##################
### CHANGE HERE
##################
warehouseTotal = 160
##################
##################

emptyPercent = 0.02 #this should be being changed
numTotal = int(warehouseTotal*emptyPercent)   # Total number of empty (Shelly) bins that we have to work with
hPrd = 0.6      # Percentage of bins allocated for high velocity products
sPrd = 0.2      # Percentage of bins allocated for seasonal products
eBin = 1 - hPrd - sPrd  # %age of bins left empty for discretionary use

###########################################################################
#TODO: need to find, for each of the 3 depts, the average discontinuing time for each prod and the distribution
# for each dept we will have a different time and diff delta
###########################################################################

#######################################
### Regular Products
#######################################


##################
### CHANGE HERE
##################
oTime = 26.5306 #this is the arbitrary expected time for regular product to be OOS
oDelta = 3 #this is the arbitrary variance for reg prod OOS


disconParams = (2, 49, 0.019375306, 0.02, 0.02062469)
disconArr = genCDF(disconParams)


aTime = 10 #mean time for the arrival of incoming reg prod
aDelta = 3 #variance for incoming reg prod
#TODO: we should find the actual incoming time and the variance. we propose that it should be the same for the 3 depts

##################
##################

#########################################
### Seasonal Products
#########################################

###############
### CHANGE HERE
###############

arrTime = 10 #arbitrary arrival time for new sProd candidate
shelfTime = 42 #arbitrary OOS time for new sProd candidate
#TODO: shelfTime for seasonal products in different departments should be different 

################
################

############################################
### Distribution of candidates
############################################
#TODO: Ben proposes the distribution for candidates is the same across all depts, but params changed
# Issue: hard to determine category of rejected products (Arthur suggests look at internet)

# maxSHVel = 14 #number of candidates for super hi vel is random(0,maxSHVel)
# maxHVel = 14 #number of candidates for hi vel is random(0,maxHVel)
# maxRegProd = 2 #number of reg prod pairs being swapped is random(0,maxRegProd)
# maxSProd = 1 #number of seasonal prod candidates is random(0,maxSProd)

###############
### CHANGE HERE
###############

regInputParams = (0, 3, 0.14333333, 0.25, 0.35666666) #A, L, first, middle, last
regReqArr = genCDF(regInputParams)

seasInputParams = (0, 2, 0.94, 0.05, 0.01)
seasReqArr = genCDF(seasInputParams)

HInputParams = (6, 7, 0.111142857, 0.125, 0.138857143)
HReqArr = genCDF(HInputParams)

SHInputParams = (4, 5, 0.1870666666, 0.166666666, 0.1462666666)
SHReqArr = genCDF(SHInputParams)

################
################

### Situation Scores

SHVelPoints = 10 #score for binning super high velocity product (a)
HVelPoints = 6 #score for binning high velocity product (b)
RegPoints = 9 # score for successfully binning an overlap (d)
SeasProdBinPoints = 14 # score for actually binning a new seasonal product (c)
EmptyBinPenalty = 1 # penalty for leaving a bin empty in each period (f)
SeasProdAppPoints = 2 # score for approving a new seasonal product (e)
###################################################################
###################################################################
# Overall design principles/details: 

# we will use dictionaries to keep track of products due for replacement, 
# with keys being product IDs and values being the relevant lifespan of the product
DBG = False

###################################################################
### Initial Values
###################################################################
currProd = 0    # total number of products currently being tracked
hPrdInUse = 0
sPrdInUse = 0
eBinInUse = 0
# number of Shelly bins not in use
binNotInUse = numTotal - hPrdInUse - sPrdInUse - eBinInUse


seasCap = sPrd*numTotal #this is the total number of bins avail for sProds
seasAvail = seasCap - sPrdInUse #total available slots for sProds

totalScore = 0
stepScore = 0
###################################################################

#Regular Products
regProdsA = {} #holds the actual lifetime of the outProd
regProdsE = {} #holds the expected remaining lifetime of the outProd
regProdsPair = {} #pairs the outProd with the related inProd
regProdsIn = {} #holds the time until the inProd comes in
garbIn = set()
garbOut = set()


#Seasonal Products
sArriveTimes = {} #time to arrival for approved products
sStockTimes = {} #time until out of stock for approved products
sGarb = set()


numSeasProds = len(sArriveTimes)
sOccTime = {} #keeps track of how long each seasonal slot is scheduled to be occupied

###################################################################
### Functions
###################################################################
def initSeasTracking():
    for i in xrange(int(sPrd*numTotal)):
        sOccTime["sProd"+str(i+1)] = 0
    print "sOccTime is", sOccTime

def reinitRun():
    global currProd
    global hPrdInUse
    global sPrdInUse
    global eBinInUse
    global binNotInUse
    global seasCap
    global seasAvail
    global totalScore
    global stepScore
    global regProdsA
    global regProdsE
    global regProdsPair
    global regProdsIn 
    global garbIn
    global garbOut

    #Seasonal Products
    global sArriveTimes
    global sStockTimes
    global sGarb

    global numSeasProds
    global sOccTime
    
    currProd = 0    # total number of products currently being tracked
    hPrdInUse = 0
    sPrdInUse = 0
    eBinInUse = 0
    # number of Shelly bins not in use
    binNotInUse = numTotal - hPrdInUse - sPrdInUse - eBinInUse


    seasCap = sPrd*numTotal #this is the total number of bins avail for sProds
    seasAvail = seasCap - sPrdInUse #total available slots for sProds

    totalScore = 0
    stepScore = 0
    ###################################################################

    #Regular Products
    regProdsA = {} #holds the actual lifetime of the outProd
    regProdsE = {} #holds the expected remaining lifetime of the outProd
    regProdsPair = {} #pairs the outProd with the related inProd
    regProdsIn = {} #holds the time until the inProd comes in
    garbIn = set()
    garbOut = set()


    #Seasonal Products
    sArriveTimes = {} #time to arrival for approved products
    sStockTimes = {} #time until out of stock for approved products
    sGarb = set()


    numSeasProds = len(sArriveTimes)
    sOccTime = {} #keeps track of how long each seasonal slot is scheduled to be occupied
    return
    
def updateBinState():
    global binNotInUse
    global seasAvail
    global numTotal 
    global seasCap
    numTotal = int(warehouseTotal*emptyPercent) 
    binNotInUse = numTotal - hPrdInUse - sPrdInUse - eBinInUse
    seasCap = sPrd*numTotal
    seasAvail = min(seasCap, binNotInUse) - sPrdInUse #total available slots for sProds
    return
    
def dispBinState():
    if (DBG): print "################################"
    if (DBG): print "binNotInUse is", binNotInUse
    if (DBG): print "numTotal is", numTotal
    if (DBG): print "hPrdInUse is", hPrdInUse
    if (DBG): print "sPrdInUse is", sPrdInUse
    if (DBG): print "eBinInUse is", eBinInUse
    if (DBG): print "################################"


def newRegProd(outProd, inProd):
    global currProd
    if (outProd == "None"): return 0
    # we want to add outProd to the tracking dict, and when the lifetime is up,
    # bring in the inProd. If outProd is still present, then we have a problem
    # i.e. the inProd needs to use the empty bins
    ###################################################################
    ###################################################################
    regProdsE[outProd] = oTime
    ##################
    ### CHANGE HERE
    ##################
    # actualTime = random.randint(oTime-oDelta, oTime+oDelta) #put in a rdm val
    actualTime = genRV(disconArr, disconParams)
    inTime = random.randint(aTime-aDelta, aTime+aDelta)
    ##################
    ##################
    regProdsA[outProd] = actualTime
    regProdsPair[inProd] = outProd
    regProdsIn[inProd] = inTime
    currProd += 1
    if (DBG): print "item added"
    if (DBG): print outProd, inProd, inTime
    return 0

# have a function to create product name (incoming and outgoing), 
# otherwise go to default name
def getPName(name = "None"):
    pName = ""
    if name == "None":
        pName = "product_"+str(currProd+1)
    else: pName = name
    # print pName
    # print type(pName)
    return pName
    
def getRName(name = "None"):
    pName = ""
    if name == "None":
        pName = "inProd_"+str(currProd+1)
    else: pName = name
    # print pName
    # print type(pName)
    return pName
    
#function to create name for seasonal product
def getSName(name = "None"):
    pName = ""
    if name == "None":
        pName = "sProd_"+str(currProd+1)
    else: pName = name
    if (DBG): print pName
    if (DBG): print type(pName)
    return pName
# getPName()
# getPName("milk")

def run(n = 1):
    reinitRun()
    initSeasTracking()
    print "ThiS IS A NEW RUN"
    print "emptyPercent is", emptyPercent
    for i in xrange(n): 
        print "this is period", i
        step(i)
        print "totalScore after run is", totalScore
    
def step(period):
    #priority: seasonal, then super hiV, regular, hiV
    global hPrdInUse
    global totalScore
    global stepScore
    print "\n NEW STEP this is period", period, "\n"
    stepScore = 0
    hPrdInUse = 0
    updateBinState()
    #this should be generating seasonal candidates, and accepting/rejecting based
    #on availability in the seasonal section model
    if (DBG): print "here, sOccTime is", sOccTime
    SeasProds = addSeasProds(period) 
    
    #this should be updating the seasonal section, plus handling the actual binning on arrival
    updateSeasProds()    
    
    
    SHVelSuccess = 0
    SHVel = addSHVelProds() #add in new SHV prods, this is only valid in this step
    if (DBG): print "we have", SHVel, "candidate(s) in the SHVel pool this step"
    while ((binNotInUse > 0) and (SHVel > 0)):
        SHVel -= 1 
        SHVelSuccess += 1
        hPrdInUse += 1
        updateBinState()
        dispBinState()  
    #amend the score for super hi vel prods and those that we weren't able to add
    stepScore += SHVelSuccess * SHVelPoints
    if (DBG): print "we were able to bin", SHVelSuccess, "SHVel Prod(s), add", SHVelPoints,"points to stepScore for each, +", SHVelSuccess*SHVelPoints, "total points"
    stepScore -= SHVel * SHVelPoints #the remaining SHVel is the number of SHVel not binned
    if (DBG): print "we were not able to bin", SHVel, "SHVel Prod(s), minus", SHVelPoints,"points to stepScore for each, -", SHVel*SHVelPoints, "total points"
    
    if (DBG): print "WE GOT TO THIS POINT CORRECTLY"
    regProds = addRegProds(period) #add in new reg prods if any in this step
    updateRegProds() #update the state of the model
    
    
    
    HVelSuccess = 0
    HVel = addHVelProds() #add in new HV prods, only valid in this step
    if (DBG): print "we have", HVel, "candidate(s) in the HVel pool this step"
    while ((binNotInUse > 0) and (HVel > 0)): 
        HVel -= 1
        HVelSuccess += 1
        hPrdInUse += 1
        updateBinState()
        dispBinState()
    #amend the score for hi vel prods and those that we weren't able to add
    stepScore += HVelSuccess * HVelPoints
    if (DBG): print "we were able to bin", HVelSuccess, "HVel Prod(s), add", HVelPoints,"points to stepScore for each, +", HVelSuccess*HVelPoints, "total points"
    # if (DBG): print "we were able to bin a HVel Prod, add", HVelPoints,"points to stepScore for", HVelSuccess, "HV products"
    stepScore -= HVel * HVelPoints #number of HVel not binned
    # if (DBG): print "we were not able to bin a HVel Prod, minus", HVelPoints,"points to stepScore for", HVel, "HV products, total", HVel*HVelPoints
    if (DBG): print "we were not able to bin", HVel, "HVel Prod(s), minus", HVelPoints,"points to stepScore for each, -", HVel*HVelPoints, "total points"
    
    
    
    #penalty for having empty bins not holding anything
    stepScore -= binNotInUse * EmptyBinPenalty
    if (DBG): print "we have", binNotInUse, "bins not in use, a penalty of", EmptyBinPenalty, "for each empty bin, total -", binNotInUse * EmptyBinPenalty
    
    if (DBG): print "################################"
    if (DBG): print "binNotInUse is", binNotInUse
    if (DBG): print "hPrdInUse is", hPrdInUse
    if (DBG): print "sPrdInUse is", sPrdInUse
    if (DBG): print "eBinInUse is", eBinInUse
    if (DBG): print "stepScore for this step is", stepScore
    totalScore += stepScore
    if (DBG): print "totalScore is now:", totalScore
    if (DBG): print "################################"
    if (DBG): print "\n END OF NEW STEP \n"
    
def addHVelProds():
    # this function is designed to add in new HVel prods (if any)
    # returns a list of candidate hi-vel prods
    #for every period, choose a random number of hi vel prods
    ################################
    ### CHANGE THIS
    ################################
    # numHi = random.randint(0,maxHVel) #arbitrary
    numHi = genRV(HReqArr, HInputParams)
    ################################
    ################################
    return numHi
    
def addSHVelProds():
    # this function is designed to add in new SHVel prods (if any)
    # returns a list of candidate super hi-vel prods
    #for every period, choose a random number of super hi vel prods
    ################################
    ### CHANGE THIS
    ################################
    # numSuperHi = random.randint(0,maxSHVel) #arbitrary
    numSuperHi = genRV(SHReqArr, SHInputParams)
    ################################
    ################################
    return numSuperHi
    
def updateSeasProds(): #TODO
    # we assume that seasonal products will go OOS in a fixed time interval.
    # we also assume that seasonal products will arrive in a known time frame.
    # we receive a random number of seasonal product requests each period, 
    # and we have to check if there is forecasted space to accept the new 
    # seasonal products
    
    # we keep track of current seasonal products (either already present or we
    # know that they are coming in; we don't distinguish between the two (assumption))
    # we compare the time that new seasonal product candidates are coming in and we 
    # decide if we can accept them
    
    # Qn: how do we generate number of seasonal prod candidates and their time to arrival?
    
    #decrement the remaining time in stock for each item
    
    global sPrdInUse
    global stepScore
    if (DBG): print "stepping sProds"
    
    # seasAvail = seasCap - sPrdInUse #total available slots for sProds
    if (DBG): print "sArriveTimes is", sArriveTimes
    if (DBG): print "sStockTimes is", sStockTimes
    
    assert(len(sArriveTimes) == len(sStockTimes))
    
    for key in sArriveTimes:
        sArriveTimes[key] -= 1  #decrement the time to arrival for each sProd
        sStockTimes[key] -= 1 #decrement the time to OOS for each sProd
        sArrTimeLeft = sArriveTimes[key]
        sStkTimeLeft = sStockTimes[key]
        if (DBG): print "seas key is", key
        if (DBG): print "sArrTimeLeft is", sArrTimeLeft
        if (DBG): print "sStkTimeLeft is", sStkTimeLeft
        assert(sArrTimeLeft < sStkTimeLeft)
        
        if (sArrTimeLeft > 0): #the seasonal product isn't in yet, no worries
            
            
            continue
        elif (sArrTimeLeft == 0):
            #try to put the seasonal product in one of the seasonal bins
            if (seasAvail > 0):
                #there is space for the seasonal product
                sPrdInUse += 1
                updateBinState()
                if (DBG): print "Line 319: We now have", sPrdInUse, "seas bin(s) in use."
                stepScore += SeasProdBinPoints
                if (DBG): print "we were able to bin a sProd, add (+)", SeasProdBinPoints,"points to stepScore"
            else:
                #we have no bins available for the sProd
                if (DBG): print "Line 0: there are no more empty bins for sProds"
                if (DBG): print "Line 5: We now have", sPrdInUse, "seasonal bin(s) in use."
                updateBinState()
                stepScore -= SeasProdBinPoints
                if (DBG): print "we were not able to bin a sProd, subtract (-)", SeasProdBinPoints,"points from stepScore"
                
            # continue
        elif (sArrTimeLeft < 0):
            #the sProd should already have been in the bin, or discarded
            
            if (sStkTimeLeft == 0): #the product is now out of stock
                assert(sPrdInUse >= 1)
                sGarb.add(key)
                
                
        else: 
            if (DBG): print "Oopsx2"
        
    #garbage collection step, for sProds that we are no longer tracking
    for key in sGarb:
        if (DBG): print "we are clearing", key
        del sArriveTimes[key]
        del sStockTimes[key]
    sGarb.clear()
    return 0
    
def addSeasProds(period): 
    #this function is designed to add in new seasonal products (if any)
    #populate a dictionary of seasonal product candidates
    #which will be cleared after it has been updated into the model
    
    #first, generate a number of seasonal prods as candidates, then
    #this is where we decide which seasonal prod candidates to accept or rejections

    global stepScore
    
    
    #decrement the scheduled (?) occupied time in each period
    for key in sOccTime:
        sOccTime[key] -= 1
    
    # we are not at the beginning of the week, so no new seasonal products
    if (period%7 != 0): return 0 
    
    ################################
    ### CHANGE THIS
    ################################
    # numSeasCand = random.randint(0,maxSProd)
    numSeasCand = genRV(seasReqArr, seasInputParams)
    # numSeasCand = 2 #for testing purposes
    #these products are going to arrive in arrTime, and last for shelfTime
    # arrTime = 6 #arbitrary
    # shelfTime = 10 #arbitrary
    ################################
    ################################
    if (DBG): print "we have", numSeasCand, "seasonal prod candidates"
    
    for i in xrange(numSeasCand):
        earlyAccomTime = sys.maxsize #this is the earliest we can accommodate another sProd
        earlyAccomSlot = "None"
        for key in sOccTime: 
            if (sOccTime[key] < earlyAccomTime): 
                earlyAccomTime = sOccTime[key]
                earlyAccomSlot = key
                
        if (DBG): print "sOccTime is", sOccTime
        if (DBG): print "earlyAccomSlot is", earlyAccomSlot
        if (DBG): print "earlyAccomTime is", earlyAccomTime
        #now earlyAccomTime has the smallest occupied time of the sProd space
        # and earlyAccomSlot is the space where the new sProd can be scheduled
        
        #if they can fit into the earliest space, then register the sProd
        if (arrTime > earlyAccomTime):
            #we know that the sProd will come in when there is space for it
            # we can register the new sProd
            newSeasProd(getSName(), arrTime, shelfTime)
            #now the slot is occupied for the entire arrTime + shelfTime
            sOccTime[earlyAccomSlot] = earlyAccomTime + arrTime + shelfTime
            stepScore += SeasProdAppPoints
            if (DBG): print "we were able to approve a sProd, add (+)", SeasProdAppPoints,"points to stepScore for 1 sProd"
        else: 
            stepScore -= SeasProdAppPoints
            if (DBG): print "we were not able to approve a sProd, minus (-)", SeasProdAppPoints,"points to stepScore for 1 sProd"
            continue #now we check the next sProd candidate
    
    return 0

def newSeasProd(sProd, arrivalTime, shelflifeTime):
    global currProd
    sArriveTimes[sProd] = arrivalTime
    sStockTimes[sProd] = arrivalTime+shelflifeTime #this is the time until out of stock
    currProd += 1
    if (DBG): print "sProd added"
    if (DBG): print sProd, arrivalTime, shelflifeTime
    return
    
def updateRegProds():
    #update all regProd dictionaries to decrement lifetime left
    global eBinInUse
    global stepScore
    if (DBG): print "stepping reg prods"
    if (DBG): dispBinState()    
        
    for key in regProdsIn: 
        regProdsIn[key] -= 1 #decrement the remaining time for incoming prod
        inTimeLeft = regProdsIn[key]
        out = regProdsPair[key]
        regProdsA[out] -= 1 #decrement the outgoing prod time in stock
        regProdsE[out] -= 1 #decrement the expected outgoing prod time in stock
        outTimeLeft = regProdsA[out]
        
        # if (DBG): print "key is", key
        # if (DBG): print "out is", out
        # if (DBG): print "regProdsIn is", regProdsIn
        # if (DBG): print "regProdsPair is", regProdsPair
        # if (DBG): print "regProdsA is", regProdsA
        # if (DBG): print "regProdsE is", regProdsE
        # if (DBG): print "inTimeLeft is", inTimeLeft
        # if (DBG): print "outTimeLeft is", outTimeLeft
        
        if (inTimeLeft > 0):
            if (DBG): print "whoops1"
            #this means the new product has not come in yet in this step
            # we don't have to check anything
            if (outTimeLeft > 0): 
                #the outgoing product has not sold out yet either, continue
                continue
            elif (outTimeLeft == 0): 
                #the outgoing product has just sold out, the bin is ready 
                #for the new product
                if (eBinInUse >= 1):
                    eBinInUse -= 1 # if there was previous overlap here for another product, now we can return the shelly bin
                    updateBinState()
                if (DBG): print "Line 1: We now have", eBinInUse, "empty bin(s) in use."
                continue
            elif (outTimeLeft < 0):
                #the outgoing product sold out in a previous period, waiting now
                continue
            else: 
                if (DBG): print "Oops2!"
            
            
        elif (inTimeLeft == 0): 
            if (DBG): print "whoops2"
            #the new product is coming in at this step
            #we need to check if the corresponding product is OutOfStock
            if (outTimeLeft == 0): 
                #just nice, the outProd ran out now as well
                # the incoming product will replace the outgoing prod
                garbOut.add(out)
                garbIn.add(key)
                
            elif (outTimeLeft != 0): 
                #this means the outProd either not OOS or already OOS earlier
                #so we need a new empty bin from the pool for the incoming prod
                if (DBG): print "we have overlap!"
                if (DBG): print "binNotInUse is", binNotInUse
                if (DBG): print "incoming prod is", key
                if (DBG): print "time left to incoming is", inTimeLeft
                if (DBG): print "outgoing prod is", out
                if (DBG): print "time left to outgoing is", outTimeLeft
                
                if (binNotInUse > 0):
                    eBinInUse+=1
                    updateBinState()
                    print "Line 2: We now have", eBinInUse, "empty bin(s) in use."
                    stepScore += RegPoints
                    print "we were able to bin an overlap, add (+)", RegPoints,"points to stepScore"
                else: 
                    #we have no more bins to store this overlap
                    print "Line 0: there are no more empty bins"
                    print "Line 5: We now have", eBinInUse, "empty bin(s) in use."
                    updateBinState()
                    stepScore -= RegPoints
                    #we have to discard the incoming product, and we can stop tracking this pair
                    garbOut.add(out)
                    garbIn.add(key)
                    print "we were not able to bin an overlap, subtract (-)", RegPoints,"points to stepScore"
            # elif (outTimeLeft < 0):
                # the outProd ran out in a previous period
                # the new product can occupy the old space
                # and the whole transaction is complete
                
                # BUT WAIT
                # this means that the empty bin was already returned to the pool
                # the new product needs to draw another empty bin
                # garbOut.add(out)
                # garbIn.add(key)
                
                
            else: #this should not be entered
                print "There's been an error"   
                assert(False)
                    
        elif (inTimeLeft < 0):
            if (DBG): 
                print "whoops3"
                print "inTimeLeft is", inTimeLeft
                print "outTimeLeft is", outTimeLeft
                print "key is", key
                print regProdsA
                print regProdsE
                print regProdsIn
                print regProdsPair
                dispBinState()
            #this means that the product has already arrived in a previous step
            #and should have been handled previously
            if (outTimeLeft > 0):
                #we are still waiting for the old product to finish, the new prod is sitting in an empty bin now
                continue
            elif (outTimeLeft == 0):
                #now the old product has just run out of stock, we can return the empty bin to shelly
                
                if (eBinInUse >= 1):
                    eBinInUse -= 1 
                    updateBinState()
                if (DBG): print "Line 3: We now have", eBinInUse, "empty bin(s) in use."
            elif (outTimeLeft < 0):
                #old prod has run out, new prod has alr come in previously
                garbIn.add(key)
                garbOut.add(out)
            else:
                print "Another error..."
            # print "We shouldn't be entering here either"
            
        else: print "Oops!"

    
    # after iterating through all the keys in ProdIn and ProdOut, we know which 
    # ones we need to keep around and which we can clear
    # this is garbage collection
    # print "we got to here"
    print ""
    # print "garbIn is:", garbIn
    # print "regProdsIn is", regProdsIn
    # print "regProdsPair is", regProdsPair
    # print "garbOut is", garbOut
    # print "regProdsA is", regProdsA
    # print "regProdsE is", regProdsE
    print ""
    for key in garbIn: 
        del regProdsIn[key]
        del regProdsPair[key]
    for key in garbOut: 
        del regProdsA[key]
        del regProdsE[key]
    garbIn.clear()
    garbOut.clear()
    return 0

def addRegProds(period):
    #this function is designed to add in new regular products (if any)
    #at each step 
    
    #we are not at the beginning of the week, so no new reg products to add
    if (period%7 != 0): return 0
    else:
        ################################
        ### CHANGE THIS
        ################################
        # numRegProds = random.randint(0,maxRegProd)
        numRegProds = genRV(regReqArr, regInputParams)
        # numRegProds = 2
        ################################
        ################################
        for i in xrange(numRegProds):
            # newRegProd(getPName(), getRName(), random.randint(2,4))
            newRegProd(getPName(), getRName())
        return numRegProds
    
def testRegProc():
    #adding new products
    # newRegProd("milk", "eggs", 3)
    # newRegProd("yoghurt", "cheese", 2)
    # newRegProd(getPName(), getRName(),2)
    #running across time periods
    initSeasTracking()
    run(300)
    print "totalScore being returned is", totalScore
    return totalScore
    
    


def aggregate():
    # testPercent = [0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
    
    global emptyPercent
    
    testPercent = []
    
    # testPercent.append(0.001)
    # testPercent.append(0.005)
    for i in xrange(20):
        testPercent.append(i*0.01)
    print testPercent
    
    
    
    testResult = []
    n = 5
    aggScore = 0
    runScore = 0
    
    for element in testPercent:
        emptyPercent = element
        updateBinState()
        aggScore = 0
        for i in xrange(n):
            
            runScore = testRegProc()
            print "we have finished one sequence of 100 periods"
            print "runScore at this stage is", runScore
            print "this was simulation number", i
            print "param is", emptyPercent
            print ""
            aggScore += runScore
            runScore = 0
        
        meanScore = aggScore/n
        
        testResult.append(meanScore)
    
    assert(len(testPercent) == len(testResult))
    
    for i in xrange(len(testPercent)):
        print "param is", testPercent[i], "; average score is", testResult[i] 
    # testRegProc()
    return
    
    
    
aggregate()
# testRegProc()