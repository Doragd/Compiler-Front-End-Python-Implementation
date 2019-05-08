import copy
import random

class LLParser:
    def __init__(self, file_name):

        self.file_object = file_name #获取句柄
        self.grammer = {}
        self.unac_set = []
        self.ac_set = []
        self.first_res = {}
        self.follow_res = {}
        self.select_res = {}
        self.predict_table = {}
        self.string = "" #测试字符串
        self.p = 0       #字符串指针
        for line in self.file_object.readlines():
            
            div_list = line.replace(' ','').strip('\n').split('::')
            if div_list[0] not in self.grammer.keys():
                self.grammer[div_list[0]] = []
                
            self.grammer[div_list[0]].append(div_list[1])
            
            for ch in line:
                if ch.isupper() and ch not in self.unac_set:
                    self.unac_set.append(ch)
            for ch in div_list[1]:
                if ch != '#' and ch not in self.unac_set:
                    self.ac_set.append(ch)
        
                    
    def convert(self, ch_i, ch_j, grammer):

        rules = copy.deepcopy(grammer)
        for key in grammer.keys():
            for item_i in grammer[key]:
                if ch_i == key and ch_j == item_i[0]:
                    rules[key].remove(item_i)
                    for item_j in grammer[ch_j]:
                        rules[key].append(item_j + item_i[1:])
        return rules
    
    def clean_direct_recur(self, ch_i, grammer, new_unac_set):
        ch = ''
        flag = 0
        rules = copy.deepcopy(grammer)

        while(True):
            temp = chr(random.randint(65,90))
            if temp not in new_unac_set:
                ch = temp
                break
                
        for key in grammer.keys():
            for item_i in grammer[key]:
                if ch_i == key and ch_i == item_i[0]:
                    flag = 1
                    if ch not in rules.keys():
                        rules[ch] = []
                        
                    rules[ch].append(item_i[1:] + ch)
                    rules[key].remove(item_i)

        if flag == 0: #不存在左递归，不用消去
            return rules,new_unac_set

        for key in grammer.keys():
            for item_i in grammer[key]:    
                if ch_i == key and ch_i != item_i[0]:
                    if ch not in rules.keys():
                        rules[ch] = []
                    rules[ch_i].append(item_i + ch)
                    rules[key].remove(item_i)
        rules[ch].append('#') #空输入在最后，不会影响递归下降
        new_unac_set.append(ch)

        return rules, new_unac_set
    
    def remove_left_recursion(self):
        new_grammer = copy.deepcopy(self.grammer)
        new_unac_set = copy.deepcopy(self.unac_set)
        
        for i in range(len(self.unac_set)):
            for j in range(0,i):
                new_grammer = self.convert(self.unac_set[i], self.unac_set[j], new_grammer)           
            new_grammer,new_unac_set = self.clean_direct_recur(self.unac_set[i], new_grammer, new_unac_set)    
        return new_grammer,new_unac_set
    

    def LCP(self, i,j, rules): #获取两个字符串之间的最长公共前缀
        strs = [rules[i], rules[j]]
        res = ''
        for each in zip(*strs):
            if len(set(each)) == 1:
                res += each[0]
            else:
                return res
        return res

    def get_lcp_res(self, key): #获得每个拥有公共前缀的元素下标
        res = {}   
        rules = self.grammer[key]
        for i in range(len(rules)):
            for j in range(i+1, len(rules)):
                temp = self.LCP(i,j,rules)
                if temp not in res.keys():
                    res[temp] = set()
                res[temp].add(i)
                res[temp].add(j)
        if '' in res.keys():
            res.pop('')
        return res
    
    def remove_common_factor(self):
        keys = list(self.grammer.keys()) #事先保存好没有修改过的grammer_key
        for key in keys:
            while(True):
                res = self.get_lcp_res(key)
                if(res == {}): #不断迭代，直到没有公共前缀
                    break           
                dels = [] #存储需要删除的符号串        
                lcp = list(res.keys())[0] #策略：每次取一个公共前缀      
                ch = ''
                while(True):
                    temp = chr(random.randint(65,90))
                    if temp not in self.unac_set:
                        ch = temp
                        break
                self.unac_set.append(ch)       
                for i in res[lcp]: #res[lcp]存储的要消除公共因子的元素下标
                    string = self.grammer[key][i]
                    dels.append(string)
                    string = string.lstrip(lcp)
                    if string == '':
                        string += '#'
                    if ch not in self.grammer.keys():
                        self.grammer[ch] = []
                    self.grammer[ch].append(string) #加到新的产生式里面
                for string in dels: #从原来的产生式里面删除
                    self.grammer[key].remove(string)
                self.grammer[key].append(lcp+ch)
        return self.grammer, self.unac_set
    
    def get_first(self, ch):
        self.first_res[ch] = set()
        if ch not in self.unac_set: #ch是终结符
            self.first_res[ch].add(ch)
        else:
            for rule in self.grammer[ch]: #ch不是终结符，则遍历ch的每一条产生式
                if rule == '#': #存在空输入产生式
                    self.first_res[ch].add('#')
                    continue
                if rule[0] not in self.first_res.keys(): #在求first集前先判断是否已经求好了
                    self.get_first(rule[0])
                self.first_res[ch].update(self.first_res[rule[0]] - set(['#'])) #加入First(Y0)\{#}
                for i in range(1, len(rule)):
                    flag = 0
                    for j in range(0,i): #对Yi前面的进行遍历，是否每一个的First集都存在空集
                        if '#' not in self.first_res[rule[j]]:
                            flag = 1
                            break
                    if(flag == 0): #flag=0说明都存在空集，则加入First(Yi)\{#}
                        if rule[i] not in self.first_res.keys():
                            self.get_first(rule[i])
                        self.first_res[ch].update(self.first_res[rule[i]] - set(['#']))
                    else:
                        break
                flag = 0
                for i in range(0, len(rule)): #判断所有的Yi是否每一个的First集都存在空集
                    if '#' not in self.first_res[rule[i]]:
                        flag = 1
                        break
                if(flag == 0): #flag=0说明所有的first集都存在空集，则加入'#'
                    self.first_res[ch].add('#')

    def get_first_str(self, st, rule):
        res = set()
        res.update(self.first_res[rule[st]] - set(['#']))
        for i in range(st+1, len(rule)):
            flag = 0
            for j in range(st,i): #对Yi前面的进行遍历，是否每一个的First集都存在空集
                if '#' not in self.first_res[rule[j]]:
                    flag = 1
                    break
            if(flag == 0): #flag=0说明都存在空集，则加入First(Yi)\{#}
                res.update(self.first_res[rule[i]] - set(['#']))
            else:
                break
        flag = 0
        for i in range(st, len(rule)): #判断所有的Yi是否每一个的First集都存在空集
            if '#' not in self.first_res[rule[i]]:
                flag = 1
                break
        if(flag == 0): #flag=0说明所有的first集都存在空集，则加入'#'
            res.add('#')
        return res

    def get_follow(self):
        for i in self.unac_set:
            self.follow_res[i] = set()
        self.follow_res[self.unac_set[0]].add('$')
        while(True):
            copy_follow_res = copy.deepcopy(self.follow_res)
            for ch in self.grammer.keys():
                for rule in self.grammer[ch]:
                    for j in range(len(rule)):
                        if rule[j] in self.unac_set:
                            if j != len(rule)-1: 
                                first_str = self.get_first_str(j+1, rule)
                                self.follow_res[rule[j]] |= (first_str - set(['#']))
                                if '#' in first_str:
                                    self.follow_res[rule[j]] |=  self.follow_res[ch]
                            else:  #注意特判，否则会越界
                                self.follow_res[rule[j]] |=  self.follow_res[ch]
            if(copy_follow_res == self.follow_res):
                break
    
    def get_select(self):   
        for i in LLP.ac_set: #获取终结和非终结符的first集
            LLP.get_first(i)
        for i in LLP.unac_set:
            LLP.get_first(i) 
        LLP.get_follow() #获取follow集

        for ch in self.unac_set:
            self.select_res[ch] = {}
            for rule in self.grammer[ch]:
                self.select_res[ch][rule] = set()
                if rule == '#':
                    self.select_res[ch][rule].update(self.follow_res[ch])
                elif len(rule) == 1:
                    if '#' in LLP.first_res[rule]:
                        self.select_res[ch][rule].update( (self.first_res[rule] - set('#')) | self.follow_res[ch])
                    else:
                        self.select_res[ch][rule].update(self.first_res[rule])
                else:
                    temp_res = self.get_first_str(0, rule)
                    if '#' in temp_res:
                        self.select_res[ch][rule].update( (temp_res - set('#')) | self.follow_res[ch])
                    else:
                        self.select_res[ch][rule].update(temp_res)
    
    def is_LL(self):
        self.get_select()
        LL_flag = True
        for ch in self.unac_set:
            judge_list = []
            flag = 1
            for rule in self.grammer[ch]:
                judge_list.append(self.select_res[ch][rule])
            for i in range(len(judge_list)):
                for j in range(i+1, len(judge_list)):
                    if (judge_list[i] & judge_list[j]) != set():
                        flag = 0
                        break
            if(flag == 0):
                LL_flag = False
        return LL_flag
    
    def make_predict_table(self):
        predict_table = {}
        for ch in self.select_res.keys():
            predict_table[ch] = {}
            for rule in self.select_res[ch].keys():
                for a in self.select_res[ch][rule]:
                    predict_table[ch][a] = rule
        return predict_table

    def test_string(self):
        stack = ['$',self.unac_set[0]]
        flag = 1
        while(stack[-1] != '$'):
            if(stack[-1] == self.string[self.p]):
                stack.pop(-1)
                self.p += 1            
            elif(stack[-1] in self.ac_set):
                print('Error!')
                flag = 0
                break
            else:
                try:
                    rule = self.predict_table[stack[-1]][self.string[self.p]]
                    print(stack[-1] + '->'+ rule)
                    stack.pop(-1)
                    if rule != '#':
                        temp = list(rule).copy()
                        temp.reverse()
                        stack.extend(temp)
                    else:
                        continue
                except:
                    print('Error!')
                    flag = 0
                    break
        if(stack[-1] != self.string[self.p]):
            flag = 0
        return flag
    
    def output(self, grammer):
        res = []
        for key in grammer.keys():
            for item in grammer[key]:
                res.append(key + '->' + item)
        for item in res:
            print(item)
                
    def run(self):
        self.grammer,self.unac_set = self.remove_left_recursion()
        self.grammer,self.unac_set = self.remove_common_factor()
        print('grammer after processing:')
        self.output(self.grammer)
        if(self.is_LL() == False):
            print(' Not LL(1) ')
            return
        self.predict_table = self.make_predict_table()
        while(True):
            self.string = input('输入测试字符串(以$结尾,输入exit则结束):')
            self.p = 0
            if self.string == 'exit':
                break
            if self.string[-1] != '$':
                print('输入不合法')
                continue
            flag = self.test_string()
            if(flag):
                print(self.string + ' is Yes')
            else:
                print(self.string + ' is No')
f = open('test.txt')
LLP = LLParser(f)
LLP.run()
f.close()