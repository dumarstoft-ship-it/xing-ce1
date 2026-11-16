import sys
sys.path.insert(0,'/home/user/xing-ce1/广东行测18套模拟/重编/M03/复核/scripts')
import q48_options_fit as Q
from q48_refit import refit
S=Q.transform(Q.main+[(1,2,0)],Q.ROT[14])
print(sorted(S))
print(refit(S,'A','q48_A_refit_R14h.png'))
Afit=[(-1,0,2),(0,0,1),(0,0,2),(0,0,3),(0,1,1),(0,2,1),(0,2,3),(1,0,3),(1,2,1),(1,2,3)]
print(refit(Afit,'A','q48_A_refit_fit.png'))
