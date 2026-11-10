"""Material specs for ZL4B. segs are 0-based page, y0, y1 in PDF points."""
MATS = {
    'ZLM-JS2023A-1': dict(tag='JS2023A_xc', label='一、根据以下资料，回答116~120题。', segs=[[27, 477.0, 679.8]], qnos=list(range(116, 121))),
    'ZLM-ZJ2015A-3': dict(tag='ZJ2015A', label='(材料3)', segs=[[14, 31.0, 414.5]], qnos=list(range(121, 126))),
    'ZLM-GK2022X-4': dict(tag='GK2022X', label='（资料第4则，无序号）', segs=[[19, 662, 816], [20, 33, 73.3]], qnos=list(range(126, 131)), reuse=True),
    'ZLM-ZJ2017A-1': dict(tag='ZJ2017A', label='(一)', segs=[[13, 447.5, 617.5]], qnos=list(range(111, 116))),
    'ZLM-GK2016D-3': dict(tag='GK2016D', label='(三)', segs=[[13, 734.5, 803.5], [14, 31.5, 114.0]], qnos=list(range(121, 126))),
    'ZLM-JS2016A-1': dict(tag='JS2016A', label='(材料)', segs=[[12, 572.5, 713.5]], qnos=list(range(116, 121))),
    'ZLM-JS2018A-3': dict(tag='JS2018A', label='（本则无标号，下一则标“（四）”）', segs=[[15, 767.0, 797.0], [16, 34.5, 113.5]], qnos=list(range(116, 121))),
    'ZLM-ZJ2020B-2': dict(tag='ZJ2020B_xc', label='(材料2)', segs=[[11, 215.5, 594.5]], qnos=list(range(91, 96))),
}
