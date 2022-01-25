import json
import socket
import commands as co
import time
from cle import Cle
from config import Config
from tag import Tag


def process_config(msg, CLE, cfg):
    cle = get_current_cle(msg, CLE)
    if cle:
        CLE.remove(cle)
    cle = Cle(msg, cfg)
    CLE.append(cle)


def process_TX(msg, cle):
    for anchor in cle.anchors:
        if msg["receiver"] == anchor.master_ID:
            anchor.add_tx(msg)
            if anchor.data2sendflag:
                data2send = get_anchor_info(anchor)
                co.send_to_server(data2send, output)
                anchor.data2sendflag = 0


def process_RX(msg, cle):
    for anchor in cle.anchors:
        if msg["receiver"] == anchor.ID and msg["sender"] == anchor.master_ID:
            anchor.add_rx(msg)
            if anchor.data2sendflag:
                data2send = get_anchor_info(anchor)
                co.send_to_server(data2send, output)
                anchor.data2sendflag = 0
            break


def process_BLINK(msg, cle):

    for anchor in cle.anchors:
        if msg["receiver"] == anchor.ID:
            break

    if anchor.sync_flag:
        msg["anchor_number"] = anchor.number
        msg["corrected_timestamp"] = anchor.correct_timestamp(msg["timestamp"])
        match_flag = 0
        for tag in cle.tags:
            if msg["sender"] == tag.ID:
                match_flag = 1
                break

        if match_flag == 0:
            tag = Tag(msg, cle)
            print(f"New tag {tag.ID}")
            cle.tags.append(tag)
        tag.add_data(msg)
        if tag.data2sendflag:
            data2send = get_tag_info(tag)
            # print(data2send)
            co.send_to_server(data2send, output)
            tag.data2sendflag = 0

def get_current_cle(msg, CLE):
    cle = []
    for cle in CLE:
        if cle.company == msg["company"] and cle.room == msg["room"]:
            break
    return cle


def get_tag_info(tag):
    tag_info = {}
    tag_info["type"] = "tag"
    tag_info["ID"] = tag.ID
    tag_info["x"] = tag.x
    tag_info["y"] = tag.y
    tag_info["z"] = tag.h
    tag_info["dop"] = tag.DOP
    tag_info["lifetime"] = tag.lifetime
    tag_info["time"] = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(tag.lasttime))
    tag_info["anchors"] = tag.anchors_number_to_solve
    tag_info["company"] = tag.company
    tag_info["room"] = tag.room
    return tag_info

def get_anchor_info(anchor):
    anchor_info = {}
    anchor_info["type"] = "anchor"
    anchor_info["number"] = anchor.number
    anchor_info["ID"] = anchor.ID
    anchor_info["master_ID"] = anchor.master_ID
    anchor_info["role"] = anchor.Role
    anchor_info["x"] = anchor.x
    anchor_info["y"] = anchor.y
    anchor_info["z"] = anchor.z
    anchor_info["sync_flag"] = anchor.sync_flag
    anchor_info["company"] = anchor.company
    anchor_info["room"] = anchor.room
    return anchor_info



if __name__ == "__main__":

    with open("ipconfig.json", "r") as file:
        ipconfig = (json.loads(file.read()))

    cfg = Config()
    CLE = []

    input = socket.socket()
    input.connect((ipconfig["IP"], ipconfig["PORT1"]))

    output = socket.socket()
    output.connect((ipconfig["IP"], ipconfig["PORT2"]))

    while True:
        data = co.receive_from_server(input)
        if data["type"] == "room_config":
            process_config(data, CLE, cfg)
        elif data["type"] == "CS_TX":
            cle = get_current_cle(data, CLE)
            if cle:
                process_TX(data, cle)
        elif data["type"] == "CS_RX":
            cle = get_current_cle(data, CLE)
            if cle:
                process_RX(data, cle)
        elif data["type"] == "BLINK":
            cle = get_current_cle(data, CLE)
            if cle:
                process_BLINK(data, cle)

