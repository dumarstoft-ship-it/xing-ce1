import numpy as np
w = 28.5
# strip coordinates: u along length (x right), v up (math). Image y is down, so '/' in image (bottom-left to top-right) is direction (1,1) in math coords.
strips = {
 'A': (359.5, 1249.5, [(465.5,'\\'),(591.5,'/'),(712.5,'\\'),(838.5,'\\'),(1054.5,'/')]),
 'B': (359.5, 1249.5, [(458.5,'/'),(589.5,'/'),(712.0,'/'),(931.0,'\\'),(1148.0,'/')]),
 'C': (359.5, 1249.5, [(464.5,'\\'),(592.0,'/'),(811.0,'\\'),(1019.5,'/'),(1150.5,'\\')]),
 'D': (359.5, 1249.5, [(591.5,'/'),(713.0,'\\'),(924.0,'/'),(1033.0,'\\'),(1142.0,'/')]),
}
def refl(p, d):
    # reflection across line through p with direction d (unit), returns affine (M, t)
    d = np.array(d)/np.linalg.norm(d)
    M = 2*np.outer(d,d) - np.eye(2)
    t = np.array(p) - M@np.array(p)
    return M, t
def fold(start, end, creases):
    # centerline at v = w/2; crease line passes through (u_c, w/2) with direction (1,1) for '/', (1,-1) for '\\'
    T_M, T_t = np.eye(2), np.zeros(2)
    pts = [T_M@np.array([start, w/2]) + T_t]
    for (u, s) in creases:
        c = np.array([u, w/2])
        pts.append(T_M@c + T_t)
        d = (1,1) if s=='/' else (1,-1)
        M, t = refl(c, d)
        # new transform = T o R
        T_t = T_M@t + T_t
        T_M = T_M@M
    pts.append(T_M@np.array([end, w/2]) + T_t)
    return np.array(pts)
for k,(s,e,cr) in strips.items():
    P = fold(s,e,cr)/w
    P = P - P[0]
    segs = np.diff(P, axis=0)
    dirs = [tuple(np.round(sg/np.linalg.norm(sg),2)) for sg in segs]
    lens = [round(float(np.linalg.norm(sg)),2) for sg in segs]
    turns = []
    for a,b in zip(segs[:-1], segs[1:]):
        cr = a[0]*b[1]-a[1]*b[0]
        turns.append('L' if cr>0 else 'R')
    print(k, 'lens', lens, 'turns', ''.join(turns))
    print('   points', [tuple(np.round(p,2)) for p in P])
    print('   end - start', np.round(P[-1]-P[0],2))
