"""clm.py KEY [TWIN...] : check+take KEY for PD4A, then take each image twin with note imgdup-of-KEY. Logs to claims_log.txt"""
import subprocess, sys, time
C='/home/user/work/tools/claim.py'
def run(*a): return subprocess.run([sys.executable,C,*a],capture_output=True,text=True).stdout.strip()
key=sys.argv[1]; twins=sys.argv[2:]
log=open('claims_log.txt','a')
st=run('check',key); print(key,'check:',st)
if st!='FREE' and 'PD4A' not in st:
    print('!! not free, abort'); log.write(f'{key}\tBLOCKED\t{st}\n'); sys.exit(1)
r=run('take',key,'PD4A','D12 图推'); print(key,'take:',r); log.write(f'{key}\ttake\t{r}\n')
for t in twins:
    st=run('check',t)
    r=run('take',t,'PD4A',f'imgdup-of-{key} (同图题，随 {key} 一并锁定)'); print(' twin',t,'check:',st,'take:',r); log.write(f'{t}\ttwin-of-{key}\t{st}\t{r}\n')
