import os.path
import os
import sys

from bottle import run, static_file, get, route
import chardet
import yaml

_version = '0.3.0-wip'
config = None
# pydeck_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
pydeck_path = os.path.abspath(os.path.curdir)
cfg_server_f = os.path.join(pydeck_path, 'config/server.yaml')
cfg_client_f = os.path.join(pydeck_path, 'config/client.yaml')

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
    global config
    with open_any_enc(cfg_server_f, 'r') as f:
        config = yaml.safe_load(f)
    print('---- config:')
    print(yaml.dump(config, default_flow_style=False, sort_keys=False))

@get('/')
@get('/<filename:re:(?!_action_|_config_).+>')
def get_static_file(filename: str='index.html'):
    return static_file(filename, root=os.path.join(pydeck_path, 'static/'))

@get('/_config_')
def get_config():
    with open_any_enc(cfg_client_f, 'r') as f:
        cfg = yaml.safe_load(f)
    return cfg

@route('/_action_/RELOAD')
def reload():
    load_cfg()
    return resp(0, 'ok')

@route('/_action_/<appid>')
def action(appid: str):
    ret = resp(404, f'Can not find app [{appid}]')
    for app in config['apps']:
        if app['id'] == appid:
            pre = str(config.get('pre-action', ''))\
                .replace('{PYDECK_PATH}', pydeck_path)\
                .replace('{APPID}', appid)
            post = str(config.get('post-action', ''))\
                .replace('{PYDECK_PATH}', pydeck_path)\
                .replace('{APPID}', appid)
            cmd = str(app['command'])\
                .replace('{PYDECK_PATH}', pydeck_path)\
                .replace('{APPID}', appid)
            pwd = str(app.get('workdir', '.'))\
                .replace('{PYDECK_PATH}', pydeck_path)\
                .replace('{APPID}', appid)
            print('')
            # 只考虑运行在 Windows 平台，为了和服务器进程独立开，用了 START
            # 如果要在 linux 平台运行，需要修改
            if pre:
                print('---- Run pre-action: {}'.format(pre))
                os.system('START "" /I {}'.format(pre))
            print('---- Run app[{}]: {}'.format(appid, cmd))
            os.system('START "[PyDeck] CMD" /I /D {} {}'.format(pwd, cmd))
            if post:
                print('---- Run post-action: {}'.format(post))
                os.system('START "" /I {}'.format(post))
            print('')
            ret = resp(0, 'success')
            break
    return ret

if __name__ == '__main__':
    print('---- version:', _version)
    load_cfg()
    run(host='0.0.0.0', port=config['port'], server='paste')
