# -*- coding: utf-8 -*-
# 魔改了 AutoCleaner
import copy
import time
import json
import os

Prefix = '!!clear'
die = ''
item_counter = False
tag = False

ConfigFileFolder = './plugins/config/'
ConfigFilePath = ConfigFileFolder + 'AutoCleaner.json'

HelpMessage = '''
§7------------§bMCD ClearItem§7------------
一个扫地机插件(在白名单中物品可以避免被删除)
§7''' + Prefix + ''' §r清理物品
§7''' + Prefix + ''' help §r 显示帮助信息
§7''' + Prefix + ''' whitelist add <物品> §r添加<物品>进入白名单
§7''' + Prefix + ''' whitelist remove <物品> §r从白名单中删除<物品>
§7''' + Prefix + ''' whitelist list §r显示白名单中已有的物品'''

#帮助信息
def help_message(server ,info):
    server.tell(info.player,HelpMessage)
    
#MCDR-帮助信息
def on_load(server ,old):
    server.add_help_message(Prefix,'清理掉落物')
    if not os.path.isfile(ConfigFilePath):
        server.logger.info('[扫地] 未找到配置文件，已自动生成')
        with open(ConfigFilePath, 'w+') as f:
            f.write('[{"item_name": []}]')
            f.close()

    
#死亡检测
def on_death_message(server, death_message):
    global die
    death_split = death_message.split(' ')
    if death_split[0].lower().startswith('bot'):
        pass
    else:
        die = death_split[0] + ' ' + str(round(time.time() * 1000))
        server.say('[§2扫地§r] §4警告 ' + death_split[0] + ' 死亡 5 Min 内无法扫地!')
               
    
def on_info(server ,info):
    global tag
    global die
    global item_counter
    content = info.content
    command = content.split(' ')
    
    #清理物品总数统计
    if item_counter == True:
        if command[1].isdigit() == True:
            server.say('[§2扫地§r] §2共清理 §4{} §2物品'.format(command[1]))
            item_counter = False
            return
        elif content.find('No entity was found') != -1:
            server.say('[§2扫地§r] §2共清理 §4 0 §2物品')
        elif content.find('No entity was found') == -1:
            server.say('[§2扫地§r] §2共清理 §41 §2物品')
        item_counter = False
        
        
    if len(command) == 0 or command[0] != Prefix:
        return
    del command[0]
    
    #检测是否为玩家或者控制台输入
    if not info.is_user:
        return
            
    #直接清理所有物品
    elif len(command) == 0:
        if die != '':
            tick = die.split(' ') # 分割空格
            me = int(round(time.time() * 1000)) - int(tick[1]) # 当前时间 - 死亡时间
            # server.say(str(me))
            if me <= 300000: # 判断时间是否大于300000毫秒
                server.say('[§2扫地§r] §4警告 5 Min 内 ' + tick[0] + ' 死亡,操作被阻止!')
                server.tell(tick[0], '[§2扫地§r] ' + info.player + ' §4请求扫地! 请确保装备捡完,输入 ' + Prefix + ' yes 同意,拒绝不用管.')
                pass
            else:
                die = '' # 清空变量
                if tag == False: # 判断tag是否为 否 否则开始
                    kill(server)
                else:
                    tag = False
        else:
            if tag == False: # 判断tag是否为 否 否则开始
                kill(server)
            else:
                tag = False



    elif len(command) == 1 and command[0] == 'help':
        help_message(server ,info)


    elif len(command) == 1 and command[0] == 'yes':
        if die != '':
            tick = die.split(' ') # 分割空格
            if info.player == tick[0]: # 判断操作玩家是否是死亡玩家
                die = ''
                server.say('[§2扫地§r] §4阻止清理已关闭!')
            else:
                server.tell(info.player, '又不是你死了!')
        else:
            server.tell(info.player, '没有人死亡!')

    #测试
    elif len(command) == 1 and command[0] == 'w':
        die = info.player + ' ' + str(round(time.time() * 1000)) # 写入测试变量
    elif len(command) == 2 and command[0] == 'w':
        die = info.player + ' ' + command[1] # 写入测试变量

    #白名单相关
    elif len(command) in [2,3] and command[0] == 'whitelist':
        if command[1] == 'list':
            with open(ConfigFilePath, 'r') as f:
                js = json.load(f)
                lines = js[0]["item_name"]
                server.tell(info.player ,'§7--------§bMCD Cleaner Whitelist§7--------')
                for i in range(len(lines)):
                    name = lines[i].replace('\n', '').replace('\r', '')
                    server.tell(info.player,'§e' + name)
        elif command [1] == 'add' and len(command) == 3:
            api = server.get_plugin_instance('MinecraftItemAPI') #从MinecraftItemAPI获取物品信息
            if api.getMinecraftItemInfo(command[2]):
                with open(ConfigFilePath, 'r') as f:
                    js = json.load(f)
                    js_list = js[0]['item_name']
                    if not command[2] in js_list:
                        js_list.append(command[2])
                        js_new = []
                        temp = {}
                        temp['item_name'] = js_list
                        js_new.append(temp)
                        f.close()
                    else:
                        server.tell(info.player,'§7[§4扫地§r] §e' + command[2] + ' §c已存在于白名单')
                        f.close()
                        return
                with open(ConfigFilePath, 'w') as f:
                    f.write(json.dumps(js_new,ensure_ascii=False))
                    f.close
                server.tell(info.player,'§7[§2扫地§r] §e' + command[2] + ' §b已添加')
            else:
                server.tell(info.player,'§7[§4扫地§r] §e' + command[2] + ' §c非正确的MC物品ID')
        elif command [1] == 'remove' and len(command) == 3:
            with open(ConfigFilePath, 'r') as f:
                js = json.load(f)
                js_list = js[0]['item_name']
                if command[2] in js_list:
                    js_list.remove(command[2])
                    js_new = []
                    temp = {}
                    temp['item_name'] = js_list
                    js_new.append(temp)
                    f.close()
                else:
                    server.tell(info.player,'§7[§4扫地§r] §c未在白名单文件中找到 §e' + command[2])
                    f.close()
                    return
            with open(ConfigFilePath, 'w') as f:
                f.write(json.dumps(js_new,ensure_ascii=False))
                f.close
            server.tell(info.player,'§7[§2扫地§r/§bINFO§7] §e' + command[2] + ' §b已从白名单中删除')
        else:
            server.tell(info.player,'§7[§4扫地§r] §c参数错误，请输入 §7§l' + Prefix + ' help §r§c查看具体命令')
    else:
        server.tell(info.player,'§7[§4扫地§r] §c参数错误，请输入 §7§l' + Prefix + ' §r§c查看具体命令')

    #NBT格式写入
def get_nbt(name):
    return ',nbt=!{Item:{id:"minecraft:' + name + '"}}'

def kill(server):
    global tag # 全局Tag
    now = 15 # 倒计时
    server.say('[§2扫地§r] §2即将手动清理 §4警告：' + str(now) + 's后清理,输入!!clear取消')
    tag = True
    while tag: # 循环
        if tag == False: # 判断tag是否为 否 否则跳出
            break
        if now == 0: # 判断秒是否为 0 0则跳出
            break
        if now <= 5: # 判断是否小于等于 5
            server.say('[§2扫地§r] §2即将手动清理 §4警告：' + str(now) + 's后清理,输入!!clear取消')
        now -= 1 # 秒-1s
        time.sleep(1) # 等待 1s
    if tag == False: # 判断tag 否则继续
        tag == True
        server.say('[§2扫地§r] §4操作取消')
    else:
        kill_item(server) # 清理掉落物

    #清理物品
def kill_item(server):
    global item_counter
    cmd = 'kill @e[type=item'
    with open(ConfigFilePath, 'r') as f:
        js = json.load(f)
        lines = js[0]['item_name']
        
        for i in range(len(lines)):
            name = lines[i].replace('\n', '').replace('\r', '')
            cmd = cmd + get_nbt(name)
    cmd = cmd + ']'
    server.execute(cmd)
    item_counter = True
