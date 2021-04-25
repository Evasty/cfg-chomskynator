import sys
import utils
import re
from collections import defaultdict,deque
#\eps will be #

msg_stt = "Chomskynator initiating. .." 
msg_end = "Grammar (hopefully) chomskynated "

#don't use 'f' and only single char symbols allowed
terS = []#'a','b','c','d','e']
i_nTerS = []#'A','B','C','D','E','S']
o_nTerS = []
relations = defaultdict( list)# ,{'A':['BC'],'B':['bC'] , 'C':['#','c']})
o_relations = defaultdict(set)  #init with terminal relations
#relations = defaultdict(list,{'A':['BC'],'B':['bC'] , 'C':['#','c'], 'D':['ADBC']})


stSym = 'S'


getRelValues = lambda k : relations[k] if k in relations  else []
addRule = lambda k,v : relations[k].append(v)
inSub = lambda s,l : s in (l)


def grammarLoader():
    gram_in = [x.rstrip() for x in utils.file2list('grammar.txt') if not re.match('\\n|#',x) ] 
    terS.extend(gram_in[0].split(','))
    i_nTerS.extend(gram_in[1].split(','))
    relations.update({ k.rstrip() : (v.strip()).split('|') for k,v in map(lambda x: x.split('->'),gram_in[2:]) })
    o_relations.update({f'{x}_f': set(x) for x in  terS})
    


def grammarSaver():
    out =[]
    out.append('#terminals')
    out.append(','.join(terS))
    out.append('#non-terminals')
    out.append(','. join( sorted(o_relations.keys())))
    out.append('#relations')
    out.extend(map(lambda x: f'{x} -> {f" | ".join(o_relations[x])}', sorted(o_relations )) )
    utils.list2fileW(out,'cnf_gramm.txt')

def printer(msg='',j='rel'):
    print("\n$$$$",msg,)
    if j=='rel':
        for k in relations:
            print(k,'->',relations[k])
    elif j == 'relf':
        for k in sorted(o_relations):
            print(k,'->',o_relations[k])
    else:
            print(j,'->',relations[j])

#rem epsilon
def epsiNator():
    for k in getEpsRels(): # k,no terminal: k -> epsilon
        relations[k].remove('#')
        for l in i_nTerS: # l, no terminal
            for j in getRelValues(l): #j una transición de l
                if k in j and len(j)>1:
                    addRule(l,j.replace(k,'')) ## adds relations removing epsilon

     

def getEpsRels():
    epsRels=[]
    for k in i_nTerS:
        epsRels.append(k) if ('#' in getRelValues(k) ) else print(k,end=', ')
    return epsRels

#rem single trans
def singliNator(): #adds relations replacing single transitions A->B
    singles = singlesFinder()
    singleRedundanceEngine(singles)
    for i in map(lambda a: relations[a],relations):
        for j in i:
            if len(j) == 1:
                i.remove(j)



def singlesFinder():
    singles = defaultdict(set)
    for k in i_nTerS:
        for j in getRelValues(k): #j una transición de k
            if len(j) == 1:
                singles[k].add(j)
    return singles

""" not needed
def singleAnalyzer(singles):
    for k in singles: # k is a symbol : k -> X for some symbol X
        aux = list(singles[k])    #aux holds the transitions of K including higher order ones
        for j in aux: #j are the transitions of 
            if j in singles:
                aux.extend(singles[j]) #set changed size during iter error; using aux list
        singles[k].update(aux)
    return singles
 """

def singleRedundanceEngine(singles):
    #buscar en cada regla los singles y agregar todas las transiciones singulares
    #singles = defaultdict()
    for k in relations:
        aux1 = getRelValues(k)
        for j in aux1:
            for i in singles:
                #map( lambda x: aux1.append(j.replace(i,x))  , singles[i])   
                ##warning this might not add but alter and repeat so..
                if i in j:
                    for x in singles[i]:
                        aux1.append(j.replace(i,x))

"""         A   -> BCDEFGH
            A   -> BA1
            A1  -> CA2
            ... """

#add redundant transitions with len=2

"""
S   -> ABCDEFG...Z
S   -> AS_0
S_0 -> BS_1
S_1 -> CS_2
.
.
.
S_# -> YZ

ABCD
S AS0
S0 BS1
S1 CD

"""
def dualiNator():
    #foreach rh rule w len n > 2 generate  happy things
    nkeys = defaultdict(list) #can't add keys while iterating
    for k in relations:
        for l in getRelValues(k): # adding aux dict
            if len(l)>2 and '_' not in l:
                separator(k, l, nkeys) #add to l the separations of r with prefix k
    relations.update(nkeys)
    

#input grammar ONLY single char symbols required
def separator(prefix , l , dicc ):
    #print(l)
    o_relations[prefix].add(f'{finisher(l[0])}.{prefix}_0')
    for i,j in enumerate(l[1:-2]): # this go 1 by 1
        o_relations[f'{prefix}_{i}'].add(f'{finisher(j)}.{prefix}_{i+1}')
    o_relations[f'{prefix}_{len(l)-3}'].add(f'{finisher(l[-2])}.{finisher(l[-1])}')

def finisher(s):
    for i in terS:
        if i in s:
            s = s.replace(i,f'{i}_f')
    return s

#Transfer relevant rules to chomsky thingy
def grammarChomskynator():
    #find adequate rh rules w len=2 to chomskynate
    for k in relations:
        if len(relations[k])>0:
            deque( map( lambda x : rhrFixer(k,x) if (len(x) == 2) else False, relations[k]),0)
            # weird lambda magic thing happening somewhere here so much fun lols
                
            
    
#will make sure rhr is chomskynated
def rhrFixer(lh,rh):
    #replace terminal w equivalent non-termial
    rhr = f'{rh[0]}_f' if rh[0] in terS else rh[0]
    rhr = f'{rhr}.{rh[1]}_f' if rh[1] in terS else f'{rhr}.{rh[1]}'
    #transfer CNF rule
    return o_relations[lh].add(rhr) #this is so weird but so nice lol

    

def modTest():
    grammarLoader()
    #load grammar from file
    printer('input grammar')
    #epsilon redundance enigne + eliminator
    epsiNator()
    printer("\nepsinator:")
    
    #singles
    singliNator()
    printer("\nsinglinator:")
    
    #2 Symbol redundance engine
    dualiNator()
    printer("\ndualinator:")
    #CHOMSKY MACHINE
    grammarChomskynator()
    printer("\nchomskynated:",'relf')
    grammarSaver()
    
    
    
    #for k in relations:
     #   print(k,'->',relations[k])
#replace multitrans

if __name__ == "__main__":
    print(msg_stt)
    #print(o_relations)
    #print(o_relations)
    modTest()
    print(msg_end)


#### 
""" 
idea: las # también son transiciones singulares
hacer un árbol de a dónde se puede llegar o algo así

 """