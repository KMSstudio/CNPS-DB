# made by Kang Myeong Seok
# serius02 > db > make_data.py
# raw.json, medi.json, hist.json, 

# --help    | -h : help
# --raw     | -r : update only raw.json
# --medi    | -m : update only medi.json
# --hist    | -h : update only hist.json

import json
import sys

# ===== user define ===== #
company = 'lg'

outstatic_standard = 30

# ===== binary search ===== #
def bn_search(arr, val, idx_op=False):
    lft = 0
    rht = len(arr)-1
    while lft <= rht:
        mid = (lft + rht) // 2
        if arr[mid] == val:
            return mid
        elif arr[mid] > val:
            rht = mid-1
        else:
            lft = mid+1
    return lft if idx_op else -1

def bn_insert(arr, val):
    arr.insert(bn_search(arr, val, idx_op=True), val)

# ===== apply option ===== #
argv = list(sys.argv)[1:]

if ('--help' in argv) or ('-h' in argv):
    print('made by Kang Myeong Seok')
    print('')
    print('--help\t| -h : help')
    print('--raw\t| -r : update only raw.json')
    print('--medi\t| -m : update only medi.json')
    print('--hist\t| -h : update only hist.json')
    exct = [0, 0, 0]
elif ('--raw' in argv) or ('-r' in argv):
    exct = [1, 0, 0]
elif ('--medi' in argv) or ('-m' in argv):
    exct = [0, 1, 0]
elif ('--hist' in argv) or ('-h' in argv):
    exct = [0, 0, 1]
else:
    exct = [1, 1, 1]
    
if ('--cj' in argv) or ('cj' in argv):
    company = 'cj'
elif ('--po' in argv) or ('po' in argv):
    company = 'po'
elif ('--hj' in argv) or ('hj' in argv):
    company = 'hj'
elif ('--lg' in argv) or ('lg' in argv):
    company = 'lg'
    
# ===== initalize ===== #
path = f'./{company}'
    
# ===== raw.json ===== #
if exct[0]:
    print('='*50)
    print(f'update {path}/raw.json')
    print('='*50)
    
    with open(path + '/queue.json', 'r', encoding="UTF-8") as f:
        que = json.load(f)
    print(f"precieved queue len : ({que['size']})")
    db = {}

    for idx in range(0, que['size']):
        res = que['queue'][idx][1]
        
        for item in res:
            if item[0] in db.keys():
                bn_insert(db[item[0]], item[1])
            else:
                db[item[0]] = [item[1]]

            mrg = item[0].split('_', maxsplit=2)
            if len(mrg) < 3:
                continue
            mrgItem = mrg[0] + '_' + mrg[2]
            
            if mrgItem in db.keys():
                bn_insert(db[mrgItem], item[1])
            else:
                db[mrgItem] = [item[1]]
                
        if not (idx % 2000):
            print(f"\r {{ {idx} / {que['size']} }}", end='') # console print occur here!
            with open(path + '/raw.json', 'w', encoding="UTF-8") as f:
                json.dump(db, f, ensure_ascii=False, indent=4)
    
    with open(path + '/raw.json', 'w', encoding="UTF-8") as f:
        json.dump(db, f, ensure_ascii=False)
    print('\nsuccess')
    
# ===== medi.json ===== #
if exct[1]:
    print('='*50)
    print(f'update {path}/medi.json by {path}/raw.json')
    print('='*50)

    db = {}
    with open(path + '/raw.json', 'r', encoding="UTF-8") as f:
        db = json.load(f)
    ret = [0, 0]
    print(f'precieved db len : ({len(db)})')

    medi = {}
    for key, item in db.items():
        length = len(item)
        if(length < outstatic_standard): 
            ret[1] += 1 
            continue
        ret[0] += 1
        medi[key] = {'25': item[length//4], '50': item[length//2], '75': item[length*3//4], '95': item[length*19//20]} 
    print(f'{{ outstatic: {ret[1]}, instatic: {ret[0]} }}')

    medi = dict(sorted(medi.items()))

    with open(path + '/medi.json', 'w', encoding="UTF-8") as f:
        json.dump(medi, f, ensure_ascii=False)
    print('success')

# ===== hist.json ===== #
if exct[2]:
    print('='*50)
    print(f'update {path}/hist.json by {path}/raw.json')
    print('='*50)
    
    db = {}
    with open(path + '/raw.json', 'r', encoding="UTF-8") as f:
        db = json.load(f)
    ret = [0, 0]
    print(f'precieved db len : ({len(db)})')

    hist = {}
    for key, item in db.items():
        if len(item) < outstatic_standard:
            ret[1] += 1 
            continue
        ret[0] += 1
        hist[key] = {}
        pre = cur = 0
        for hour in range(1, 73):
            cur = bn_search(item, hour*60, idx_op=True)
            hist[key]['h'+str(hour)] = cur - pre
            pre = cur
    print(f'{{ outstatic: {ret[1]}, instatic: {ret[0]} }}')

    with open(path + '/hist.json', 'w', encoding="UTF-8") as f:
        json.dump(hist, f, ensure_ascii=False)
    print('success')