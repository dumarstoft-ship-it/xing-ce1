from PIL import Image
import numpy as np
im = np.array(Image.open('/home/user/work/build/pkg_r2/assets/PD2A/GD2020X-45.png').convert('L')).astype(int)
dark = im < 140
strips = {'A':(334,362),'B':(392,421),'C':(450,479),'D':(508,537)}
for k,(t,b) in strips.items():
    # left/right ends: vertical lines
    mid = (t+b)//2
    xs = [x for x in range(300, im.shape[1]) if dark[mid, x]]
    # group
    groups=[]
    for x in xs:
        if groups and x-groups[-1][-1]<=2: groups[-1].append(x)
        else: groups.append([x])
    cents=[sum(g)/len(g) for g in groups]
    # at row near top and bottom, find crease crossings
    def crossings(y):
        xs=[x for x in range(300, im.shape[1]) if dark[y,x]]
        gs=[]
        for x in xs:
            if gs and x-gs[-1][-1]<=2: gs[-1].append(x)
            else: gs.append([x])
        return [sum(g)/len(g) for g in gs]
    top=crossings(t+4); bot=crossings(b-4)
    print(k, 'mid-row xs', [round(c,1) for c in cents])
    print('   top+4', [round(c,1) for c in top])
    print('   bot-4', [round(c,1) for c in bot])
