import os,pty,fcntl,termios,struct,subprocess,select,time,signal,html,json
from pathlib import Path
import pyte
root=Path('/Users/jondev/dev/active/product/tink-arcade-snake')
out=Path('/tmp/snake-visual')
sections=[];results=[]
for cols,rows in [(80,30),(100,35)]:
 for mono in [False,True]:
  for module in ['neon_tetris','tink_snake']:
   master,slave=pty.openpty();fcntl.ioctl(slave,termios.TIOCSWINSZ,struct.pack('HHHH',rows,cols,0,0))
   screen=pyte.Screen(cols,rows)
   for y in range(rows):
    for x in range(cols):screen.buffer[y][x]=screen.default_char
   stream=pyte.Stream(screen);raw=bytearray()
   args=['/usr/bin/env','python3','-B','-m',module,'--seed','1','--no-sound']+(['--no-color'] if mono else [])
   proc=subprocess.Popen(args,cwd=root,env=dict(os.environ,TERM='xterm-256color'),stdin=slave,stdout=slave,stderr=slave,start_new_session=True)
   def pump(seconds):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
     if select.select([master],[],[],.01)[0]:
      b=os.read(master,65536);raw.extend(b);stream.feed(b.decode(errors='replace'))
   def save(state):
    title=f'{module} {cols}x{rows} {"monochrome" if mono else "color"} {state}'
    lines=[]
    for y in range(rows):
     chunks=[]
     for x in range(cols):
      c=screen.buffer[y][x]
      def color(v,default):return default if v=='default' else '#'+v if len(v)==6 else v
      fg=color(c.fg,'#dddddd');bg=color(c.bg,'#161616')
      if c.reverse:fg,bg=bg,fg
      chunks.append(f'<span style="color:{fg};background:{bg};font-weight:{"bold" if c.bold else "normal"}">{html.escape(c.data)}</span>')
     lines.append(''.join(chunks))
    sections.append('<section><h2>'+title+'</h2><pre>'+ '\n'.join(lines)+'</pre></section>')
    text='\n'.join(screen.display)
    results.append({'title':title,'state_label_visible':state=='play' or ('PAUSED' if state=='pause' else 'GAME OVER') in text})
    (out/(title.replace(' ','_')+'.txt')).write_text(text)
   try:
    
    deadline=time.monotonic()+5
    while not any('paper '+('snake' if module=='tink_snake' else 'tetris') in row for row in screen.display) and time.monotonic()<deadline:pump(.02)
    assert any('PLAY / PAPER' in row for row in screen.display), 'No initial game frame'
    save('play');os.write(master,b'p');pump(.15);save('pause');os.write(master,b'p');pump(.05)
    if module=='neon_tetris':
     for i in range(25):os.write(master,b' ');pump(.025)
    else:pump(2.3)
    save('game-over');os.write(master,b'q');pump(.1);proc.wait(timeout=2)
   finally:
    if proc.poll() is None:os.killpg(proc.pid,signal.SIGTERM);proc.wait(timeout=3)
    os.close(master);os.close(slave)
   (out/f'{module}-{cols}-{mono}.ansi').write_bytes(raw)
(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Snake and Tetris terminal captures</title><style>body{background:#ddd;color:#222;font-family:system-ui;margin:24px}h2{font-size:15px}pre{font:14px/17px Menlo,monospace;display:inline-block;padding:0;margin:0}section{margin-bottom:36px}</style><h1>Actual PTY captures: Tetris and Snake</h1>'+''.join(sections))
(out/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
