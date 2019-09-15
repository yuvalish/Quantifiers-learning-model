"""
A class representing a Deterministic Finite Automaton (DFA) over any finite alphabet.
"""
from printer import info
import datetime
import os
from collections import defaultdict
from graphviz import Digraph
import copy
from quantifier_creator import create_built_dfa_and_return_total_index

PENALTY_EXISTING_TRANSITION = 5
index_total_states = 0

class DFA:
    def __init__(self, states, transitions, initial, accepting,raise_index_total_states=True):
        """
        Initializes a DFA instance.
        
        @param states: The names of the states of the DFA.
        @param transitions: the transitions of the DFA, as a dictionary where each key-value pair
                            is of the form state: {letter1: next state, ..., letterN: next state},
                            where letter1, ..., letterN are the letters of the alphabet.}
        @param initial: the name of the initial state.
        @param accepting: The names of the accepting states.
        """
        self.states = states
        self.transitions = transitions
        self.initial = initial
        self.accepting = accepting
        if(raise_index_total_states):
            global index_total_states
            index_total_states+=len(self.states)

    def __eq__(self, other):
        # info('self:', self, 'other:', other, sep='\n')
        return isinstance(other, DFA) and \
               self.states == other.states and \
               self.transitions == other.transitions and \
               self.initial == other.initial and \
               self.accepting == other.accepting

    def __str__(self):
        to_string = ""
        to_string += "states: "
        to_string += str(self.states) + '\n'
        to_string += "accepting states: "
        if len(self.accepting) == 0:
            to_string += "empty set.\n"
        else:
            to_string += str(self.accepting) + '\n'
        to_string += "transitions: "
        to_string += str(self.transitions)
        return to_string

    def recognize(self, word):
        """
        Decides whether a given word is in the language of the DFA.

        @param word: The word to decide.
        @return: Whether or not the word is in the language of the DFA.
        """
        curr_state = self.initial
        for letter in word:
            try:
                curr_state = self.transitions[curr_state][letter]
            except KeyError:
                # If no transition is defined for the current state and letter, then the DFA rejects the word.
                return False
        return curr_state in self.accepting

    def tmp_delete_word_end_trans(self):
        """
        takes DFA with one accepting state, that the transition/s led to it is #, and return DFA without this state
        and without those # transitions. The states that led with # transition to the former accepting state are now
        accepting states
        """
        new_accepting = []
        self.states.remove(self.accepting[0])
        new_transitions = copy.deepcopy(self.transitions)
        for s in self.accepting:
            self.accepting.remove(s)
        for s in self.states:
            for t in self.transitions[s]:
                if(t=="#"):
                    new_acc_state = s
                    if(not(new_acc_state in new_accepting)):
                        new_accepting.append(new_acc_state)   
                    del new_transitions[s]["#"]
        self.transitions = new_transitions
        self.accepting = new_accepting

    def change_to_totally_defined(self,alpha=["0","1"]):
        global index_total_states
        new_transitions = copy.deepcopy(self.transitions)
        new_states = self.states.copy()
        for s in self.states:
            if(not(s in self.transitions)):
                new_transitions[s]={}
            for l in alpha:
                if(not(l in new_transitions[s])):
                    new_state = 'q' + str(index_total_states)
                    index_total_states+=1
                    new_states.append(new_state)
                    new_transitions[s][l] = new_state
                    new_transitions[new_state] = {}
                    for l2 in alpha:
                        new_transitions[new_state][l2]=new_state                 
        self.transitions = new_transitions
        self.states = new_states
            

    def is_unreachable_state(self,s,deleted_states=[]):
        if(s!=self.initial):
            for state in self.states:
                if(not(state in deleted_states)):
                    if(s!=state and s in self.transitions[state].values()):
                        return False
            return True
        return False
    
    def delete_unreachable_states(self):
        deleted_states = []
        check=True
        while(check):
            check=False
            for s in self.states:
                if(not(s in deleted_states) and self.is_unreachable_state(s,deleted_states)):
                    del self.transitions[s]
                    deleted_states.append(s)
                    check=True
        for to_remove in deleted_states:
            self.states.remove(to_remove)
            if(to_remove in self.accepting):
                self.accepting.remove(to_remove)
        

    def is_useless_state(self,s):
        if(not(s in self.accepting)):
            if(not(s in self.transitions) or len(self.transitions[s])==0 or (len(set(self.transitions[s].values()))==1 and s in self.transitions[s].values())):
                return True
        return False

    def delete_transitions_to(self,s):
        new_transitions = copy.deepcopy(self.transitions)
        for state in self.states:
            if(state in self.transitions):
                for tran in self.transitions[state]:
                    if(self.transitions[state][tran]==s):
                        del new_transitions[state][tran]
        self.transitions = new_transitions

    def delete_useless_states(self):
        deleted_states = []
        check=True
        while(check):
            check=False
            for s in self.states:
                if(not(s in deleted_states) and self.is_useless_state(s)):
                    deleted_states.append(s)
                    del self.transitions[s]
                    self.delete_transitions_to(s)
                    check=True
        for to_remove in deleted_states:
            self.states.remove(to_remove)
        if(len(self.states)==0):
            self.states = [self.initial]   
        #new_transitions = copy.deepcopy(self.transitions)
        #for state in self.transitions:
            #if(not(state in self.states)):
                #print("22")
                #del new_transitions[state]
        #self.transitions = new_transitions
          
    def add_back_word_end_trans(self):
        global index_total_states
        new_transitions = copy.deepcopy(self.transitions)
        final_state = 'q' + str(index_total_states)
        self.states.append(final_state)
        for s in self.accepting:
            if(not(s in self.transitions)):
                new_transitions[s]={}              
            new_transitions[s]["#"] = final_state
        index_total_states+=1
        if(len(self.accepting)>0):
            self.accepting = [final_state]
        else:
            new_transitions[self.initial] = {}
            new_transitions[self.initial]["#"] = final_state    
        self.transitions = new_transitions                      

    def create_dict_for_naming_compound_DFA(self,another):
        d={}
        global index_total_states
        for x in self.states:
            for y in another.states:
                d[(x,y)]='q' + str(index_total_states)
                index_total_states+=1
        return(d)
                
    def intersection(self,another,alpha=["0","1"]):
        if(len(self.accepting)==0):
            return self
        elif(len(another.accepting)==0):
            return another
    
        self.tmp_delete_word_end_trans()
        another.tmp_delete_word_end_trans()
        self.change_to_totally_defined()
        another.change_to_totally_defined()
        first_states = self.states
        second_states = another.states
        first_transitions = self.transitions
        second_transitions = another.transitions
        first_initial = self.initial
        second_initial = another.initial
        first_accepting = self.accepting
        second_accepting = another.accepting
        d = self.create_dict_for_naming_compound_DFA(another) # dictionary that maps (q_num1,q_num2) to q_num2, for easier naming
        new_states = [d[(x,y)] for x in first_states for y in second_states]
        new_initial = d[(first_initial,second_initial)]
        new_accepting = [d[(x,y)] for x in first_accepting for y in second_accepting]
        new_transitions={}
        for x in first_states:
            for y in second_states:
                for c in alpha:
                    if(not(d[(x,y)] in new_transitions)):
                        new_transitions[d[(x,y)]]={}
                    new_transitions[d[(x,y)]][c] = d[(first_transitions[x][c],second_transitions[y][c])]        
        new_DFA = DFA(new_states,new_transitions,new_initial,new_accepting)
        new_DFA.delete_unreachable_states()
        new_DFA.delete_useless_states()
        new_DFA.add_back_word_end_trans()
        return(new_DFA)

    def union(self,another,alpha=["0","1"]):
        if(len(self.accepting)==0):
            return another
        elif(len(another.accepting)==0):
            return self
    
        self.tmp_delete_word_end_trans()
        another.tmp_delete_word_end_trans()
        self.change_to_totally_defined()
        another.change_to_totally_defined()
        first_states = self.states
        second_states = another.states
        first_transitions = self.transitions
        second_transitions = another.transitions
        first_initial = self.initial
        second_initial = another.initial
        first_accepting = self.accepting
        second_accepting = another.accepting
        d = self.create_dict_for_naming_compound_DFA(another) # dictionary that maps (q_num1,q_num2) to q_num2, for easier naming
        new_states = [d[(x,y)] for x in first_states for y in second_states]
        new_initial = d[(first_initial,second_initial)]
        new_accepting_with_rep = [d[(x,y)] for x in first_accepting for y in second_states]
        new_accepting_with_rep += [d[(x,y)] for x in first_states for y in second_accepting]
        new_accepting_with_rep = set(new_accepting_with_rep)
        new_accepting = [x for x in new_accepting_with_rep]
        new_transitions={}
        for x in first_states:
            for y in second_states:
                for c in alpha:
                    if(not(d[(x,y)] in new_transitions)):
                        new_transitions[d[(x,y)]]={}
                    new_transitions[d[(x,y)]][c] = d[(first_transitions[x][c],second_transitions[y][c])]        
        new_DFA = DFA(new_states,new_transitions,new_initial,new_accepting)
        new_DFA.delete_unreachable_states()
        new_DFA.delete_useless_states()
        new_DFA.add_back_word_end_trans()
        return(new_DFA)

    def get_complement(self):
        if(len(self.accepting)==0):
            return(create_dfa_exist_at_least(0))
        
        self.tmp_delete_word_end_trans()
        self.change_to_totally_defined()
        old_acc = self.accepting
        states = self.states
        new_acc=[]
        for s in states:
            if(not(s in old_acc)):
                new_acc.append(s)
        new_DFA = DFA(self.states,self.transitions,self.initial,new_acc)
        new_DFA.delete_unreachable_states()
        new_DFA.delete_useless_states()
        new_DFA.add_back_word_end_trans()
        return(new_DFA)

    def plot_transitions(self, graph_name, directory):
        # Requires graphviz executables to be installed.
        dot = Digraph(comment=graph_name,
                      format='png',
                      name=graph_name,
                      directory=directory,
                      graph_attr={'rankdir': 'LR'})
        dot.node(graph_name, shape='square')

        for state in self.states:
            node_attributes = {'shape': 'doublecircle' if state in self.accepting else 'circle'}
            if state == self.initial:
                node_attributes['fontname'] = 'bold'
            dot.node(state, **node_attributes)

        for source_state, targets in self.transitions.items():
            for letter, target_state in targets.items():
                dot.edge(source_state, target_state, label=letter)

        dot.render(graph_name + '.gv')

    def reaches_qf(self, state):
        return bool(self.transitions.get(state, {}).get('#'))

    def encode(self):
        # Ensure that the states are consecutively numbered.
        assert sorted(map(lambda state: int(state[1:]), filter(lambda s: s != 'qF', self.states))) == \
               sorted(range(len(self.states) - 1))

        no_transition = '0'
        self_transition = '1' + ('0' * PENALTY_EXISTING_TRANSITION)
        transition_to_next = '1' + ('1' * PENALTY_EXISTING_TRANSITION)

        def encode_transition(state, letter):
            transition_or_none = self.transitions[state].get(letter)
            return no_transition if transition_or_none is None else (
                self_transition if transition_or_none == state else transition_to_next)

        return ''.join(encode_transition('q%d' % i, letter)
                       for i in range(len(self.states) - 1)
                       for letter in ('0', '1', '#'))

    def encode_positive_example(self, word):
        def deterministic_transition(state):
            return len(self.transitions[state]) == 1

        def two_transitions(state):
            return len(self.transitions[curr_state]) == 2

        encoding = ''
        curr_state = self.initial
        letter_encoding_in_state_which_reaches_qf = {'0': '00', '1': '10', '#': '11'}
        for letter in word:
            if(deterministic_transition(curr_state)):
                encoding +=''
            elif(two_transitions(curr_state)):
                if(letter=='#'):
                    if('0' in self.transitions[curr_state]):
                        encoding+='1'
                    else:
                        encoding+='0'
                else:
                    encoding +=letter
            else:
                encoding+=letter_encoding_in_state_which_reaches_qf[letter]
            curr_state = self.transitions[curr_state][letter]
        return encoding

def create_built_dfa(basic,mode,value):
    global index_total_states
    DFA_and_index = create_built_dfa_and_return_total_index(basic,mode,value,index_total_states)
    dfa = DFA(DFA_and_index[0],DFA_and_index[1],DFA_and_index[2],DFA_and_index[3],DFA_and_index[4])
    index_total_states = DFA_and_index[5]
    return(dfa)

def create_dfa_exist_exactly(value_or_values):
    return(create_built_dfa("exist","exactly",value_or_values))

def create_dfa_exist_at_least(value):
    return(create_built_dfa("exist","at least",value))

def create_dfa_exist_at_most(value):
    return(create_built_dfa("exist","at most",value))

def create_dfa_all_exactly(value):
    return(create_built_dfa("all","exactly",value))

def create_dfa_all_at_least(value):
    return(create_built_dfa("all","at least",value))

def create_dfa_all_at_most(value):
    return(create_built_dfa("all","at most",value))

def resetGlobalIndex():
    global index_total_states
    index_total_states = 0

