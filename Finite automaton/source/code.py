class FA:
    def __init__(self, file_name):
        self.file_object = file_name #获取句柄
        lines = [line.strip('\n') for line in self.file_object] #获取每一行
        self.total_states = int(lines[0]) #第一行是状态数
        self.end_states = [int(x) for x in lines[-1].split(' ')] #最后一行是结束状态列表
        self.vis = [0]*self.total_states #访问标记数组
        self.states_transition = self.get_transition(lines, self.total_states) #状态转移数组
        self.alpha_set = self.get_alpha_set(self.states_transition) #字母表
        
    def get_transition(self, lines, total_states):
        states_transition = {}
        for i in range(total_states):
            temp = [x for x in lines[i+1].strip('\n').split(' ')]
            if temp == ['']:
                states_transition[i] = {}
            else:
                temp_dict = {}
                for j in range(0, len(temp), 2):
                    temp_dict[temp[j]] = []
                for j in range(0, len(temp), 2):
                    temp_dict[temp[j]].append(int(temp[j+1]))
                states_transition[i] = temp_dict
        return states_transition
    
    def get_alpha_set(self, states_transition):
        res = []
        for i in states_transition.keys():
            res.extend(states_transition[i].keys())
        res = set(res)
        if '0' in res:
            res.remove('0') #去除空输入,假定0是空输入
        return sorted(res)
    
    def is_DFA(self):
        for i in self.states_transition.keys():
            if '0' in self.states_transition[i].keys():
                return False
            else:
                for value in self.states_transition[i].values():
                    if len(value) >= 2:
                        return False
        return True
    
    def format_DFA(self):
        total_states = self.total_states
        ends = self.end_states
        trans = self.states_transition.copy()
        for i in trans.keys():
            for key in trans[i].keys():
                trans[i][key] = trans[i][key][0]
        return total_states, trans, ends
    
    def epsilon_closure(self, states_set):
        res = []
        for state in states_set:
            if self.vis[state] == 0: #未被访问过
                res.append(state)
                self.vis[state] = 1
                temp = self.states_transition[state]
                if('0' in temp.keys()):
                    res.extend(self.epsilon_closure(temp['0']))
        return res
    
    def edge_closure(self, states_set, ch):
        res = []
        self.vis = [0]*self.total_states
        for state in states_set:
            temp = self.states_transition[state]
            if(ch in temp.keys()):
                res.extend(temp[ch])
        if res == []: #该状态没有ch的edge边
            return res
        return self.epsilon_closure(res)
    
    def convert(self):
        
        self.vis = [0]*self.total_states #记得每次初始化
        states = [self.epsilon_closure([0])]
        trans = {}
        ends = []
        now_state = 0 #从0开始编号
        total_states = 1
        while(now_state < total_states):
            trans[now_state] = {}
            for ch in self.alpha_set:
                temp = self.edge_closure(states[now_state], ch)
                if(temp == []):
                    continue
                if temp in states:
                    trans[now_state][ch] = states.index(temp)
                else:
                    states.append(temp)
                    trans[now_state][ch] = total_states
                    total_states += 1
            now_state += 1
        for state in states:
            if len(set(state)&set(self.end_states)) != 0:
                ends.append(states.index(state))
        return total_states, trans, ends
    
    def min_DFA(self):
        import copy
        
        if(self.is_DFA()):
            print("This is DFA")
            DFA = self.format_DFA()
        else:
            print("This is NFA")
            print(self.states_transition)
            DFA = self.convert()
            print("This is New DFA converted from NFA")       
        print(DFA)
        
        trans = DFA[1]
        tot_states = [x for x in range(DFA[0])]
        ac_states = [x for x in tot_states if x in DFA[2]]
        unac_states = [x for x in tot_states if x not in DFA[2]]
        
        def split_set(states_set, id, ch):
            test_set = copy.deepcopy(states_set)
            need_div_set = copy.deepcopy(test_set[id])
            res = []
            empty_set = []
            for s in test_set:
                temp = []
                for x in need_div_set:
                    try:
                        if(trans[x][ch] in s):
                            temp.append(x)
                    except:
                        if x not in empty_set:
                            empty_set.append(x) #对某个元素，没有ch输入
                        continue                        
                if temp == []: #说明对于输入ch，集合里面的所有状态不在集合S
                    continue
                res.append(temp)
            if empty_set != []:
                res.append(empty_set)
            return res
        
        states_set = [ac_states, unac_states]
        iterate_set = [ac_states, unac_states]
        
        while(True):
            res = []
            for id in range(len(iterate_set)):
                for ch in self.alpha_set:
                    temp_res = split_set(iterate_set, id, ch) #判断是否可以拆分
                    if len(temp_res) == 1 and ch != self.alpha_set[-1]: #如果ch为最后一个测试输入
                        continue #如果长度为1表示集合对于ch输入均转移到同一集合中
                    else:
                        res.extend(temp_res)
                        break
            if iterate_set == res:
                break
            iterate_set = res.copy()
   
        print(iterate_set)
        new_trans = {}  #更新状态转移数组
        for i in trans.keys():
            new_trans[i] = trans[i]
            
        new_ends = []
        
        for i in range(len(iterate_set)):
            
            iterate_set[i].sort() #若有多个状态，仅保留序号最小的状态，因为默认0为初始状态
            if(len(iterate_set[i]) > 1):
                new_state = iterate_set[i][0] #仅保留序号最小的状态
                for j in range(1,len(iterate_set[i])):
                    del new_trans[iterate_set[i][j]]
                    
                for j in range(1,len(iterate_set[i])): #更新转移后的状态
                    for k in new_trans.keys():
                        for ch in self.alpha_set:
                            try:
                                if new_trans[k][ch] == iterate_set[i][j]:
                                    new_trans[k][ch] = new_state
                            except:
                                continue

        for key in new_trans.keys():
            if key in ac_states:
                new_ends.append(key)
                
        total_states = len(new_trans)
        
        return total_states, new_trans, new_ends
    
    
    def run(self):
        string = ''
        minDFA = self.min_DFA()
        print("This is minDFA")
        print(minDFA)
        
        while(True):
            string = input('输入测试字符串(输入exit则结束):')
            if string == 'exit':
                break
            now_state = 0
            i = 0
            while(i < len(string)):
                ch = string[i]
                if ch in minDFA[1][now_state].keys():
                    now_state = minDFA[1][now_state][ch]
                    i += 1
                else:
                    break
            if i == len(string) and now_state in minDFA[2]:
                print(string + ' is YES')
            else:
                print(string + ' is NO')

f = open('DFA.txt')
test = FA(f)
f.close()
test.run()