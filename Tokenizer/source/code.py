class Tokenizer:
    def __init__(self, file_name):
        self.file_object = file_name
        self.seps = {
            ',':'comma',
            ':':'colon',
            ';':'simcon',
            '(':'lparen',
            ')':'rparen',
            '{':'lbrac',
            '}':'rbrac',
        }
        self.kws = {
            'int':'kw_int',
            'char':'kw_char',
            'void':'kw_void',
            'if':'kw_if',
            'else':'kw_else',
            'switch':'kw_switch',
            'case':'kw_case',
            'default':'kw_default',
            'while':'kw_while',
            'do':'kw_do',
            'for':'kw_for',
            'break':'kw_break',
            'continue':'kw_continue',
            'return':'kw_return'
        }
        self.ops = {
            '+':'add',
            '-':'sub',
            '*':'mul',
            '/':'div',
            '%':'mod',
            '&':'bit_and',
            '|':'bit_or',
            '!':'not',
            '>':'gt',
            '<':'lt',
            '=':'assign',
            '++':'inc',
            '--':'dec',
            '&&':'and',
            '||':'or',
            '>=':'ge',
            '<=':'le',
            '==':'equ',
            '!=':'nequ',
        }
        self.state = 0
        self.line_number = 0
        self.error_message = []
        self.char_message = []
    def identify(self, line):
        line_length = len(line)
        i = 0
        string = ''
        while(i < line_length):
            ch = line[i]
            if self.state == 0:
                if ch == ' ':
                    i += 1
                    continue
                elif ch in self.seps.keys():
                    string += ch
                    content = '('+ self.seps[string] + ',' + string + ')'
                    
                    self.char_message.append(content)
                    self.state = 0
                    string = ''
                    i += 1
                    continue
                elif ch == '_' or ch.isalpha():
                    string += ch
                    self.state = 1
                    i += 1
                elif ch.isdigit():
                    string += ch
                    self.state = 2
                    #i += 1 不移动指针，因为要继续判断
                elif ch == '\'':
                    string += ch
                    self.state = 9
                    i += 1
                elif ch == '"':
                    string += ch
                    self.state = 12
                    i += 1
                elif ch in self.ops.keys():
                    string += ch
                    self.state = 15
                    #i += 1 不转移，要继续判断
            elif self.state == 1:
                while(i < line_length):
                    ch = line[i]
                    if ch.isdigit() or ch.isalpha() or ch == '_':
                        string += ch
                        i += 1
                    else:
                        if string in self.kws.keys():
                            content = '(' + self.kws[string] + ',' + string + ')'
                        else:
                            content = '(id,' + string + ')'
                        
                        self.char_message.append(content)
                        self.state = 0
                        string = ''
                        break
            elif self.state == 2:
                if ch == '0':
                    i += 1
                    self.state = 3
                else:
                    i += 1
                    self.state = 4
            elif self.state == 3:
                if ch == 'x' or ch == 'X':
                    string += ch
                    i += 1
                    self.state = 5
                elif ch in ['8', '9']:
                    string += ch #将错误的ch也加入进来
                    self.state = 6 #转到错误处理
                elif ch.isdigit():
                    string += ch
                    i += 1
                    self.state = 7
                else:
                    content = '(num,' + string + ')'
                    
                    self.char_message.append(content)
                    self.state = 0
                    string = ''  
            elif self.state == 4:
                while(i < line_length):
                    ch = line[i]
                    if ch.isdigit():
                        string += ch
                        i += 1
                    else:
                        content = '(num,' + string + ')'
                        
                        self.char_message.append(content)
                        self.state = 0
                        string = ''
                        break  
            elif self.state == 5:
                if ch.isdigit() or (ch >= 'a' and ch <= 'f') or (ch >= 'A' and ch <= 'F'):
                    string += ch
                    i += 1
                    self.state = 8
                else:
                    string += ch #将错误的ch也加入进来
                    self.state = 6 #转到错误处理
            elif self.state == 6:
                content = '(line:'+str(self.line_number)+',' + 'num Error:'+ string + ',' + 'Location:' + ch + ')'
                
                self.error_message.append(content)
                self.state = 0
                string = ''
                i += 1
            elif self.state == 7:
                while(i < line_length):
                    ch = line[i]
                    if ch in ['8', '9']:
                        string += ch #将错误的ch也加入进来
                        self.state = 6
                        break
                    elif ch.isdigit():
                        string += ch
                        i += 1
                    else:
                        content = '(num,' + string + ')'
                        
                        self.char_message.append(content)
                        self.state = 0
                        string = ''
                        break                          
            elif self.state == 8:
                while(i < line_length):
                    ch = line[i]
                    if ch.isdigit() or (ch >= 'a' and ch <= 'f') or (ch >= 'A' and ch <= 'F'):
                        string += ch
                        i += 1
                    else:
                        content = '(int,' + string + ')'
                        
                        self.char_message.append(content)
                        self.state = 0
                        string = ''
                        break 
            elif self.state == 9:
                if ch == '\'': #说明此时为空字符
                    string += ch
                    content = '(char,' + string + ')'
                    
                    self.char_message.append(content)
                    self.state = 0
                    string = ''
                    i += 1
                else:
                    string += ch
                    i += 1
                    self.state = 10
            elif self.state == 10:
                if ch == '\'':
                    string += ch
                    content = '(char,' + string + ')'
                    
                    self.char_message.append(content)
                    self.state = 0
                    string = ''
                    i += 1
                else:
                    string += ch #将错误的ch也加入进来
                    self.state = 11 #错误处理
            elif self.state == 11:
                content = '(line:'+str(self.line_number)+',' + 'char Error:' + string + 'Location:' + ch + ')'
                
                self.error_message.append(content)
                self.state = 0
                string = ''
                i += 1
            elif self.state == 12:
                if ch == '"':
                    string += ch
                    content = '(str,' + string + ')'
                    
                    self.char_message.append(content)
                    self.state = 0
                    string = ''
                    i += 1  
                else:
                    string += ch
                    i += 1
                    self.state = 13
            elif self.state == 13:
                if ch == '"':
                    string += ch
                    content = '(str,' + string + ')'
                    
                    self.char_message.append(content)
                    self.state = 0
                    string = ''
                    i += 1
                else:
                    string += ch
                    i += 1
                    while(i < line_length):
                        ch = line[i]
                        if ch == '"':
                            string += ch
                            content = '(str,' + string + ')'
                            
                            self.char_message.append(content)
                            self.state = 0
                            string = ''
                            i += 1
                            break 
                        else:
                            string += ch
                            i += 1
                    if i >= line_length:
                        i -= 1 #回退到行末尾
                        self.state = 14
            elif self.state == 14:
                content = '(line:'+str(self.line_number)+',' + 'str Error:' + string + ',' + 'Location:' + ch + ')'
                
                self.error_message.append(content)
                self.state = 0
                string = ''
                i += 1
            elif self.state == 15:
                if ch in ['*','/','%']:
                    content = '('+ self.ops[string] + ',' + string + ')'
                    
                    self.char_message.append(content)
                    self.state = 0
                    string = ''
                    i += 1
                elif ch in ['+','-','&','|','=']:
                    i += 1
                    self.state = 16
                elif ch in ['!','<','>']:
                    i += 1
                    self.state = 17
            elif self.state == 16:
                if ch == line[i-1]:
                    string += ch
                    content = '('+ self.ops[string] + ',' + string + ')'
                    
                    self.char_message.append(content)
                    self.state = 0
                    string = ''
                    i += 1
                else:
                    content = '('+ self.ops[string] + ',' + string + ')'
                    
                    self.char_message.append(content)
                    self.state = 0
                    string = ''
            elif self.state == 17:
                if ch == '=':
                    string += ch
                    content = '('+ self.ops[string] + ',' + string + ')'
                    
                    self.char_message.append(content)
                    self.state = 0
                    string = ''
                    i += 1
                else:
                    content = '('+ self.ops[string] + ',' + string + ')'
                    
                    self.char_message.append(content)
                    self.state = 0
                    string = ''
    def get_error_message(self):
        return self.error_message
    def get_char_message(self):
        return self.char_message                
    def run(self):
        for line in self.file_object:
            line = line.strip('\n')
            line = line.replace('\t','')
            self.line_number += 1
            self.identify(line)

if __name__ == '__main__':
    file = open('test2.txt')
    tk = Tokenizer(file)
    tk.run()
    char_message = tk.get_char_message()
    error_message = tk.get_error_message()
    print("=============Token=======================\n")
    for msg in char_message:
        print(msg)
    if len(error_message) != 0:
        print("===========Error=============\n")
        for msg in error_message:
            print(msg)
    file.close()
