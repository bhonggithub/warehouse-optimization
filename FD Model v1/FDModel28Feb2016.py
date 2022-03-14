#Angel Consulting -- FreshDirect
#Model Implementation v1.0
# CAA 27 Feb 2016
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

# Global Variables
####################################################################

currProd = 0    # total number of products currently being tracked
numTotal = 10   # Total number of empty (Shelly) bins that we have to work with
hPrd = 0.6      # Percentage of bins allocated for high velocity products
sPrd = 0.2      # Percentage of bins allocated for seasonal products
eBin = 1 - hPrd - sPrd  # %age of bins left empty for discretionary use

hPrdInUse = 0
sPrdInUse = 0
eBinInUse = 0

# number of Shelly bins not in use
binNotInUse = numTotal - hPrdInUse - sPrdInUse - eBinInUse


eTime = 8 #this is arbitrary
delta = 3 #this is also arbitrary

SHVelPoints = 10
HVelPoints = 5
RegPoints = 6
SeasProdBinPoints = 9
EmptyBinPenalty = 5
SeasProdAppPoints = 8

###################################################################

# Overall design principles/details: 

# we will use dictionaries to keep track of products due for replacement, 
# with keys being product IDs and values being the relevant lifespan of the product

totalScore = 0
stepScore = 0

#Regular products
regProdsA = {} #holds the actual lifetime of the outProd
regProdsE = {} #holds the expected remaining lifetime of the outProd
regProdsPair = {} #pairs the outProd with the related inProd
regProdsIn = {} #holds the time until the inProd comes in
garbIn = set()
garbOut = set()

seasProdsA = {}
numSeasProds = len(seasProdsA)



def newRegProd(outProd, inProd, inTime):
    global currProd
    if (outProd == "None"): return 0
    # we want to add outProd to the tracking dict, and when the lifetime is up,
    # bring in the inProd. If outProd is still present, then we have a problem
    # i.e. the inProd needs to use the empty bins
    ###################################################################
    ###################################################################
    regProdsE[outProd] = eTime
    aTime = random.randint(eTime-delta, eTime+delta) #put in a rdm val
    regProdsA[outProd] = aTime
    regProdsPair[inProd] = outProd
    regProdsIn[inProd] = inTime
    currProd += 1
    print "item added"
    print outProd, inProd, inTime
    return 1

# have a function to create product name (incoming and outgoing), 
# otherwise go to default name
def getPName(name = "None"):
    pName = ""
    if name == "None":
        pName = "product_"+str(currProd+1)
    else: pName = name
    print pName
    print type(pName)
    return pName
    
def getRName(name = "None"):
    pName = ""
    if name == "None":
        pName = "inProd_"+str(currProd+1)
    else: pName = name
    print pName
    print type(pName)
    return pName
    
# getPName()
# getPName("milk")

def run(n = 1):
    for i in xrange(n): step()
    
def step():
    #priority: seasonal, then super hiV, regular, hiV
    global hPrdInUse
    global totalScore
    global stepScore
    stepScore = 0
    
    SeasProds = addSeasProds() 
    # while (binNotInUse >= 0):
        # add SeasProds until empty
        # continue
    
    SHVelSuccess = 0
    SHVel = addSHVelProds() #add in new SHV prods, this is only valid in this step
    while ((binNotInUse >= 0) and (SHVel > 0)):
        SHVel -= 1 
        SHVelSuccess += 1
        hPrdInUse += 1
    #amend the score for super hi vel prods and those that we weren't able to add
    stepScore += SHVelSuccess * SHVelPoints
    stepScore -= SHVel * SHVelPoints #the remaining SHVel is the number of SHVel not binned
    
    
    regProds = addRegProds() #add in new reg prods if any in this step
    
    
    
    HVelSuccess = 0
    HVel = addHVelProds() #add in new HV prods, only valid in this step
    while ((binNotInUse >= 0) and (HVel > 0)): 
        HVel -= 1
        HVelSuccess += 1
        hPrdInUse += 1
    #amend the score for hi vel prods and those that we weren't able to add
    stepScore += HVelSuccess * HVelPoints
    stepScore -= HVel * HVelPoints #number of HVel not binned
    
    
    updateSeasProds()    
    updateRegProds() #update the state of the model
    
    #penalty for having empty bins not holding anything
    stepScore -= binNotInUse * EmptyBinPenalty
    
    print "stepScore for this step is", stepScore
    totalScore += stepScore
    print "totalScore is now:", totalScore
    
def addHVelProds():
    # this function is designed to add in new HVel prods (if any)
    # returns a list of candidate hi-vel prods and super hi-vel
    
    #for every period, choose a random number of super hi vel and hi vel prods
    numHi = random.randint(3,6)
      
    return numHi
    
def addSHVelProds():
    # this function is designed to add in new HVel prods (if any)
    # returns a list of candidate hi-vel prods and super hi-vel
    
    #for every period, choose a random number of super hi vel and hi vel prods
    numSuperHi = random.randint(3,6)

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
    
    
    if (numSeasProds >= 1): 
        for key in seasProdsA:
            seasProdsA[key] -= 1
    
    seasCap = sPrd*numTotal
    seasAvail = seasCap - sPrdInUse #available slots for seasonal products
    
    
    return 
    
def addSeasProds(): #TODO
    #this function is designed to add in new seasonal products (if any)
    #populate a dictionary of seasonal product candidates
    #which will be cleared after it has been updated into the model
    
    #first, generate a number of seasonal prods as candidates, then
    #this is where we decide which seasonal prod candidates to accept or rejections
    
    return 0
    
def updateRegProds():
    #update all regProd dictionaries to decrement lifetime left
    global eBinInUse
    global stepScore
    print "stepping"
        
    for key in regProdsIn: 
        regProdsIn[key] -= 1 #decrement the remaining time for incoming prod
        inTimeLeft = regProdsIn[key]
        out = regProdsPair[key]
        regProdsA[out] -= 1 #decrement the outgoing prod time in stock
        regProdsE[out] -= 1 #decrement the expected outgoing prod time in stock
        outTimeLeft = regProdsA[out]
        
        print regProdsIn
        print regProdsPair
        print regProdsA
        print regProdsE
        
        if (inTimeLeft > 0):
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
                print "Line 1: We now have", eBinInUse, "empty bin(s) in use."
                continue
            elif (outTimeLeft < 0):
                #the outgoing product sold out in a previous period, waiting now
                continue
            else: print "Oops2!"
            
            
        elif (inTimeLeft == 0): 
            #the new product is coming in at this step
            #we need to check if the corresponding product is OutOfStock
            if (outTimeLeft == 0): 
                #just nice, the outProd ran out now as well
                # the incoming product will replace the outgoing prod
                garbOut.add(out)
                garbIn.add(key)
                
            elif (outTimeLeft > 0): #this means the outProd is not OOS
                print "we have overlap!"
                if (binNotInUse >= 0):
                    eBinInUse+=1
                    print "Line 2: We now have", eBinInUse, "empty bin(s) in use."
                    stepScore += RegPoints
                else: 
                    #we have no more bins to store this overlap
                    print "Line 0: there are no more empty bins"
                    print "Line 5: We now have", eBinInUse, "empty bin(s) in use."
                    stepScore -= RegPoints
            elif (outTimeLeft < 0):
                #the outProd ran out in a previous period
                #the new product can occupy the old space
                #and the whole transaction is complete
                
                garbOut.add(out)
                garbIn.add(key)
                
            else: #this should not be entered
                print "There's been an error"   
                    
        elif (inTimeLeft < 0):
            #this means that the product has already arrived in a previous step
            #and should have been handled previously
            if (outTimeLeft > 0):
                #we are still waiting for the old product to finish, the new prod is sitting in an empty bin now
                assert(eBinInUse >= 1)
                continue
            elif (outTimeLeft == 0):
                #now the old product has just run out of stock, we can return the empty bin to shelly
                eBinInUse -= 1 
                print "Line 3: We now have", eBinInUse, "empty bin(s) in use."
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
    print "we got to here"
    print ""
    print "garbIn is:", garbIn
    print "regProdsIn is", regProdsIn
    print "regProdsPair is", regProdsPair
    print "garbOut is", garbOut
    print "regProdsA is", regProdsA
    print "regProdsE is", regProdsE
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

def addRegProds():
    #this function is designed to add in new regular products (if any)
    #at each step 
    numRegProds = random.randint(1,2)
    for i in xrange(numRegProds):
        #
        newRegProd(getPName(), getRName(), random.randint(2,4))
    return numRegProds
    
def testRegProc():
    #adding new products
    # newRegProd("milk", "eggs", 3)
    # newRegProd("yoghurt", "cheese", 2)
    # newRegProd(getPName(), getRName(),2)
    #running across time periods
    run(10)
    
testRegProc()
