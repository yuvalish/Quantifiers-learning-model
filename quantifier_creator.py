from collections import defaultdict
           
def create_built_dfa_and_return_total_index(basic,mod,value,index_total_states):
    if(basic=="exist" and mod=="exactly"):
        if(isinstance(value,int)):
            n_values = [value]
        pre_index = index_total_states
        initial = 'q' + str(index_total_states)
        states = ['q' + str(index_total_states+i) for i in range(max(n_values) + 2)]
        transitions = defaultdict(dict)
        for i in range(max(n_values)):
            transitions['q' + str(index_total_states)]['0'] = 'q' + str(index_total_states)
            transitions['q' + str(index_total_states)]['1'] = 'q' + str(index_total_states + 1)
            index_total_states+=1
        transitions['q' + str(index_total_states)]['0'] = 'q' + str(index_total_states)
        accepting=['q' + str(index_total_states+1)]
        index_total_states+=1
        for n in n_values:
            transitions['q' + str(pre_index+n)]['#'] = 'q' + str(index_total_states)
        index_total_states+=1
        return([states,transitions,initial,accepting,False,index_total_states])

    if(basic=="exist" and mod=="at least"):
        initial = 'q' + str(index_total_states)
        states = ['q' + str(index_total_states+i) for i in range(value + 2)]
        transitions = defaultdict(dict)
        for i in range(value):
            transitions['q' + str(index_total_states)]['0'] = 'q' + str(index_total_states)
            transitions['q' + str(index_total_states)]['1'] = 'q' + str(index_total_states + 1)
            index_total_states+=1
        transitions['q' + str(index_total_states)]['0'] = 'q' + str(index_total_states)
        transitions['q' + str(index_total_states)]['1'] = 'q' + str(index_total_states)
        transitions['q' + str(index_total_states)]['#'] = 'q' + str(index_total_states+1)
        accepting=['q' + str(index_total_states+1)]
        index_total_states+=2
        return([states,transitions,initial,accepting,False,index_total_states])

    if(basic=="exist" and mod=="at most"):    
        max_index = index_total_states + value + 1
        initial = 'q' + str(index_total_states)
        states = ['q' + str(index_total_states+i) for i in range(value + 2)]
        transitions = defaultdict(dict)
        for i in range(value):
            transitions['q' + str(index_total_states)]['0'] = 'q' + str(index_total_states)
            transitions['q' + str(index_total_states)]['1'] = 'q' + str(index_total_states + 1)
            transitions['q' + str(index_total_states)]['#'] = 'q' + str(max_index)
            index_total_states+=1
        transitions['q' + str(index_total_states)]['0'] = 'q' + str(index_total_states)
        transitions['q' + str(index_total_states)]['#'] = 'q' + str(max_index)
        accepting=['q' + str(max_index)]
        index_total_states+=2
        return([states,transitions,initial,accepting,False,index_total_states])

    if(basic=="all" and mod=="exactly"):
        initial = 'q' + str(index_total_states)
        states = ['q' + str(index_total_states+i) for i in range(value + 2)]
        transitions = defaultdict(dict)
        for i in range(value):
            transitions['q' + str(index_total_states)]['1'] = 'q' + str(index_total_states + 1)
            index_total_states+=1
        transitions['q' + str(index_total_states)]['#'] = 'q' + str(index_total_states+1)
        accepting=['q' + str(index_total_states+1)]
        index_total_states+=2
        return([states,transitions,initial,accepting,False,index_total_states])

    if(basic=="all" and mod=="at least"):
        initial = 'q' + str(index_total_states)
        states = ['q' + str(index_total_states+i) for i in range(value + 2)]
        transitions = defaultdict(dict)
        for i in range(value):
            transitions['q' + str(index_total_states)]['1'] = 'q' + str(index_total_states + 1)
            index_total_states+=1
        transitions['q' + str(index_total_states)]['1'] = 'q' + str(index_total_states)
        transitions['q' + str(index_total_states)]['#'] = 'q' + str(index_total_states+1)
        accepting=['q' + str(index_total_states+1)]
        index_total_states+=2
        return([states,transitions,initial,accepting,False,index_total_states])

    if(basic=="all" and mod=="at most"):
        max_index = index_total_states + value + 1
        initial = 'q' + str(index_total_states)
        states = ['q' + str(index_total_states+i) for i in range(value + 2)]
        transitions = defaultdict(dict)
        for i in range(value):
            transitions['q' + str(index_total_states)]['1'] = 'q' + str(index_total_states + 1)
            transitions['q' + str(index_total_states)]['#'] = 'q' + str(max_index)
            index_total_states+=1
        transitions['q' + str(index_total_states)]['#'] = 'q' + str(max_index)
        accepting=['q' + str(max_index)]
        index_total_states+=2
        return([states,transitions,initial,accepting,False,index_total_states])
    
