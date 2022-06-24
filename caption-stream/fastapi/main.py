from typing import Optional
import pymysql
from fastapi import FastAPI, HTTPException
import nacos
import json
import os
from pydantic import BaseModel
from dbutils.pooled_db import PooledDB
from loguru import logger

try:
    SERVER_ADDRESSES = os.environ["SERVER_ADDRESSES"]
    NAMESPACE = os.environ["NAMESPACE"]
    GROUP = os.environ["GROUP"] 
    COMMON_CONFIG_DATA_ID = os.environ["DATA_ID"]
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
    config = json.loads(get_config(client, COMMON_CONFIG_DATA_ID, GROUP))
    print("get nacos config success ")
    logger.info("get nacos config success ")
except Exception as e:
    print(str(e))
    logger.info("5675675675")

description = """
鉴别用户直播推流权限
{\n
    "code": int,
    "msg": str,
    "data": str
}\n
**code为0是失败，code为1是成功**
"""

tags_metadata = [
    {
        "name": "create",
        "description": "为一个用户创建一个字幕服务。1、transcribe_language_code为直播语言，只能添一个。2、source_translate_language_code为翻译源语言，因为语言代码和transcribe_language_code不一样，所以再添一次，比如汉语：transcribe_language_code为zh-CN,source_translate_language_code为zh。3、target_translate_language_codes为翻译目标语言，可多选，用:分割，比如： zh:en代表翻译成中文和英文",
    },
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
    title="鉴权服务",
    description=description,
    version="0.0.1",
    openapi_tags=tags_metadata)


class Auth(BaseModel):
    name: str
    sex: Optional[str] = None

@app.get("/publish")
def publish(name: str):
    db = mysql_connection_pool.connection()
    cursor = db.cursor()
    cursor.execute("SELECT push_key FROM ai_data.caption where push_key = \'%s\' and deleted = 0" % (name))
    caption_info = cursor.fetchone()
    logger.info("starting living")
    if caption_info == None:
        logger.info("The user has no permission！")    
        raise HTTPException(status_code=403, detail="The user has no permission！")
    return 

