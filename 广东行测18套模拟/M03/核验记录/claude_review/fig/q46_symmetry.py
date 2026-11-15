"""Q46: symmetry classification of the 3x3 black/white dot panels (transcribed from 1310.png, see crops/q46_*_x3.png).
Cells (row, col) 1..3; 'B' black, 'W' white. Checks: 180-degree rotation, and 4 reflection axes
(vertical, horizontal, main diagonal, anti-diagonal), with colours required to match."""
P={
 'P1':{(1,1):'B',(2,1):'W',(2,2):'B',(2,3):'W',(3,3):'B'},
 'P2':{(1,1):'W',(1,2):'B',(1,3):'W',(3,2):'B'},
 'P3':{(1,1):'B',(2,1):'W',(2,2):'W',(2,3):'W',(3,3):'B'},
 'P4':{(1,1):'W',(2,1):'B',(2,2):'B',(2,3):'B',(3,1):'W'},
 'P5':{(1,2):'B',(1,3):'B',(2,2):'W',(3,1):'B',(3,2):'B'},
 'A':{(1,1):'B',(1,3):'W',(2,2):'B',(3,1):'W',(3,3):'B'},
 'B':{(1,1):'B',(1,2):'W',(2,2):'W',(3,2):'W',(3,3):'B'},
 'C':{(1,1):'B',(1,3):'B',(2,2):'B',(3,1):'W',(3,3):'W'},
 'D':{(1,1):'B',(1,2):'W',(3,2):'B',(3,3):'W'},
}
maps={'rot180':lambda r,c:(4-r,4-c),'axis|':lambda r,c:(r,4-c),'axis-':lambda r,c:(4-r,c),
      'axis\\':lambda r,c:(c,r),'axis/':lambda r,c:(4-c,4-r)}
def sym(p,f): return all(p.get(f(r,c))==v for (r,c),v in p.items())
def sym_shape(p,f): return all(f(r,c) in p for (r,c) in p)
for k,p in P.items():
    col=[n for n,f in maps.items() if sym(p,f)]
    shp=[n for n,f in maps.items() if sym_shape(p,f)]
    central='rot180' in col; axes=[a for a in col if a!='rot180']
    kind=('central+axis' if central and axes else 'central only' if central else 'axis only' if axes else 'none')
    print(f"{k}: with colours -> {kind:13s} {col} | shape only -> {shp}")
