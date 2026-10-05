#!/usr/bin/env python3
"""Capture real curses cells in a PTY; export faithful SVGs for visual review.

Win and loss use ordinary legal-input replays, then the same application renderer.
No game state is assigned to manufacture a result. This checks rendering, not
real-time human play. JSON retains character, foreground, background and attributes.
"""
import argparse
import curses
import html
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tink_pong.engine import Game
from tink_pong.ui import Renderer
from scripts.pong_replay import play

OUTPUT = ROOT / 'runs/pong/04-test/output/captures'


def screen_capture(screen, destination, monochrome):
    screen.keypad(True)
    curses.curs_set(0)
    renderer = Renderer(screen, monochrome)
    game = Game()
    # Capture each state immediately, because serve/rally/pause share one game.
    def save(name, game):
        renderer.draw(game, False, 'key sound off')
        rows,cols = screen.getmaxyx()
        cells=[]
        for y in range(rows):
            row=[]
            for x in range(cols):
                cell=screen.inch(y,x)
                pair=curses.pair_number(cell)
                fg,bg = curses.pair_content(pair) if pair else (7,0)
                row.append([chr(cell & curses.A_CHARTEXT),fg,bg,bool(cell & curses.A_BOLD),bool(cell & curses.A_REVERSE),bool(cell & curses.A_DIM)])
            cells.append(row)
        (destination/f'{name}.json').write_text(json.dumps(dict(rows=rows,cols=cols,cells=cells,state=game.snapshot())))
    save('serve',game)
    game.launch();game.advance(.1);save('rally',game)
    game.toggle_pause();save('pause',game)
    for player,name in ((True,'win'),(False,'loss')):
        game,_=play(player);save(name,game)


def color(index):
    basic=['#000000','#cd0000','#00cd00','#cdcd00','#0000ee','#cd00cd','#00cdcd','#e5e5e5',
           '#7f7f7f','#ff0000','#00ff00','#ffff00','#5c5cff','#ff00ff','#00ffff','#ffffff']
    if index<16:return basic[index]
    if index>=232:
        value=8+(index-232)*10;return f'#{value:02x}{value:02x}{value:02x}'
    index-=16;levels=[0,95,135,175,215,255]
    return '#'+''.join(f'{levels[n]:02x}' for n in (index//36,(index//6)%6,index%6))


def svg(path):
    data=json.loads(path.read_text());w,h=data['cols']*10,data['rows']*20
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="700" height="{700*h/w}" viewBox="0 0 {w} {h}">']
    for y,row in enumerate(data['cells']):
        for x,(char,fg,bg,bold,reverse,dim) in enumerate(row):
            if reverse:fg,bg=bg,fg
            parts.append(f'<rect x="{x*10}" y="{y*20}" width="10" height="20" fill="{color(bg)}"/>')
            if char!=' ':
                parts.append(f'<text x="{x*10}" y="{y*20+15}" fill="{color(fg)}" font-family="Menlo,monospace" font-size="15" font-weight="{"bold" if bold else "normal"}" opacity="{.65 if dim else 1}">{html.escape(char)}</text>')
    parts.append('</svg>');path.with_suffix('.svg').write_text('\n'.join(parts))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--child',type=Path);parser.add_argument('--mono',action='store_true');args=parser.parse_args()
    if args.child:
        curses.wrapper(screen_capture,args.child,args.mono);return
    import fcntl,pty,select,struct,termios
    for cols,rows in ((80,30),(100,35)):
        for mono in (False,True):
            directory=OUTPUT/f'{cols}x{rows}-{"mono" if mono else "color"}';directory.mkdir(parents=True,exist_ok=True)
            master,slave=pty.openpty();fcntl.ioctl(slave,termios.TIOCSWINSZ,struct.pack('HHHH',rows,cols,0,0))
            proc=subprocess.Popen([sys.executable,'-B',__file__,'--child',str(directory)]+(['--mono'] if mono else []),
                stdin=slave,stdout=slave,stderr=slave,cwd=ROOT,env=dict(os.environ,TERM='xterm-256color'))
            raw=bytearray();deadline=time.monotonic()+10
            try:
                while proc.poll() is None and time.monotonic()<deadline:
                    if select.select([master],[],[],.02)[0]:raw.extend(os.read(master,65536))
                if proc.poll() is None:raise RuntimeError('Capture timed out')
                if proc.returncode:raise RuntimeError(raw.decode(errors='replace'))
                (directory/'terminal.ansi').write_bytes(raw)
            finally:
                if proc.poll() is None:proc.kill()
                proc.wait();os.close(master);os.close(slave)
            for path in directory.glob('*.json'):svg(path)
    print(f'Captured 20 real curses screens to {OUTPUT}')


if __name__=='__main__':main()
