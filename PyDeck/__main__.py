from datetime import datetime
import os.path
import os
import subprocess
import sys
from typing import Dict, List, Optional, Tuple, Union

from bottle import run, static_file, get, route
import chardet
import yaml
from PIL.ImageGrab import grab

_version = '0.3.0-wip'
pydeck_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
# pydeck_path = os.path.abspath(os.path.curdir)
cfg_server_f = os.path.join(pydeck_path, 'config/server.yaml')
cfg_client_f = os.path.join(pydeck_path, 'config/client.yaml')
web_root = os.path.join(pydeck_path, 'static/')

class ServerApp:
    def __init__(self, d: dict):
        self.id = d.get('id', None)
        if not self.id:
            raise ValueError('Invalid "id" in app config')
        self.program = str(d.get('program', '')).replace('{PYDECK_PATH}', pydeck_path)
        if not self.program:
            raise ValueError('Invalid "program" in app config')
        self.argument = str(d.get('argument', '')).replace('{PYDECK_PATH}', pydeck_path)
        self.workdir = str(d.get('workdir', '.')).replace('{PYDECK_PATH}', pydeck_path)
        self.runtype = d.get('runtype', 'sa')

class ServerCfg:
    def __init__(self, d: dict):
        self.port = d.get('port', 7777)
        self.pre_action = str(d.get('pre_action', '')).replace('{PYDECK_PATH}', pydeck_path)
        self.post_action = d.get('post_action', '').replace('{PYDECK_PATH}', pydeck_path)
        self.apps: Dict[str, ServerApp] = dict()
        for app in d['apps']:
            sa = ServerApp(app)
            self.apps[sa.id] = sa

def open_any_enc(filename, mode='r', default_encoding='ascii'):
    """ open “自动识别文件编码”版本

    :param default_encoding: (str) 万一没有识别出文件编码时使用的缺省编码
    """
    r = None
    with open(filename, 'rb') as f:
        d = chardet.UniversalDetector()
        for l in f:
            d.feed(l)
            if d.done:
                break
        r = d.close()
    encoding = r['encoding'] if r and r['encoding'] else default_encoding
    return open(filename, mode, encoding=encoding)

def resp(errcode:int, msg:str, data:Optional[Union[Dict, List]]=None):
    return {'errcode': errcode, 'msg':msg, 'data':data}

def load_cfg():
    with open_any_enc(cfg_server_f, 'r') as f:
        d = yaml.safe_load(f)
    print('---- config:')
    print(yaml.dump(d, default_flow_style=False, sort_keys=False))
    return ServerCfg(d)

@get('/')
@get('/<filename:re:(?!_action_|_config_).+>')
def get_static_file(filename: str='index.html'):
    return static_file(filename, root=os.path.join(pydeck_path, 'static/'))


class Layout:
    def __init__(self, x_grid:int):
        self.x_grid = x_grid
        self._layout = []
        self._line_cnt = 0
        self._x = 0
        self._y = 0

    @property
    def X(self):
        return self._x

    @X.setter
    def X(self, v:int):
        if (self._x != v):
            # print(f'X: {self._x} -> {v}')
            self._x = v

    @property
    def Y(self):
        return self._y

    @Y.setter
    def Y(self, v:int):
        if (self._y != v):
            # print(f'Y: {self._y} -> {v}')
            self._y = v

    def _more_line(self, n:int=1):
        self._layout.extend([['']*self.x_grid for i in range(n)])
        self._line_cnt = len(self._layout)

    def _extend(self, y:int, x:int):
        if x > self.x_grid:
            y = y + x / self.x_grid
            # x = x % self.x_grid
        if (y + 1) > self._line_cnt:
            print('---- _extend:', y + 1 - self._line_cnt)
            self._more_line(y + 1 - self._line_cnt)

    def _reloc(self, t:int, l:int, h:int=1, w:int=1) -> Tuple[int, int]:
        if (l + w) > self.x_grid:
            print(f'---- _reloc: ({t},{l}) {w}x{h} -> ({t+1},0)')
            return t+1, 0
        return t, l

    def _is_empty(self, t, l, h, w) -> bool:
        self._extend(t+h-1, l+w-1)
        for y in range(t, t+h):
            for x in range(l, l+w):
                if self._layout[y][x]:
                    print(f'---- _is_empty: ({t}, {l}) {w}x{h} False')
                    return False
        print(f'---- _is_empty: ({t}, {l}) {w}x{h} True')
        return True

    def _put(self, appid:str, t, l, h, w):
        print(f'---- _put: ({t}, {l}) "{appid}" {w}x{h}')
        self._extend(t+h-1, l+w-1)
        for y in range(t, t+h):
            for x in range(l, l+w):
                self._layout[y][x] = appid

    def put(self, appid:str, h:int, w:int, t:Optional[int]=None, l:Optional[int]=None):
        print(f'-- put: ({self.Y}, {self.X}) "{appid}" {w}x{h} ({t},{l})')
        if w > self.x_grid:
            w = self.x_grid
        if (l is not None) and (t is not None):
            # t, l = self._reloc(t, l, h, w)
            # self._put(appid, t, l, h, w)
            return t, l, h, w
        else:
            self.Y, self.X = self._reloc(self.Y, self.X, h, w)
            while not self._is_empty(self.Y, self.X, h, w):
                self.Y, self.X = self._reloc(self.Y, self.X+1, h, w)
            self._put(appid, self.Y, self.X, h, w)
            ret = (self.Y, self.X, h, w)
            self.Y, self.X = self._reloc(self.Y, self.X + w)
            return ret

    def newline(self):
        print('-- newline')
        self.X = 0
        self.Y = self.Y + 1
        self._extend(self.Y, self.X)

    def print(self):
        for y in range(self._line_cnt):
            print(' | '.join('{:<10}'.format(self._layout[y][x]) for x in range(self.x_grid)))


@get('/_config_')
def get_client_config():
    with open_any_enc(cfg_client_f, 'r') as f:
        cfg = yaml.safe_load(f)
    cfg.setdefault('slogan', '')
    cfg.setdefault('theme', 'dark')
    cfg.setdefault('show_label', True)
    cfg.setdefault('bg_image', '')
    x_grid = cfg.setdefault('x_grid', 12)
    cfg.setdefault('default_icon_width', 1)
    cfg.setdefault('default_icon_height', cfg['default_icon_width'])
    for app in cfg['apps']:
        if not app: continue
        app.setdefault('width', cfg['default_icon_width'])
        app.setdefault('height', cfg['default_icon_height'])
        app.setdefault('left', None)
        app.setdefault('top', None)
        app.setdefault('z_index', 1)
    layout = Layout(x_grid)
    for app in cfg['apps']:
        if app:
            if (app['left'] is not None) and (app['top'] is not None):
                app['z_index'] = 2
            app['top'], app['left'], app['height'], app['width'] = layout.put(app['id'], app['height'], app['width'], app['top'], app['left'])
        else:
            layout.newline()
    layout.print()
    return cfg

@route('/_server_/RELOAD')
def reload():
    global config
    config = load_cfg()
    return resp(0, 'ok')

@route('/_server_/SCREENSHOT')
def screenshot():
    ss_fp = f'screenshot/{datetime.now().strftime("%Y%m%d-%H%M%S")}.png'
    try:
        grab().save(os.path.join(web_root, ss_fp))
    except Exception as e:
        return resp(1, f'error: {e.__str__()}')
    return resp(0, 'ok', {'js': f"setTimeout(show_screenshot,1000,'/{ss_fp}');"})

@route('/_action_/<appid>')
def action(appid: str):
    global config
    ret = resp(404, f'Can not find app [{appid}]')
    app = config.apps.get(appid, None)
    if app:
        pre = config.pre_action.replace('{APPID}', appid)
        post =config.post_action.replace('{APPID}', appid)
        print('')
        # 只考虑运行在 Windows 平台，为了和服务器进程独立开，用了 START
        # 如果要在 linux 平台运行，需要修改
        if pre:
            print(f'---- Run pre-action: {pre}')
            os.system(f'START "" /I {pre}')
        print(f'---- Run [{app.runtype}] app [{appid}]: {app.program} {app.argument}')
        if app.runtype == 'sa':
            os.system(f'START "[PyDeck] CMD" /I /D {app.workdir} {app.program} {app.argument}')
        else:
            pass
        if post:
            print(f'---- Run post-action: {post}')
            os.system(f'START "" /I {post}')
        print('')
        ret = resp(0, 'success')
    return ret

if __name__ == '__main__':
    print('---- version:', _version)
    config = load_cfg()
    run(host='0.0.0.0', port=config.port, server='paste')
