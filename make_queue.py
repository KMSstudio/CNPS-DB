# made by Kang Myeong Seok
# serius02 > db > make_queue.py
# queue.json

# lidst of invoices : read argv as search range. all invoice +- src_range will be searched.
# --file    | -f    : read {path}/queue.json as argv

import inquiry

import time
import json
import sys

# ===== user define ===== #
company = 'po'
src_range = 10 * 1000

Q_LIM_DATE = 365
Q_LIM_SIZE = 1000 * 1000

FILE_AUTOSAVE = 2000

# ===== apply option ===== #
argv = list(sys.argv)
if ('--cj' in argv) or ('cj' in argv):
    company = 'cj'
elif ('--po' in argv) or ('po' in argv):
    company = 'po'
elif ('--hj' in argv) or ('hj' in argv):
    company = 'hj'
elif ('--lg' in argv) or ('lg' in argv):
    company = 'lg'

# argv : list of numeric string
if ('--file' in sys.argv) or ('-f' in sys.argv):
    with open(f'./{company}/list.txt', 'r', encoding="UTF-8") as f:
        data = f.read()
    invoices = data.split('\n')
    argv = []
    for invoice in invoices:
        if not invoice.isnumeric():
            continue
        argv.append(int(invoice))
else:
    argv = list(sys.argv)[1:]
    for item in argv:
        if not item.isnumeric():
            argv.remove(item)    

# ===== initalize ===== #
path = f'./{company}'
api_func = inquiry.func[company]

try:
    with open(path + '/queue.json', 'r', encoding="UTF-8") as f:
        db = json.load(f)
except:
    db = {'size': 0, 'queue': []}
cnstrt = [] #construct
    
# ===== construct queue ===== #
for idx in range(0, len(argv)):
    print('='*50)
    print(f'search range in {int(argv[idx])-src_range} ~ {int(argv[idx])+src_range} [{idx+1}/{len(argv)}] at {path}')
    print('='*50)

    ret = [0, 0]
    print(f"existing queue size: {db['size']}")

    for i in range(int(argv[idx])-src_range, int(argv[idx])+src_range):
        try:
            res = api_func(i)
        except:
            print(f'I get error in invoice {i}')

        print(f'\r {{ true: {ret[0]}, false: {ret[1]}, total: {sum(ret)} }}', end='') # console print occur here!
        if (ret[0]+ret[1]) % FILE_AUTOSAVE == 0:
            db['queue'].extend(cnstrt)
            db['size'] = len(db['queue'])
            with open(path + '/queue.json', 'w', encoding="UTF-8") as f:
                json.dump(db, f, ensure_ascii=False, indent=4)
            cnstrt[:] = [] #cnstrt.clear()

        if not res['success']:
            ret[1] += 1
            continue
        else:
            ret[0] += 1
            res = res['res']
            cnstrt.append((int(time.time()) // (60 * 60 * 24), res))
    print(f'\r {{ true: {ret[0]}, false: {ret[1]}, total: {sum(ret)} }}', end='')

    # make db
    db['queue'].extend(cnstrt)
    db['size'] = len(db['queue'])
    
    # sort and dequeue (can use binaty searcch)
    db['queue'].sort(key= lambda x: x[0], reverse=False)
    today = int(time.time())//(60*60*24)
    while (today - db['queue'][0][0]) >= Q_LIM_DATE and (db['size'] > Q_LIM_SIZE):
        del db['queue'][0]
        db['size'] -= 1
    
    # print as file
    with open(path + '/queue.json', 'w', encoding="UTF-8") as f:
        json.dump(db, f, ensure_ascii=False)
    print('\nsuccess')