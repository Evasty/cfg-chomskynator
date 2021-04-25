import timeit
def file2list(fname):
    f = open(fname)
    ret = []
    for x in f:
        ret.append(x)
    f.close()
    return ret

def list2fileA(list,path):
    f = open(path,'a')
    for x in list:
        f.write(x)
    f.close()

def list2fileW(list,path):
    f = open(path,'w')
    for x in list:
        #print(x)
        f.write(f'{x}\n')
    f.close()

#type = l|d, end = <str>, sort = <bool>
def basicPrinter(pData, type = 'l',  end = '\n', sort =False):
    data = sorted(pData) if sorted else pData
    if type == 'l':
        for i in data:
            print(i)
    if type == 'd':
        for i in data:
            print(f'{i} -> {pData[i]}')


fn = 'CFG-CNF'
timing = True
if __name__ == '__main__' and timing:
    start = timeit.default_timer()
    mod = __import__(fn)
    end = timeit.default_timer()
    print(f'time: {end-start}')