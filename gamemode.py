# -*- coding: utf-8 -*-

import re
import time
import os

gm_user = 0
logfile = './plugins/gm/'


def on_info(server, info):
  global gm_user
  global user
  dimension_convert = {"0":"overworld","-1":"the_nether","1":"the_end"}
  if (info.is_player == 0):
    if("following entity data" in info.content):
      if gm_user>0:
        gm_user-=1
        name = info.content.split(" ")[0]
        if user == name:
          server.tell(name, '§6已获取到数据，正在更改模式!')
          dimension = re.search("(?<=Dimension: )-?\d",info.content).group()
          position_str = re.search("(?<=Pos: )\[.*?\]",info.content).group()
          position = re.findall("\[(-?\d*).*?, (-?\d*).*?, (-?\d*).*?\]",position_str)[0]
          #os.system('cd plugins/gm && echo "'+str(position[0])+'|'+str(position[1])+'|'+str(position[2])+'|'+dimension_convert[dimension]+'" > ' + name)
          f = open('./plugins/gm/' + name, 'w')
          f.write(str(position[0])+'|'+str(position[1])+'|'+str(position[2])+'|'+dimension_convert[dimension])
          f.close()
          server.execute("gamemode spectator " + name)
          user = ''
          server.tell(name, '§6已切换到观察者模式,要切换回来请!!gm')
  else:
    per = server.get_permission_level(info)
    if info.content.startswith('!!gm') and info.is_player == 1:
      if per >= 0:
        gm = info.content.split(" ")
        if os.path.exists('./plugins/gm/' + info.player):
          server.tell(info.player, '§65秒后改变模式,请不要走动!')
          time.sleep(5)
          server.tell(info.player, '§6正在更改模式，请不要走动!')
          server.tell(info.player, '§6更改时间由服务器tps决定!')
          f = open('plugins/gm/' + info.player, 'r')
          zub = f.read()
          zub = zub.replace('\n', '').replace('\r', '')
          f.close()
          os.remove('plugins/gm/' + info.player)
          xyz = zub.split("|")
          server.execute("execute at " + info.player + " in minecraft:" + xyz[3] + " run tp " + info.player + " " + xyz[0] + " " + str(int(xyz[1]) + 0.5) + " " + xyz[2])
          server.execute("gamemode survival " + info.player)
        else:
          server.tell(info.player, '§65秒后改变模式,请不要走动!')
          time.sleep(5)
          server.tell(info.player, '§6正在更改模式，请不要走动!')
          server.tell(info.player, '§6更改时间由服务器tps决定!')
          gm_user+=1
          os.system('cd plugins/gm && echo " " > ' + info.player)
          user = info.player
          server.execute("data get entity "+info.player)
      else:
        server.tell(info.player, '你没有权限')

def on_load(server, old):
    server.add_help_message('!!gm', '切换玩家模式')
