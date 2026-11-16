# Q47: "去同存异" check. Each figure = dict region -> colour ('w' outline, 'b' black).
# Rule from rows 1-2: regions present in both with the same colour vanish (outline too);
# regions whose colour differs survive and are black; nothing else remains (no frame).
def rule(f1,f2):
    out={}
    for k in set(f1)|set(f2):
        a,b=f1.get(k),f2.get(k)
        if a and b and a!=b: out[k]='b'
        elif (a is None)!=(b is None): out[k]=a or b
    return out
# row 2: five small right triangles of a staircase
r2f1={'r1c1':'w','r1c2':'w','r2c2_up':'w','r2c2_lo':'b','r2c3':'b'}
r2f2={'r1c1':'w','r1c2':'b','r2c2_up':'w','r2c2_lo':'b','r2c3':'w'}
r2f3={'r1c2':'b','r2c3':'b'}
print('row2 rule ok:',rule(r2f1,r2f2)==r2f3)
# row 3: square cut by both diagonals and both midlines into 8 triangles
# UL_t=upper-left quadrant, triangle on top edge; UL_l = on left edge; etc.
tri=['UL_t','UL_l','UR_t','UR_r','LL_l','LL_b','LR_r','LR_b']
def sq(black): return dict({'frame':'w'},**{t:('b' if t in black else 'w') for t in tri})
f1=sq({'UL_t','UL_l'}); f2=sq({'UL_l','UR_r'})
pred=rule(f1,f2); print('row3 predicted:',pred)
opts={'A':{'UL_t':'b','UR_r':'b'},
      'B':sq({'UL_t','LR_b'}),
      'C':sq({'UL_t','UR_r'}),
      'D':{'UL_l':'b','UR_t':'b'}}
for k,v in opts.items(): print(' ',k,'match' if v==pred else 'no')
