#Angel Consulting -- FreshDirect
#Model Implementation v1.0
# CAA 20 Feb 2016
#   Benjamin Hong for Angel Consulting

# Explanation: We need to account for 3 different types of products; 
# High velocity, seasonal, and new products (that replace current products 
# slated for discontinuation). We also need to keep aside a certain amount of 
# empty bins in order to have the flexibility to deal with uncertain situations.

# Each of the product classifications is handled differently in this code, as
# explained later on. 


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
garbIn = []
garbOut = []

def newRegProd(outProd, inProd, inTime):
    if (outProd == "None"): return 0
    # we want to add outProd to the tracking dict, and when the lifetime is up,
    # bring in the inProd. If outProd is still present, then we have a problem
    # i.e. the inProd needs to use the empty bins
    eTime = 8 #this is arbitrary
    delta = 0 #this is also arbitrary
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
    #update all regProd dictionaries to decrement lifetime left
    global eBinInUse
    print "stepping"
    for key in regProdsA: #these are the actual lifetimes of the outgoing Prods
        print "Before dec! regProdsA[",key,"] is", regProdsA[key]
        regProdsA[key] -= 1 #decrement the remaining time
        print "After dec! regProdsA[",key,"] is", regProdsA[key]
        if (regProdsA[key] == 0):
            if (eBinInUse >= 1):
            #there was a product that finished selling, and now there is
            #additional empty bin available
                eBinInUse -= 1
            else:  #eBinInUse <= 0
                # del regProdsA[key]
                # we can stop tracking this product 
                garbOut.append(key)
        elif (regProdsA[key] < 0): 
            print "Warning1! regProdsA[",key,"] is", regProdsA[key]
        #if the lifetime hits zero, the product has run out, well and good.
    
    #this is less important
    for key in regProdsE: 
        regProdsE[key] -= 1 #decrement the remaining time
        if (regProdsE[key] < 0): print "Warning2!"
        
    for key in regProdsIn: 
        regProdsIn[key] -= 1 #decrement the remaining time
        if (regProdsIn[key] == 0): #the new product is coming in
            #we need to check if the corresponding product is OutOfStock
            out = regProdsPair[key]
            if (regProdsA[out] > 0): #this means the outProd is not OOS
                print "we have overlap!"
                eBinInUse+=1
                print "We now have", eBinInUse, "empty bin(s) in use."
            else: 
                #this means the outProd is done selling, there is space
                #we can clear everything from the tracking list
                if (regProdsA[out] < 0): print "This should not be happening"
                del regProdsA[out]
                del regProdsE[out]
                # del regProdsIn[key]
                del regProdsPair[key]
                garbIn.append(key)
            # del regProdsIn[key]
        # if (regProdsIn[key] < 0): print "Warning3!"
        
    # this is garbage collection
    for key in garbIn: del regProdsIn[key]
    for key in garbOut: 
        del regProdsA[key]
        del regProdsE[key]
    #check if any of the lifetimes are zero, and handle accordingly
    
    
    #insert new products into each of the categories if any?
    
    return 0

def testRegProc():
    
    newRegProd("milk", "eggs", 3)
    run(10)
    
testRegProc()
