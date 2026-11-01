#!/usr/bin/env python3
"""dP狸 小红书 3:4 图文封面 v4：重点红、第二行叠图+渐变。
用法: python3 build.py [config.json] [输出目录] [变体: frame,warm,bleed]"""
import json, sys, os, subprocess, html, re
D = os.path.dirname(os.path.abspath(__file__))
cp = sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, 'config.json')
cfg = json.load(open(cp)); CD = os.path.dirname(os.path.abspath(cp))
out = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else D
variants = sys.argv[3].split(',') if len(sys.argv) > 3 else ['frame', 'warm', 'bleed']
W, H = 1242, 1656
INK, MINT, RED = '#111111', '#73fcd6', '#D93A2B'
P = lambda p: p if os.path.isabs(p) else os.path.join(CD, p)
FONT = P(cfg.get('font') or os.path.join(os.path.dirname(D), 'assets', 'fonts', 'YueDongHei.ttf'))
IMG = P(cfg['image']) if cfg.get('image') else ''
POS = cfg.get('image_position', 'center')
LOGO_DIR = os.path.join(os.path.dirname(D), 'assets', 'logo')

MODE = cfg.get('period_mode', 'dot')  # dot：logo 直接当句号；ring：句号圆圈里放 logo
def logo(color):
    """定稿矢量 logo（r4_4_pupils_black.svg），去底 rect，裁到图形边界，线色随背景，红鼻尖保留。"""
    svg = open(os.path.join(LOGO_DIR, 'r4_4_pupils_black.svg')).read()
    svg = re.sub(r'<rect[^>]*/>', '', svg, count=1).replace('#111111', color)
    svg = svg.replace('width="1024" height="1024" viewBox="0 0 1024 1024"', 'width="100%" height="100%" viewBox="159 176 687 647"')
    return svg

def logo_mono(color):
    """花纹用：定稿矢量，单色，鼻尖也改成同色。"""
    svg = open(os.path.join(LOGO_DIR, 'r4_4_pupils_black.svg')).read()
    svg = re.sub(r'<rect[^>]*/>', '', svg, count=1)
    svg = svg.replace('#111111', color).replace('#D93A2B', color)
    svg = svg.replace('width="1024" height="1024" viewBox="0 0 1024 1024"',
                      'width="100%" height="100%" viewBox="159 176 687 647"')
    return svg

def pattern(opacity=0.08, size=72, gap=110, rot=-18, strong=False):
    """黑底 logo 暗纹：倾斜错位网格，仅铺在顶部黑区，到底图渐变处用 mask 淡出。"""
    if strong:
        opacity = 0.14
    # tile: size + gap spacing; staggered every other row
    cell = gap
    cols = int(W / cell) + 3
    rows = int((H - W + 200) / cell) + 3  # cover black band + a bit into fade
    items = []
    for r in range(rows):
        for c in range(cols):
            x = int(c * cell + (cell * 0.5 if r % 2 else 0) - cell)
            y = int(r * cell - cell * 0.3)
            items.append(
                f'<div class="pt" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px;'
                f'opacity:{opacity}">{logo_mono(MINT)}</div>'
            )
    # pattern layer height covers black + fade zone; mask fades at image top
    ph = H - W + 400  # into the image fade
    return (
        f'<div class="pat" style="height:{ph}px;transform:rotate({rot}deg);'
        f'transform-origin:50% 40%;'
        f'-webkit-mask-image:linear-gradient(to bottom,#000 0%,#000 55%,transparent 92%);'
        f'mask-image:linear-gradient(to bottom,#000 0%,#000 55%,transparent 92%)">'
        + ''.join(items) + '</div>'
    )


# 悦动黑「。」(U+3002) 实测（1em=1000 单位）：外圈 x16–258；内圈 x88–186、y 基线上 -40–+54；内圈圆心 (0.137em, 基线上 0.007em)，内径约 0.093em
# 悦动黑「。」外径约 0.24em，圆心 (0.137em, 基线上 0.008em)
PC_X, PC_Y = 0.137, 0.008
FILL_EM = 0.24          # 实心黑点，盖住内孔，外径对齐字形
LOGO_EM = 0.185         # 笔画最远点半径=0.589×LOGO_EM≈0.109em，黑点半径0.12em，内边距约9%
def period(logo_color=None, mode=None):
    """字体句号 + 同位置实心黑点填充 + logo 叠在上层（可大于句号）。浅/深底一律薄荷线+红鼻。"""
    lc = MINT  # 实心黑点上必须用亮色线
    return (
        f'<span class="anc">'
        f'<span class="fill" style="left:{PC_X-FILL_EM/2:.4f}em;top:{-PC_Y-FILL_EM/2:.4f}em;width:{FILL_EM}em;height:{FILL_EM}em"></span>'
        f'<span class="lg" style="left:{PC_X-LOGO_EM/2:.4f}em;top:{-PC_Y-LOGO_EM/2:.4f}em">{logo(lc)}</span>'
        f'</span>'
        f'<span class="stop" style="color:{INK}">。</span>'
    )

def lines():
    """拆成第一行（上方文字区）与第二行/重点行（叠图）。"""
    L = cfg['lines']; hl = set(cfg.get('highlight') or [])
    if len(L) >= 2:
        top, bot = L[:-1], L[-1]
        bot_hl = (len(L) - 1) in hl
    else:
        top, bot, bot_hl = L, '', False
    return top, bot, bot_hl

def top_html(ink):
    top, _, _ = lines()
    return ''.join(f'<div><span class="ln" style="color:{ink}">{html.escape(l)}</span></div>' for l in top)

def bot_html(style, pc=INK, mode=None):
    _, bot, _ = lines()
    if not bot: return ''
    return f'<div class="bot"><span class="ln" style="{style}">{html.escape(bot)}{period(pc, mode)}</span></div>'

def img(style=''):
    bg = f"background-image:url('file://{IMG}');background-position:{POS};" if IMG else f'background:{MINT};'
    return f'<div class="img" style="{bg}{style}"></div>'

def fade(color, h=280):
    return (f'<div class="fade" style="height:{h}px;background:linear-gradient(to bottom,'
            f'{color} 0%,{color}00 100%)"></div>')

M = 72
S = W - 2 * M
IS = round(S * cfg.get('image_scale', 0.92))
IL = (W - IS) // 2
LG = 96
G = IL
# 图片顶边 y；第二行从顶边向上伸出一部分、向下叠进图片
IMG_Y = H - M - IS
FADE_H = 320
UP1 = cfg.get('lift_line1', 150)  # frame/warm 第一行上移量
UP2 = cfg.get('lift_line2', 110)  # frame/warm 第二行上移量

RM = cfg.get('red_mode', '')
LS = cfg.get('letter_spacing', -0.015)
DROP = cfg.get('line2_drop', 0)  # bleed 第二行下移 px，拉开行距
BLEED_FADE = fade(INK, 360)
BLEED_RED = f"color:{RED}"
if RM == 'A':   # 提亮红 + 更深更长的黑渐变
    BLEED_RED = "color:#FF3B2F"
    BLEED_FADE = (f'<div class="fade" style="height:560px;background:linear-gradient(to bottom,'
                  f'{INK} 0%,{INK} 38%,{INK}cc 60%,{INK}00 100%)"></div>')
elif RM == 'B': # 红色实心块贴字 + 白字
    BLEED_RED = f"color:#FFFFFF;background:{RED};padding:0 .06em .02em"
elif RM in ('C', 'C_green'): # 红/绿字 + 小范围黑色柔光
    BLEED_RED = (f"color:{RED if RM == 'C' else MINT};text-shadow:0 0 .03em rgba(0,0,0,.95),0 0 .09em rgba(0,0,0,.85),0 0 .2em rgba(0,0,0,.6)")

LAYOUTS = {
  # 白底；重点行红字叠图；图顶白→透明渐变；薄荷框点缀；黑线 logo
  'frame': (MINT,
            f'<div style="position:absolute;left:{IL}px;top:{IMG_Y}px;width:{IS}px;height:{IS}px;border:4px solid {RED};overflow:hidden">'
            f'{img()}{fade(MINT, FADE_H)}</div>'
            f'<div class="txt" style="left:{M}px;top:48px;width:{S}px;height:{IMG_Y-48-20-UP1}px">'
            f'<div class="t">{top_html(INK)}</div></div>'
            f'<div class="ov" style="left:{M}px;top:{IMG_Y-20-UP1+15}px;width:{S}px">{bot_html(f"color:{RED};text-shadow:0 0 .05em rgba(255,255,255,.55),0 0 .14em rgba(255,255,255,.35)")}</div>'),
  # 绿底；图在上字在下；行距与 frame 完全一致（txt 底与 ov 顶相差 15px）
  'flip': (MINT,
            # 图在上字在下；两行整体上移压图（相对贴底版再上移 100px），行距不变
            f'<div style="position:absolute;left:{IL}px;top:{M}px;width:{IS}px;height:{IS}px;border:4px solid {RED};overflow:hidden">'
            f'{img()}'
            f'<div class="fade" style="top:auto;bottom:0;height:{FADE_H+60}px;background:linear-gradient(to top,{MINT} 0%,{MINT}00 100%)"></div></div>'
            f'<div class="txt" style="left:{M}px;top:{H-48-357-15-300}px;width:{S}px;height:300px">'
            f'<div class="t">{top_html(INK)}</div></div>'
            f'<div class="ov" style="left:{M}px;top:{H-48-357}px;width:{S}px">{bot_html(f"color:{RED};text-shadow:0 0 .05em rgba(255,255,255,.55),0 0 .14em rgba(255,255,255,.35)")}</div>'),
  # 绿底；图在上；两行都在图下绿底（备选）
  'flip_below': (MINT,
            f'<div style="position:absolute;left:{IL}px;top:{M}px;width:{IS}px;height:{IS}px;border:4px solid {RED};overflow:hidden">'
            f'{img()}</div>'
            f'<div class="txt" style="left:{M}px;top:{M+IS+40}px;width:{S}px;height:{H-(M+IS+40)-M}px;justify-content:flex-start">'
            f'<div class="t">{top_html(INK)}'
            f'<div style="height:35px"></div>{bot_html(f"color:{RED}")}</div></div>'),
  # 暖白底；重点行红字叠图；图顶暖白渐变；黑线 logo
  'warm': ('#FEF8F1',
           f'<div style="position:absolute;left:{IL}px;top:{IMG_Y}px;width:{IS}px;height:{IS}px;overflow:hidden">'
           f'{img()}{fade("#FEF8F1", FADE_H)}</div>'
           f'<div class="txt" style="left:{M}px;top:48px;width:{S}px;height:{IMG_Y-48-20-UP1}px">'
           f'<div class="t">{top_html(INK)}</div></div>'
           f'<div class="ov" style="left:{M}px;top:{IMG_Y-40-UP2}px;width:{S}px">{bot_html(f"color:{RED}")}</div>'),
  # 近黑底；第一行白字；重点行红字叠图；图顶黑→透明；薄荷线 logo
  'bleed': (INK,
            f'{pattern(opacity=cfg.get("pattern_opacity", 0.08), size=cfg.get("pattern_size", 72), gap=cfg.get("pattern_gap", 118), rot=cfg.get("pattern_rot", -18), strong=cfg.get("pattern_strong", False))}'
            f'<div style="position:absolute;left:0;top:{H-W}px;width:{W}px;height:{W}px;overflow:hidden">'
            f'{img()}{BLEED_FADE}</div>'
            f'<div class="txt" style="left:{M}px;top:36px;width:{S}px;height:{H-W-36-20}px">'
            f'<div class="t">{top_html("#FFFFFF")}</div></div>'
            f'<div class="ov" style="left:{M}px;top:{H-W-40+DROP}px;width:{S}px">{bot_html(BLEED_RED, MINT)}</div>'),
}

# 字号：以 .txt 宽度为基准，同时测量第一行和第二行，取最长的撑满
FIT_JS = '''<script>document.fonts.ready.then(()=>{
const box=document.querySelector('.txt'), t=box.querySelector('.t'), ov=document.querySelector('.ov');
const all=[...t.querySelectorAll('.ln'), ...ov.querySelectorAll('.ln')];
const mw=()=>Math.max(...all.map(e=>e.offsetWidth||0));
let fs=220; t.style.fontSize=fs+'px'; if(ov) ov.style.fontSize=fs+'px';
for(let i=0;i<5;i++){fs=fs*box.clientWidth/mw()*1.0; t.style.fontSize=fs+'px'; if(ov) ov.style.fontSize=fs+'px';}
const used=()=>[...t.children].reduce((a,e)=>a+e.offsetHeight,0);
while(used()>box.clientHeight&&fs>40){fs*=0.97; t.style.fontSize=fs+'px'; if(ov) ov.style.fontSize=fs+'px';}
document.body.dataset.ratio=(mw()/box.clientWidth).toFixed(3)+'|'+(mw()/1242).toFixed(3);
});</script>'''

CSS = f'''@font-face{{font-family:YD;src:url('file://{FONT}')}}
*{{margin:0;padding:0;box-sizing:border-box}} body{{overflow:hidden}}
.pg{{position:relative;width:{W}px;height:{H}px;overflow:hidden}}
.txt{{position:absolute;display:flex;flex-direction:column;justify-content:flex-end;overflow:hidden;z-index:3}}
.t,.ov{{font-family:YD;font-weight:400;font-synthesis:none;letter-spacing:{LS}em;line-height:1.0;white-space:nowrap}}
.ov{{position:absolute;z-index:3;pointer-events:none}}
.ln{{display:inline-block}}
.fade{{position:absolute;left:0;top:0;width:100%;z-index:2;pointer-events:none}}
.anc{{display:inline-block;width:0;height:0;vertical-align:baseline;position:relative;z-index:5}}
.anc .fill{{position:absolute;border-radius:50%;background:{INK};z-index:1}}
.anc .lg{{position:absolute;width:{LOGO_EM}em;height:{LOGO_EM}em;line-height:0;z-index:2}}
.lg svg{{display:block}}
.stop{{margin-right:-.55em;position:relative;z-index:0}}
.img{{width:100%;height:100%;background-size:cover;background-repeat:no-repeat}}.pat{{position:absolute;left:-20%;top:-8%;width:140%;z-index:1;pointer-events:none;overflow:hidden}}.pat .pt{{position:absolute;line-height:0}}.pat .pt svg{{display:block;width:100%;height:100%}}'''

SUFFIX = cfg.get('suffix', '')
os.makedirs(out, exist_ok=True)
for v in variants:
    bg, body = LAYOUTS[v]
    doc = f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="pg" style="background:{bg}">{body}</div>{FIT_JS}</body></html>'
    hp = os.path.join(out, f'xhs_{v}{SUFFIX}.html'); open(hp, 'w').write(doc)
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--hide-scrollbars', '--allow-file-access-from-files',
                    '--virtual-time-budget=4000', f'--window-size={W},{H}', f'--screenshot={hp[:-5]}.png', 'file://' + hp], capture_output=True)
    print(hp[:-5] + '.png')
