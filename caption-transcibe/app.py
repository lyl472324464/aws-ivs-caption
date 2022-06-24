import pymysql
from fastapi import FastAPI
import nacos
import json
import os
from pydantic import BaseModel

from dbutils.pooled_db import PooledDB

try:
    SERVER_ADDRESSES = os.environ["SERVER_ADDRESSES"]
    NAMESPACE = os.environ["NAMESPACE"]
    GROUP = os.environ["GROUP"]   
    COMMON_CONFIG_DATA_ID = os.environ["COMMON_CONFIG_DATA_ID"]
    SPECIAL_CONFIG_DATA_ID = os.environ["SPECIAL_CONFIG_DATA_ID"]
    # serviceName = os.environ["SERVICE_NAME"]
    # serviceAddress = os.environ["SERVICE_ADDRESS"]
    # servicePort = int(os.environ["SERVICE_PORT"])


    def connect_nacos(server_addresses, namespace):
        client = nacos.NacosClient(server_addresses, namespace=namespace)
        return client


    def get_config(client, data_id, group):
        init_config = client.get_config(data_id, group)
        return init_config


    def add_instance(client):
        instance = client.add_naming_instance("test", "127.0.0.1", 8000)
        return instance


    client = connect_nacos(SERVER_ADDRESSES, NAMESPACE)

    common_config = json.loads(get_config(client, COMMON_CONFIG_DATA_ID, GROUP))
    special_config = json.loads(get_config(client, SPECIAL_CONFIG_DATA_ID, GROUP))
    config = {**common_config, **special_config}
    print("get nacos config success")
except Exception as e:
    print(str(e))
    config = {
        "max_captions_num": 10,
        "rds_mysql8_master":{
            "host": "mysql8-dev.cqzfv6bqgafe.us-east-1.rds.amazonaws.com",
            "user": "admin",
            "password": "C52VmXQaSgTS9n",
            "database": "mysql"
        },
        "transcribe_language_code": {
            "support_languages_code": ["uk-UA", "zh-CN", "en-AU", "en-GB", "en-US", "fr-FR", "fr-CA", "de-DE", "it-IT", "ja-JP", "ko-KR", "pt-BR", "es-US"],
            "support_languages": ["乌克兰语", "简体中文", "英语-澳大利亚", "英语-英国", "英语-美国", "法语", "法语加拿大", "德语", "意大利语", "日语", "韩语", "葡萄牙语巴西", "西班牙语美国"]
        },
        "translate_language_code": {
            "support_languages_code": ["af","sq","am","ar","hy","az","bn","bs","bg","ca","zh","zh-TW","hr","cs","da","fa-AF","nl","en","et","fa","tl","fi","fr","fr-CA","ka","de","el","gu","ht","ha","he","hi","hu","is","id","ga","it","ja","kn","kk","ko","lv","lt","mk","ms","ml","mt","mr","mn","no","ps","pl","pt","pt-PT","pa","ro","ru","sr","si","sk","sl","so","es","es-MX","sw","sv","ta","te","th","tr","uk","ur","uz","vi","cy"],
            "support_languages": ["南非荷兰语","阿尔巴尼亚语","阿姆哈拉语","阿拉伯语","亚美尼亚","阿塞拜疆语","孟加拉语","波斯尼亚语","保加利亚语","加泰罗尼亚语","简体中文","繁体中文","克罗地亚语","捷克语","丹麦语","达里语","荷兰语","英语","爱沙尼亚语","波斯语","菲律宾","芬兰语","法语","法语（加拿大）","格鲁吉亚语","德语","希腊语","古吉拉特","海地克里奥尔","豪萨语","希伯来语","印地语","匈牙利语","冰岛语","印度尼西亚语","意大利语","日语","卡纳达","哈萨克斯坦","韩语","拉脱维亚语","立陶宛","马其顿","马来语","马拉雅拉姆","马耳他语","蒙古","挪威语","普什图语","波兰语","葡萄牙语","罗马尼亚语","俄语","塞尔维亚语","僧伽罗语","斯洛伐克语","斯洛文尼亚语","索马里语","西班牙语","西班牙语（墨西哥）","斯瓦希里语","瑞典语","泰米尔语","泰卢固语","泰语","土耳其语","乌克兰语","乌尔都语","乌兹别克","越南语","威尔士语"]
        },
        "rtmp_endpoint": "rtmp://ae7c845164a8f438b92595fb6b6c57d9-5882cd9520cbbdb4.elb.us-east-1.amazonaws.com:1935/app/",
        "rtmps_endpoint": "rtmps://caption-stream-dev.ai-ai.biz:443/app/",
        "AWS_ACCESS_KEY_ID": "AKIARSUGQLPKQBW63HTR",
        "AWS_SECRET_ACCESS_KEY": "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",
        "AWS_REGION": "us-east-1",
        "AGORA_APP_ID": "a6b8be92d6024d1db5963db74210c711",
        "AGORA_APP_CERT": "25d44b1d0684411da024fb41750ab4c2"
    }

description = """
## 字幕服务共三个api，增删查，最多同时%s个字幕直播间

## 每次开播调用create_caption,关播调用delete_caption
## transcribe_language_code可以为"zh-CN", "en-AU", "en-GB", "en-US", "fr-FR", "fr-CA", "de-DE", "it-IT", "ja-JP", "ko-KR", "pt-BR", "es-US"
## source_translate_language_code，target_translate_language_codes可以为"af","sq","am","ar","hy","az","bn","bs","bg","ca","zh","zh-TW","hr","cs","da","fa-AF","nl","en","et","fa","tl","fi","fr","fr-CA","ka","de","el","gu","ht","ha","he","hi","hu","is","id","ga","it","ja","kn","kk","ko","lv","lt","mk","ms","ml","mt","mr","mn","no","ps","pl","pt","pt-PT","pa","ro","ru","sr","si","sk","sl","so","es","es-MX","sw","sv","ta","te","th","tr","uk","ur","uz","vi","cy"
## target_translate_language_codes可以多选,用:分割
## 返回值

{\n
    "code": int,
    "msg": str,
    "data": str
}\n
**code为0是失败，code为1是成功**
""" % (config["max_captions_num"])

tags_metadata = [
    {
        "name": "create",
        "description": "为一个用户创建一个字幕服务。1、transcribe_language_code为直播语言，只能添一个。2、source_translate_language_code为翻译源语言，因为语言代码和transcribe_language_code不一样，所以再添一次，比如汉语：transcribe_language_code为zh-CN,source_translate_language_code为zh。3、target_translate_language_codes为翻译目标语言，可多选，用:分割，比如： zh:en代表翻译成中文和英文",
    },
    {
        "name": "delete",
        "description": "为一个用户删除一个字幕服务",
    },
    {
        "name": "get_all",
        "description": "获取所有字幕服务",
    }
]

mysql_connection_pool = PooledDB(
    creator=pymysql,  # 使用链接数据库的模块
    maxconnections=100,  # 连接池允许的最大连接数，0和None表示不限制连接数
    mincached=100,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
    maxcached=100,  # 链接池中最多闲置的链接，0和None不限制
    maxshared=100,  # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，
    # 所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
    blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
    maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
    host=config['rds_mysql8_master']['host'],
    user=config['rds_mysql8_master']['user'],
    password=config['rds_mysql8_master']['password'],
    database=config['rds_mysql8_master']['database'],
    charset='utf8'
)

app = FastAPI(
    title="字幕服务",
    description=description,
    version="0.0.1",
    openapi_tags=tags_metadata)

@app.on_event("startup")
async def startup_event():
    # 没有caption表则创建
    db = mysql_connection_pool.connection()
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS ai_data.`caption`  (
                    `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                    `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    `push_key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                    `rtmp_push_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                    `rtmps_push_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                    `rtm_channel` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                    `transcribe_language_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                    `source_translate_language_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                    `target_translate_language_codes` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                    `deleted` int NULL DEFAULT 0
                    ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;""")
    
    # 镜像启动，重新开启所有supervisor服务
    directory = os.path.join(os.getcwd(), 'transcribe-server')
    remove_all_config_file = os.popen("rm -rf /etc/supervisor/conf.d/*.conf")
    for l in remove_all_config_file.readlines():
        print(l)
    cursor.execute("SELECT push_key, rtmp_push_url, rtm_channel, transcribe_language_code, source_translate_language_code, target_translate_language_codes FROM ai_data.`caption` WHERE deleted=0")
    captions = cursor.fetchall()
    for c in captions:
        all_language_codes_list = []
        all_true_language_codes_list = []
        transcribe_language_code = config["transcribe_language_code"]["unite_languages_code"][config["transcribe_language_code"]["support_languages_code"].index(c[3])]
        source_translate_language_code = config["translate_language_code"]["unite_languages_code"][config["translate_language_code"]["support_languages_code"].index(c[4])]
        all_language_codes_list.append(transcribe_language_code)
        all_true_language_codes_list.append(c[3])
        all_language_codes_list.append(source_translate_language_code)
        all_true_language_codes_list.append(c[4])
        true_target_translate_language_codes_list = c[5].split(":")
        for true_tlc in true_target_translate_language_codes_list:
            all_true_language_codes_list.append(true_tlc)
            tlc = config["translate_language_code"]["unite_languages_code"][config["translate_language_code"]["support_languages_code"].index(true_tlc)]
            all_language_codes_list.append(tlc)
        all_language_codes = ":".join(all_language_codes_list)
        all_true_language_codes = ":".join(all_true_language_codes_list)
        with open("/etc/supervisor/conf.d/%s.conf" % str(c[0]), 'w') as f:
            f.write("[program:%s]\n" % str(c[0]))
            f.write("command=sh run.sh\ndirectory=%s\nautostart=true\nstartsecs=1\nautorestart=true\nuser=root\n" % directory)
            f.write("""environment=RTMP_INPUT=%s,
                    AWS_REGION=%s,
                    GOOGLE_APPLICATION_CREDENTIALS=/caption/google-key.json,
                    TRANSLATE_ENABLED=true,
                    TRANSLATE_WEB_SOCKET_URL=test,
                    RTM_CHANNEL=%s,
                    TRANSCRIBE_LANGUAGE_CODE=%s,
                    SOURCE_TRANSLATE_LANGUAGE_CODE=%s,
                    TARGET_TRANSLATE_LANGUAGE_CODES=%s,
                    ALL_LANGUAGE_CODES=%s,
                    ALL_TRUE_LANGUAGE_CODES=%s,
                    AGORA_APP_ID=%s,
                    AGORA_APP_CERT=%s""" % (c[1], config["AWS_REGION"], c[2], c[3], c[4], c[5], all_language_codes, all_true_language_codes, config["AGORA_APP_ID"], config["AGORA_APP_CERT"]))
    supervisorctl_update = os.popen("supervisorctl update")
    for l in supervisorctl_update.readlines():
        print(l)
    cursor.close()
    db.close()

# @app.on_event("shutdown")
# def shutdown_event():
#     db.close()

class ResponseModel(BaseModel):
    code: int
    msg: str
    data: str

@app.post("/create_caption", response_model=ResponseModel, tags=["create"])
async def create_caption(push_key: str, transcribe_language_code: str, source_translate_language_code: str, target_translate_language_codes: str, rtm_channel: str):
    db = mysql_connection_pool.connection()
    cursor = db.cursor()
    cursor.execute("SELECT rtmp_push_url, rtmps_push_url FROM ai_data.caption where push_key = \'%s\' AND deleted = 0" % (push_key))
    caption_info = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM ai_data.caption where deleted = 0")
    caption_nums = cursor.fetchone()[0]
    target_translate_language_codes_list = target_translate_language_codes.split(":")
    try:
        target_translate_language_codes_list.remove(source_translate_language_code)
        target_translate_language_codes = ":".join(target_translate_language_codes_list)
    except:
        pass
    target_translate_language_codes_ifok = True
    for tlc in target_translate_language_codes_list:
        if tlc not in config["translate_language_code"]["unite_languages_code"]:
            target_translate_language_codes_ifok = False
            break
    try:
        if not caption_info == None:
            response = {
                "code": 0,
                "msg": "该直播间已创建字幕",
                "data": json.dumps({
                    "rtmp_push_url": caption_info[0],
                    "rtmps_push_url": caption_info[1],
                })
            }
        elif int(caption_nums) >= int(config["max_captions_num"]):
            response = {
                "code": 0,
                "msg": "最多为%s个直播间创建字幕服务" % (config["max_captions_num"]),
                "data": ""
            }
        elif transcribe_language_code not in config["transcribe_language_code"]["unite_languages_code"]:
            response = {
                "code": 0,
                "msg": "language_code不支持",
                "data": "只支持如下语言： %s, 语言代码为： %s" % (json.dumps(config["transcribe_language_code"]["support_languages"], ensure_ascii=False), json.dumps(config["transcribe_language_code"]["support_languages_code"], ensure_ascii=False))
            }
        elif source_translate_language_code not in config["translate_language_code"]["unite_languages_code"]:
            response = {
                "code": 0,
                "msg": "source_translate_language_code不支持",
                "data": "只支持如下语言： %s, 语言代码为： %s" % (json.dumps(config["translate_language_code"]["support_languages"], ensure_ascii=False), json.dumps(config["translate_language_code"]["support_languages_code"], ensure_ascii=False))
            }
        elif not target_translate_language_codes_ifok:
            response = {
                "code": 0,
                "msg": "target_translate_language_codes不支持",
                "data": "只支持如下语言： %s, 语言代码为： %s" % (json.dumps(config["translate_language_code"]["support_languages"], ensure_ascii=False), json.dumps(config["translate_language_code"]["support_languages_code"], ensure_ascii=False))
            }
        else:
            if os.path.exists("/etc/supervisor/conf.d/%s.conf" % str(push_key)):
                response = {
                    "code": 0,
                    "msg": "该直播间已开启字幕服务",
                    "data": ""
                }
            else:
                all_language_codes_list = []
                all_true_language_codes_list = []
                true_transcribe_language_code = config["transcribe_language_code"]["support_languages_code"][config["transcribe_language_code"]["unite_languages_code"].index(transcribe_language_code)]
                true_source_translate_language_code = config["translate_language_code"]["support_languages_code"][config["translate_language_code"]["unite_languages_code"].index(source_translate_language_code)]
                all_language_codes_list.append(transcribe_language_code)
                all_true_language_codes_list.append(true_transcribe_language_code)
                all_language_codes_list.append(source_translate_language_code)
                all_true_language_codes_list.append(true_source_translate_language_code)
                true_target_translate_language_codes_list = []
                for tlc in target_translate_language_codes_list:
                    all_language_codes_list.append(tlc)
                    true_tlc = config["translate_language_code"]["support_languages_code"][config["translate_language_code"]["unite_languages_code"].index(tlc)]
                    true_target_translate_language_codes_list.append(true_tlc)
                    all_true_language_codes_list.append(true_tlc)
                true_target_translate_language_codes = ":".join(true_target_translate_language_codes_list)
                all_language_codes = ":".join(all_language_codes_list)
                all_true_language_codes = ":".join(all_true_language_codes_list)
                # 创建supervisor服务
                directory = os.path.join(os.getcwd(), 'transcribe-server')
                with open("/etc/supervisor/conf.d/%s.conf" % str(push_key), 'w') as f:
                    f.write("[program:%s]\n" % str(push_key))
                    f.write("command=sh run.sh\ndirectory=%s\nautostart=true\nstartsecs=1\nautorestart=true\nuser=root\n" % directory)
                    f.write("""environment=RTMP_INPUT=%s%s,
                            AWS_REGION=%s,
                            GOOGLE_APPLICATION_CREDENTIALS=/caption/google-key.json,
                            TRANSLATE_ENABLED=true,
                            TRANSLATE_WEB_SOCKET_URL=test,
                            RTM_CHANNEL=%s,
                            TRANSCRIBE_LANGUAGE_CODE=%s,
                            SOURCE_TRANSLATE_LANGUAGE_CODE=%s,
                            TARGET_TRANSLATE_LANGUAGE_CODES=%s,
                            ALL_LANGUAGE_CODES=%s,
                            ALL_TRUE_LANGUAGE_CODES=%s,
                            AGORA_APP_ID=%s,
                            AGORA_APP_CERT=%s""" % (config["rtmp_endpoint"], push_key, config["AWS_REGION"], rtm_channel, true_transcribe_language_code, true_source_translate_language_code, true_target_translate_language_codes,  all_language_codes, all_true_language_codes, config["AGORA_APP_ID"], config["AGORA_APP_CERT"]))
                supervisorctl_update = os.popen("supervisorctl update")
                for l in supervisorctl_update.readlines():
                    print(l)
                
                cursor.execute("SELECT * FROM ai_data.caption where push_key = \'%s\' AND deleted = 1" % (push_key))
                if_same_key_exists = cursor.fetchone()
                if not if_same_key_exists == None:
                    sql = """UPDATE ai_data.`caption` SET 
                    rtmp_push_url=\'%s\', rtmps_push_url=\'%s\', rtm_channel=\'%s\', transcribe_language_code=\'%s\', source_translate_language_code=\'%s\', target_translate_language_codes=\'%s\', deleted=0 
                    WHERE push_key=\'%s\'""" % (config["rtmp_endpoint"] + push_key, config["rtmps_endpoint"] + push_key, rtm_channel, true_transcribe_language_code, true_source_translate_language_code, true_target_translate_language_codes, push_key) 
                # insert to mysql
                else:
                    sql = """INSERT INTO ai_data.`caption`(
                        push_key, rtmp_push_url, rtmps_push_url, rtm_channel, transcribe_language_code, source_translate_language_code, target_translate_language_codes, deleted)
                        VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', 0)""" % (push_key, config["rtmp_endpoint"] + push_key, config["rtmps_endpoint"] + push_key, rtm_channel, true_transcribe_language_code, true_source_translate_language_code, true_target_translate_language_codes)
                # 提交到数据库执行
                try:
                    cursor.execute(sql)
                    db.commit()
                except Exception as e:
                    # 如果发生错误则回滚
                    db.rollback()
                    cursor.close()
                    db.close()
                    response = {
                        "code": 0,
                        "msg": str(e),
                        "data": ""
                    }
                    return response
                response = {
                    "code": 1,
                    "msg": "成功开启字幕服务",
                    "data": json.dumps({
                        "rtmp_push_url": config["rtmp_endpoint"] + push_key,
                        "rtmps_push_url": config["rtmps_endpoint"] + push_key,
                    })
                }
    except Exception as e:
        sql = "UPDATE ai_data.`caption` SET deleted=1 WHERE push_key = \'%s\'" % (push_key)
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            # 如果发生错误则回滚
            db.rollback()
            cursor.close()
            db.close()
            response = {
                "code": 0,
                "msg": str(e),
                "data": ""
            }
            return response
        conf_file = "/etc/supervisor/conf.d/%s.conf" % str(push_key)
        if os.path.exists(conf_file):
            os.remove(conf_file)
            supervisorctl_update = os.popen("supervisorctl update")
            for l in supervisorctl_update.readlines():
                print(l)
        response = {
            "code": 0,
            "msg": str(e),
            "data": ""
        }
    cursor.close()
    db.close()
    return response
    

@app.delete("/delete_caption", response_model=ResponseModel, tags=["delete"])
async def delete_caption(push_key: str):
    # 删除数据库
    db = mysql_connection_pool.connection()
    cursor = db.cursor()
    sql = "UPDATE ai_data.`caption` SET deleted=1 WHERE push_key = \'%s\'" % (push_key)
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        # 如果发生错误则回滚
        db.rollback()
        cursor.close()
        db.close()
        response = {
            "code": 0,
            "msg": str(e),
            "data": ""
        }
        return response
    cursor.close()
    db.close()

    # 关闭supervisor
    try:
        os.remove("/etc/supervisor/conf.d/%s.conf" % str(push_key))
        supervisorctl_update = os.popen("supervisorctl update")
        for l in supervisorctl_update.readlines():
            print(l)
        response = {
                    "code": 1,
                    "msg": "成功关闭服务",
                    "data": ""
        }
        os.system("rm -rf /var/log/supervisor/%s*" % str(push_key))
        return response
    except Exception as e:
        response = {
                    "code": 0,
                    "msg": str(e),
                    "data": ""
                }
        return response


@app.get("/get_all_caption", response_model=ResponseModel, tags=["get_all"])
async def get_all_caption():
    try:
        db = mysql_connection_pool.connection()
        cursor = db.cursor()
        sql = "SELECT push_key FROM ai_data.`caption` WHERE deleted=0"
        cursor.execute(sql)
        captions = cursor.fetchall()    
        result = []
        for c in captions:
            result.append(c)   
        response = {
                    "code": 1,
                    "msg": "成功获取所有字幕服务",
                    "data": json.dumps(result)
                }
    except Exception as e:
        response = {
                    "code": 0,
                    "msg": str(e),
                    "data": ""
                }
    cursor.close()
    db.close()
    return response
