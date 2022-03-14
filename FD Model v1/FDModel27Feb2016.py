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


import random

# Global Variables
#

currProd = 0    # total number of products currently being tracked
numTotal = 10   # Total number of empty (Shelly) bins that we have to work with
hPrd = 0.6      # Percentage of bins allocated for high velocity products
sPrd = 0.2      # Percentage of bins allocated for seasonal products
eBin = 1 - hPrd - sPrd  # %age of bins left empty for discretionary use

hPrdInUse = 0
sPrdInUse = 0
eBinInUse = 0

# Overall design principles/details: 

# we will use dictionaries to keep track of products, with keys being product 
# IDs and values being the relevant lifespan of the product

# have a function to create product name, otherwise go to default name

regProdsA = {} #holds the actual lifetime of the outProd
regProdsE = {} #holds the expected remaining lifetime of the outProd
regProdsPair = {} #pairs the outProd with the related inProd
regProdsIn = {} #holds the time until the inProd comes in
garbIn = set()
garbOut = set()

def newRegProd(outProd, inProd, inTime):
    if (outProd == "None"): return 0
    # we want to add outProd to the tracking dict, and when the lifetime is up,
    # bring in the inProd. If outProd is still present, then we have a problem
    # i.e. the inProd needs to use the empty bins
    eTime = 8 #this is arbitrary
    delta = 3 #this is also arbitrary
    regProdsE[outProd] = eTime
    aTime = random.randint(eTime-delta, eTime+delta) #put in a rdm val
    regProdsA[outProd] = aTime
    regProdsPair[inProd] = outProd
    regProdsIn[inProd] = inTime
    print "item added"
    print outProd, inProd, inTime
    return 1

def getPName(name = "None"):
    pName = ""
    if name == "None":
        pName = "product_"+str(currProd)
    else: pName = name
    print pName
    print type(pName)
    return pName
    
# getPName()
# getPName("milk")

def run(n = 1):
    for i in xrange(n): step()
    
def step():
    updateRegProds()
    

def updateRegProds():
    #update all regProd dictionaries to decrement lifetime left
    global eBinInUse
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
                eBinInUse+=1
                print "Line 2: We now have", eBinInUse, "empty bin(s) in use."
                
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

def testRegProc():
    
    newRegProd("milk", "eggs", 3)
    run(10)
    
testRegProc()
