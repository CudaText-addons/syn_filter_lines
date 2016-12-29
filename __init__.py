import os
import re
from sw import *

fn_ini = 'syn_filter_lines.ini'


def do_dialog(text, b_re, b_nocase, b_sort, b_save):
    RES_TEXT = 1
    RES_REGEX = 2
    RES_NOCASE = 3
    RES_SORT = 4
    RES_SAVE = 5
    RES_OK = 6
    c1 = chr(1)
    s_re = '1' if b_re else '0'
    s_i = '1' if b_nocase else '0'
    s_sort = '1' if b_sort else '0'
    s_save = '1' if b_save else '0'
    
    res = dlg_custom('Filter Lines', 406, 190, 
      '\n'.join([]
         +[c1.join(['type=label', 'pos=6,5,400,0', 'cap=&Text:'])]
         +[c1.join(['type=edit', 'pos=6,23,400,0', 'val='+text])]
         +[c1.join(['type=check', 'pos=6,51,400,0', 'cap=&Reg.ex.', 'val='+s_re])]
         +[c1.join(['type=check', 'pos=6,76,400,0', 'cap=&Ignore case', 'val='+s_i])]
         +[c1.join(['type=check', 'pos=6,101,400,0', 'cap=&Sort output', 'val='+s_sort])]
         +[c1.join(['type=check', 'pos=6,126,400,0', 'cap=S&ave options', 'val='+s_save])]
         +[c1.join(['type=button', 'pos=194,160,294,0', 'cap=&OK', 'props=1'])]
         +[c1.join(['type=button', 'pos=300,160,400,0', 'cap=Cancel'])]
      ) )
    if res is None: return
        
    res, s = res
    if res != RES_OK: return
    s = s.splitlines()
    text = s[RES_TEXT]
    if not text: return
    
    regex = s[RES_REGEX]=='1'
    nocase = s[RES_NOCASE]=='1'
    sort = s[RES_SORT]=='1'
    save = s[RES_SAVE]=='1'
    return (text, regex, nocase, sort, save)


def is_ok(line, test, b_regex, b_nocase):
    if not b_regex:
        if b_nocase:
            ok = test.lower() in line.lower()
        else:
            ok = test in line
    else:
        flags = re.I if b_nocase else 0
        ok = bool(re.search(test, line, flags=flags))
    return ok


def do_filter():

    b_save = ini_read(fn_ini, 'op', 'save', '0')=='1'
    if b_save:
        text = ini_read(fn_ini, 'op', 'text', '')
        b_regex = ini_read(fn_ini, 'op', 'regex', '0')=='1'
        b_nocase = ini_read(fn_ini, 'op', 'nocase', '0')=='1'
        b_sort = ini_read(fn_ini, 'op', 'sort', '0')=='1'
    else:
        text = ''
        b_regex = False
        b_nocase = False
        b_sort = False

    res = do_dialog(text, b_regex, b_nocase, b_sort, b_save)
    if res is None: return
    text, b_regex, b_nocase, b_sort, b_save = res    

    #save options
    ini_write(fn_ini, 'op', 'save', '1' if b_save else '0')        
    if b_save:
        ini_write(fn_ini, 'op', 'text', text)
        ini_write(fn_ini, 'op', 'regex', '1' if b_regex else '0')
        ini_write(fn_ini, 'op', 'nocase', '1' if b_nocase else '0')
        ini_write(fn_ini, 'op', 'sort', '1' if b_sort else '0')

    res = []
    for i in range(ed.get_line_count()):
        line = ed.get_text_line(i)
        if is_ok(line, text, b_regex, b_nocase):
            res.append(line)
    
    if not res:
        msg_status('Cannot find lines: '+text)
        return
        
    if b_sort:
        res = sorted(res)

    file_open('')
    flag = 'r' if b_regex else '' 
    flag += 'i' if b_nocase else ''
    flag += 's' if b_sort else ''
    
    ed.set_prop(PROP_TAB_TITLE, 'Filter['+flag+']: '+text)
    ed.set_text_all('\n'.join(res))
    msg_status('Found %d matching lines' % len(res))
        

class Command:
    def dlg(self):
        do_filter()
