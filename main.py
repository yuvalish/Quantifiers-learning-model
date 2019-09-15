import math
import copy
from random import randrange
import random
import dfa_functions
from dfa_functions import create_built_dfa, resetGlobalIndex

class Num():
    def __init__(self, mod, num):
        self.mod = mod
        self.num = num
        self.bits = 1 + 2 + num+1 #For Num->mod Numbasic, Mod->?, Numbasic->?
        
    def __repr__(self):
        return(self.mod+" "+str(self.num))

    def changeMod(self,new):
        self.mod = new

    def increaseNum(self):
        self.num+=1
        self.bits+=1
             
    def decreaseNum(self): #pre: num>=1#
        self.num-=1
        self.bits-=1

class Quantifier():
    def __init__(self, q_basic, mod, num):
        self.q_basic = q_basic
        node = Node(Num(mod,num))
        self.next = node
        self.len = 1
        self.truth = True
                        
    def __repr__(self): #pre: self.len>=1, we need at least one Num#
        string = ""
        if(self.truth==False):
            string = "not "
        string += self.q_basic
        node = self.next
        #Two possibel rep: if all operators are the same (x op y op z), if not - we need inner ( and )
        if(self.ops_are_same()):
            string+="("
            while(node!=None):
                string+=str(node)
                if(node.operator!=None):
                    string+=" " + node.operator + " "
                node = node.next
            return(string + ")")
        else:
            num_of_ops = self.len-1
            num_of_needed_brackets = self.len-1
            while(node!=None):
                for i in range(num_of_needed_brackets):
                    string+="("
                string+=str(node)
                if(num_of_needed_brackets!=num_of_ops): #If not the first op
                    string+=")"
                if(node.operator!=None):
                    string+=" " + node.operator + " "
                node = node.next
                num_of_needed_brackets-=1
            return(string)

    def makeDFA(self): #pre: self.len>=1, we need at least one Num#
        dfa1 = create_built_dfa(self.q_basic,self.next.data.mod,self.next.data.num)
        node = self.next
        while(node.next!=None):
            dfa2 = create_built_dfa(self.q_basic,node.next.data.mod,node.next.data.num)
            if(node.operator=="or"):
                dfa3 = dfa1.union(dfa2)
                dfa1=dfa3
            elif(node.operator=="and"):
                dfa3 = dfa1.intersection(dfa2)
                dfa1=dfa3    
            node = node.next
        if(self.truth==False):
            dfa2 = dfa1.get_complement()
            dfa1 = dfa2
        return(dfa1)

    def ops_are_same(self): #pre: self.len>=1, we need at least one Num#
        node = self.next
        op = node.operator
        node = node.next
        while(node!=None):
            if(node.operator!=None and op!=node.operator):
                return False                
            node = node.next
        return(True)

    def get_num_of_bits(self):
        s = 3 #For rule Q->QbasicNum and Qbasic->exist/all 
        if(self.truth==False):
            s+=2
        node = self
        while(node.next!=None):
            node = node.next
            s+=node.data.bits #bits for all Nums#
        s+=2*(self.len-1) #bits for operators and conjuctions, 1 for op (or/and) and 1 for Num-> Num con Num#
        return(s)
        
    def changeTruth(self):
        self.truth=not(self.truth)

    def change_q_basic(self,new):
        self.q_basic = new

    def getNodeByIndex(self, index):
        return(getNodeByIndex_static(self, index))

    def insert(self, Num_instance, index, operator):
        insert_static(self, Num_instance, index, operator)

    def delete(self, index): #pre: len>=2, we want at least one Num#
        delete_static(self, index)    

class ComplexQuantifier():
    def __init__ (self,q):
        node = Node(q)
        self.next = node
        self.len = 1

    def __repr__(self): #pre: self.len>=1, we need at least one Quantifier#
        string=""
        node = self.next
        #Two possibel rep: if all operators are the same (x op y op z), if not - we need inner ( and )
        if(self.ops_are_same()):
            string+="("
            while(node!=None):
                string+=str(node)
                if(node.operator!=None):
                    string+=" " + node.operator + " "
                node = node.next
            return(string + ")")
        else:
            num_of_ops = self.len-1
            num_of_needed_brackets = self.len-1
            while(node!=None):
                for i in range(num_of_needed_brackets):
                    string+="("
                string+=str(node)
                if(num_of_needed_brackets!=num_of_ops): #If not the first op
                    string+=")"
                if(node.operator!=None):
                    string+=" " + node.operator + " "
                node = node.next
                num_of_needed_brackets-=1
            return(string)
        
    def ops_are_same(self): #pre: self.len>=1, we need at least one Num#
        node = self.next
        op = node.operator
        node = node.next
        while(node!=None):
            if(node.operator!=None and op!=node.operator):
                return False                
            node = node.next
        return(True)

    def getNodeByIndex(self, index):
        return(getNodeByIndex_static(self, index))

    def insert(self, q, index, operator):
        insert_static(self, q, index, operator)

    def delete(self, index): #pre: len>=2, we want at least one Q#
        delete_static(self, index)

    def getPowerOfG(self): #pre: len>=1, we want at least one quantifier#
        s = 0
        node = self
        while(node.next!=None):
            node = node.next
            s+=node.data.get_num_of_bits() #Bits for all Q 
        s+=3*(self.len-1) #bits for operators and conjuctions, 1 for op (or/and) and 2 for Q con Q#
        return(s)

    def makeDFA(self): #pre: self.len>=1, we need at least one Quantifier#
        resetGlobalIndex()
        node = self.next
        dfa1 = node.data.makeDFA()
        while(node.next!=None):
            dfa2 = node.next.data.makeDFA()
            if(node.operator=="or"):
                dfa3 = dfa1.union(dfa2)
                dfa1=dfa3
            elif(node.operator=="and"):
                dfa3 = dfa1.intersection(dfa2)
                dfa1=dfa3    
            node = node.next
        return(dfa1)
        
    def getPowerOfDG(self,D): #pre: the grammar can create every input in D
        dfa = self.makeDFA()
        power_of_DG=0
        for d in D:
            power_of_DG+=len(dfa.encode_positive_example(d))
        return(power_of_DG)
        
    def checkAcceptance(self, D):
        dfa = self.makeDFA()
        for d in D:
            if(dfa.recognize(d)==False):
                return False
        return True

    def MDL(self,D):
        score = self.getPowerOfDG(D)+self.getPowerOfG()
        return(score)

    def getRandomNeighbor(self,D,maximum):
        lst_of_q_basic = ["exist","all"]
        lst_of_mods=["at least","exactly","at most"]
        applicable = False
        tries=0
        while(tries<10 and applicable==False):
            dup = copy.deepcopy(self)
            index = randrange(self.len)
            q = dup.getNodeByIndex(index).data
            Num_index = randrange(q.len)
            Num_instance = q.getNodeByIndex(Num_index).data
            mod_of_conj = random.choice(lst_of_mods)
            operator_option = randrange(2)
            operator_choice = randrange(2)
            Quantifier_or_Num_choice = randrange(2)
            Num_choice = randrange(2)
            r = randrange(8)
            
            if(r==0): #/If conj in Num lvl or Q lvl
                t=0
                while(t<10 and applicable==False):
                    if(operator_choice==0 and Quantifier_or_Num_choice==0):
                        q_basic_of_conj = random.choice(lst_of_q_basic)
                        applicable = dup.addQuanConjAndReturnApplicability(Quantifier(q_basic_of_conj,mod_of_conj,0),index,D,"or")
                    elif(operator_choice==0 and Quantifier_or_Num_choice==1):
                        applicable = dup.addNumConjAndReturnApplicability(Num(mod_of_conj,0),q,Num_index,D,"or")
                    elif(operator_choice==1 and Quantifier_or_Num_choice==0):
                        q_basic_of_conj = random.choice(lst_of_q_basic)
                        applicable = dup.addQuanConjAndReturnApplicability(Quantifier(q_basic_of_conj,mod_of_conj,0),index,D,"and")
                    elif(operator_choice==1 and Quantifier_or_Num_choice==1):
                        applicable = dup.addNumConjAndReturnApplicability(Num(mod_of_conj,0),q,Num_index,D,"and")
                            
                    if(applicable==False):
                        dup,index,q,Num_index,Num_instance=self.recreate()
                    t+=1
                        
            elif(r==1):
                choice = randrange(2)
                t=0
                while(t<10 and applicable==False):
                    if(choice==0 and self.len>1 and q.len==1 and Num_instance.num==0 and q.truth==True):
                        applicable = dup.deleteQuAndReturnApplicability(index,D)
                    elif(choice==1 and q.len>1 and Num_instance.num==0):
                        applicable = dup.deleteNumAndReturnApplicability(q,Num_index,D)
                        
                    if(applicable==False):   
                        dup,index,q,Num_index,Num_instance=self.recreate()
                    t+=1

            elif(r==2):
                t=0
                while(t<10 and applicable==False):
                    applicable = dup.negQuAndReturnApplicability(q,D)
                    t+=1
                    if(applicable==False):   
                        dup,index,q,Num_index,Num_instance=self.recreate()
                
            elif(r==3):
                t=0
                while(t<10 and applicable==False):
                    applicable = dup.increaseNumAndReturnApplicability(q,Num_index,D)

                    if(applicable==False):   
                        dup,index,q,Num_index,Num_instance=self.recreate()
                    t+=1
                    
            elif(r==4):
                t=0
                while(t<10 and applicable==False):
                    if(Num_instance.num>=1):
                        applicable = dup.decreaseNumAndReturnApplicability(q,Num_index,D)
                        
                    if(applicable==False):   
                        dup,index,q,Num_index,Num_instance=self.recreate()
                    t+=1
                
            elif(r==5):
                t=0
                while(t<10 and applicable==False):
                    if(Num_instance.mod=="exactly"):
                        if(Num_choice==0):
                            applicable = dup.swapModAndReturnApplicability("at most","exactly",q,Num_index,D)
                        else:
                            applicable = dup.swapModAndReturnApplicability("at least","exactly",q,Num_index,D)

                    elif(Num_instance.mod=="at least"):
                        if(Num_choice==0):
                            applicable = dup.swapModAndReturnApplicability("at least","exactly",q,Num_index,D)
                        else:
                            applicable = dup.swapModAndReturnApplicability("at least","at most",q,Num_index,D)

                    elif(Num_instance.mod=="at most"):
                        if(Num_choice==0):
                            applicable = dup.swapModAndReturnApplicability("at most","exactly",q,Num_index,D)
                        else:                    
                            applicable = dup.swapModAndReturnApplicability("at most","at least",q,Num_index,D)
                            
                    if(applicable==False):   
                        dup,index,q,Num_index,Num_instance=self.recreate()                
                    t+=1
                    
            elif(r==6):
                t=0
                while(t<10 and applicable==False):
                    applicable = dup.swapqbasicAndReturnApplicability(q,D)
                    
                    if(applicable==False):   
                        dup,index,q,Num_index,Num_instance=self.recreate()
                    t+=1
                                              
            elif(r==7):
                t=0
                while(t<10 and applicable==False):
                    if(Quantifier_or_Num_choice==0 and dup.getNodeByIndex(index).next!=None):
                        applicable = dup.changeOperator(dup.getNodeByIndex(index),D)
                    elif(Quantifier_or_Num_choice==0 and q.getNodeByIndex(Num_index).next!=None):
                        applicable = dup.changeOperator(q.getNodeByIndex(Num_index),D)    
                    
                    if(applicable==False):   
                        dup,index,q,Num_index,Num_instance=self.recreate()
                    t+=1              
                
            tries+=1
            
        if(applicable):
            return(dup)
        else:
            return(self)
           
    def addQuanConjAndReturnApplicability(self,q,index,D,operator): 
        self.insert(q, index, operator)
        return(self.checkAcceptance(D))

    def addNumConjAndReturnApplicability(self,Num_instance,q,Num_index,D,operator):
        q.insert(Num_instance, Num_index, operator)
        return(self.checkAcceptance(D))

    def deleteQuAndReturnApplicability(self,index,D): #pre: num of quantifiers>=2, we want at least 1#
        self.delete(index)
        return(self.checkAcceptance(D))

    def deleteNumAndReturnApplicability(self,q,Num_index,D): #pre: num of quantifiers>=2, we want at least 1#
        q.delete(Num_index)
        return(self.checkAcceptance(D))

    def negQuAndReturnApplicability(self,q,D):
        q.changeTruth()
        return(self.checkAcceptance(D))

    def increaseNumAndReturnApplicability(self,q,Num_index,D):
        Num_instance_to_increase = q.getNodeByIndex(Num_index).data
        Num_instance_to_increase.increaseNum()
        return(self.checkAcceptance(D))    

    def decreaseNumAndReturnApplicability(self,q,Num_index,D):
        Num_instance_to_decrease = q.getNodeByIndex(Num_index).data
        Num_instance_to_decrease.decreaseNum()
        return(self.checkAcceptance(D))
                      
    def swapModAndReturnApplicability(self,st1,st2,q,Num_index,D):
        Num_instance = q.getNodeByIndex(Num_index).data
        if(Num_instance.mod==st1):
            Num_instance.changeMod(st2)
        else:
            Num_instance.changeMod(st1)
        return(self.checkAcceptance(D))

    def changeOperator(self,node,D):
        if(node.operator=="and"):
            node.operator = "or"
        elif(node.operator=="or"):
            node.operator = "and"
        return(self.checkAcceptance(D))

    def swapqbasicAndReturnApplicability(self,q,D):
        if(q.q_basic=="all"):
            q.q_basic="exist"
        elif(q.q_basic=="exist"):
            q.q_basic="all"
        return(self.checkAcceptance(D))

    def recreate(self):
        dup = copy.deepcopy(self)    
        index = randrange(self.len)
        q = dup.getNodeByIndex(index).data
        Num_index = randrange(q.len)
        Num_instance = q.getNodeByIndex(Num_index).data
        return(dup,index,q,Num_index,Num_instance)
        
class Node():
    def __init__ (self,q):
        self.data = q
        self.next=None
        self.operator=None
        self.headOf=None
        
    def __repr__(self):
        return(str(self.data))    

class SimulatedAnnealing():
    def __init__(self, in_temp, threshold, c_rate):
        self.in_temp = in_temp
        self.threshold = threshold
        self.c_rate = c_rate

    def run(self,D,in_h):
        maximum=0
        for d in D:
            if(len(d)>maximum):
                maximum = len(d) 
        alpha = self.c_rate
        h = in_h
        t = self.in_temp
        while(t>self.threshold):
            #print(t)
            h2 = h.getRandomNeighbor(D,maximum)
            delta = h2.MDL(D) - h.MDL(D)
            if(delta<0):
                p=1
            else:
                p=math.exp(-delta/t)
            r = random.random()
            if(r<p):
                h=h2
            t = alpha*t
            print(h)
        return(h)    


def getNodeByIndex_static(lst, index):
    assert 0 <= index < lst.len
    node = lst.next
    for i in range(0, index):
        node = node.next
    return node

def insert_static(lst, q, index, operator):
    assert 0 <= index < lst.len
    node = lst
    for i in range(0, index):
        node = node.next
    tmp = node.next
    node.next = Node(q)
    node.next.next = tmp
    node.next.operator = operator
    lst.len += 1

def delete_static(lst, index):
    if(index==lst.len-1):
        node = getNodeByIndex_static(lst,index-1)
        node.next=None
        node.operator=None
    else:
        node = lst
        for i in range(0, index):
            node = node.next
        node.next = node.next.next
    lst.len -= 1
