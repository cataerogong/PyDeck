import os.path
import os
import subprocess
import sys
from typing import Dict

from bottle import run, static_file, get, route
import chardet
import yaml

_version = '0.3.0-wip'
pydeck_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
# pydeck_path = os.path.abspath(os.path.curdir)
cfg_server_f = os.path.join(pydeck_path, 'config/server.yaml')
cfg_client_f = os.path.join(pydeck_path, 'config/client.yaml')

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

def resp(errcode:int, msg:str):
    return {'errcode': errcode, 'msg':msg}

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

@get('/_config_')
def get_client_config():
    with open_any_enc(cfg_client_f, 'r') as f:
        cfg = yaml.safe_load(f)
    cfg['grid_size'] = (100.0 / cfg['x_grid'])
    # try:
    #     cfg['default_icon_width'] = str(cfg['grid_size'] * int(cfg['default_icon_width'])) + '%'
    # except Exception as e:
    #     print(e)
    if cfg['layout'] == 'stream':
        for app in cfg['apps']:
            if app:
                app['width'] = cfg['default_icon_width']
    return cfg

@route('/_action_/RELOAD')
def reload():
    global config
    config = load_cfg()
    return resp(0, 'ok')

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
