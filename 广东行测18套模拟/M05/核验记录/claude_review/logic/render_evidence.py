# Re-render the original JS PDF pages (200 dpi) and cut every evidence screenshot used in findings.md.
# Source PDFs: shallow clone /home/user/dumarstoft-ship-it/xingce @407016b (blob 959016a… = 2021 A卷, 0c2016b… = 2022 A类).
# bbox values are PDF points (1/72 in) -> pixels x 200/72. Read-only on both repos; outputs go to this directory.
import subprocess, os
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__)); os.makedirs(f'{HERE}/pages',exist_ok=True)
P21='/home/user/dumarstoft-ship-it/xingce/2021年江苏公务员考试《行测》真题（A卷）.pdf'
P22='/home/user/dumarstoft-ship-it/xingce/2022年江苏公务员考试《行测》真题（A类）....pdf'
for pdf,first,last,prefix in [(P21,12,14,'js2021'),(P22,16,17,'js2022')]:
    subprocess.run(['pdftoppm','-r','200','-f',str(first),'-l',str(last),'-png',pdf,f'{HERE}/pages/{prefix}'],check=True,capture_output=True)
S=200/72
def crop(page,x0,y0,x1,y1,out,zoom=1,note=''):
    im=Image.open(f'{HERE}/pages/{page}.png')
    box=(int(x0*S),int(y0*S),int(x1*S),int(y1*S)); c=im.crop(box)
    if zoom>1: c=c.resize((c.width*zoom,c.height*zoom),Image.LANCZOS)
    c.save(f'{HERE}/{out}'); print(f'{out}: page={page} bbox_pt=({x0},{y0},{x1},{y1}) px={box} zoom={zoom} | {note}')
crop('js2021-14',30,20,560,230,'shot_js2021_p14_top_q99-100.png',1,'JS2021 第99-100题：引导为“(材料)”，材料首行排满于“白玉”、次行“隧道。已知：”续排；（1）（2）各一行；第100题设问一行')
crop('js2021-14',38.0,57.26,555.16,123.71,'shot_js2021_p14_material_M02.png',1,'JS2021-M02 材料区域（source.regions bbox±4pt）')
crop('js2021-14',38.0,171.38,460.61,222.95,'shot_js2021_p14_q100.png',1,'JS2021-A类-100 题干与选项区域')
crop('js2021-14',200,60,420,78,'shot_js2021_p14_colon_zoom.png',3,'“有 6 条隧道:长川”：原卷数字两侧为排版间距，冒号为半角')
crop('js2021-12',30,655,560,740,'shot_js2021_p12_q92.png',1,'JS2021-A类-092：题干一行，设问另起一行')
crop('js2021-12',40,666,330,684,'shot_js2021_p12_q92_colon_zoom.png',3,'“古人云:立”冒号为半角（原卷如此）')
crop('js2021-13',30,250,560,400,'shot_js2021_p13_q95.png',1,'JS2021-A类-095：前三行排满于“成/心仪/追”，第四行“捧。”，设问另起')
crop('js2021-13',30,398,560,530,'shot_js2021_p13_q96.png',1,'JS2021-A类-096：前两行排满于“人类/人群”，设问另起')
crop('js2022-17',25,20,560,265,'shot_js2022_p17_q98-99.png',1,'JS2022 第98-99题：引导为粗体“材料”；首行排满于“交替领”；张/王/李/赵各一行；“比赛结束后”段排满于“张”')
crop('js2022-17',250,220,400,240,'shot_js2022_p17_q99_qmark_zoom.png',3,'“一定为真?”问号为半角（原卷如此）')
crop('js2022-16',25,700,560,842,'shot_js2022_p16_bottom.png',1,'JS2022 第16页页底：材料前无“98~99题基于…”引导语')
