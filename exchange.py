#! /usr/bin/env /mnt/nfs/local/python2.5/bin/python
# -*- coding: utf-8 -*-

import socket
import select,time
import struct,os,sys
import threading
from models import schedules,cards,parks,records
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2
import config
from utilities import poslog

FLAGS = '\x7e'
ISOTIMEFORMATS = '%Y-%m-%d %X'
bs = None

base = [str(x) for x in range(10)] + [ chr(x) for x in range(ord('A'),ord('A')+6)]
# 十进制 to 二进制: bin() 
def dec2bin(string_num):
    num = int(string_num)
    mid = []
    while True:
        if num == 0: break
        num,rem = divmod(num, 2)
        mid.append(base[rem])

    return ''.join([str(x) for x in mid[::-1]])

def format_str(str,m):   
    rets = ''
    for i in range(0, m):
        tmp = '0x' + str[i*2:i*2+2]
        sub = hex(eval(tmp))
        rets = rets + chr(int(sub,16)) 

    return rets   

###checking code
def str_crc(str):
    crc = ord(str[0])
    for i in range( 1,len(str) ):
        crc = crc  ^  ord(str[i])
    
    return chr(crc)

def str_escape(str):
    tmp = str.replace('\x7d','\x7d\x01')
    str_new = tmp.replace('\x7e','\x7d\x02')
    
    return str_new

def str_rescape(str):
    tmp = str.replace('\x7d\x02','\x7e')
    str_new = tmp.replace('\x7d\x01','\x7d')
    
    return str_new

def charge_select(cond):

    vpr_plate= cond['vpr_plate'] 
    stime= cond['stime'] 
    etime= cond['etime'] 






def indata(element):
    query_access = records.get_id(element.s_access_id)
    for element_access in query_access:
        hexid = '%08X'%int(element_access.id)
        record_id = format_str(hexid,4) 

        plate = ''
        if element_access.in_vpr_plate:
            plate = element_access.in_vpr_plate.encode("gbk")
            schedules.delete_binding(element_access.in_vpr_plate)
        plate = plate + '\x00'

        name = ''
        vtype = '\x00'
        try:
            if element_access.card_info_id != 0:
                card_row = list(cards.query(element_access['card_info_id']))
                name = card_row[0].name.encode("gbk")
                vtype = chr(card_row[0].card_type)
        except :
            print "search card_info failed"
        name = name + '\x00'

        if element_access.in_time:
            stime = element_access.in_time.strftime(ISOTIMEFORMATS)
        else:
            stime = '0000-00-00 00:00:00'
        hextime = stime[2:4] + stime[5:7] + stime[8:10] + stime[11:13] + stime[14:16]+stime[17:19]
        in_time = format_str(hextime,6)

        status = '\x01'
        if element_access.status == 'in':
            status = '\x01'

        picpath = ''
        if element_access.in_picture:
            picpath = element_access.in_picture

        msg_sub = record_id + plate + name + vtype + in_time + status
        datastore = dict(msg = msg_sub,
                         pic = picpath
                        )
    return datastore 

def outdata(element):
    query_access = records.get_id(element.s_access_id)
    for element_access in query_access:
        #1 id
        hexid = '%08X'%int(element_access.id)
        record_id = format_str(hexid,4)

        picpath = ''
        if element_access.out_picture:
            picpath = element_access.out_picture

        #2.vpr_plate
        plate = ''
        if element_access.out_vpr_plate:
            plate = element_access.out_vpr_plate.encode("gbk")
        plate = plate + '\x00'
        #3.name,4.vtype
        name = ''
        vtype = '\x00'
        try :
            if element_access.card_info_id != 0:
                card_row = list(cards.query(element_access['card_info_id']))
                name = card_row[0].name.encode("gbk")
                vtype = chr(card_row[0].card_type)
        except :
            print "search card_info failed"
        name = name + '\x00'
        #5.in_time
        if element_access.in_time:  
            stime = element_access.in_time.strftime(ISOTIMEFORMATS)
        else:
            stime = '0000-00-00 00:00:00'

        hextime = stime[2:4] + stime[5:7] + stime[8:10] + stime[11:13] + stime[14:16] + stime[17:19] 
        in_time = format_str(hextime,6)

        #6.out_time
        if element_access.out_time: 
            etime = element_access.out_time.strftime(ISOTIMEFORMATS)
        else:
            etime = '0000-00-00 00:00:00'

        hextime = etime[2:4] + etime[5:7] + etime[8:10] + etime[11:13] + etime[14:16]+etime[17:19] 
        out_time = format_str(hextime,6)
        #7.shopping_time
        hex_tmp = "%08X"%int(element_access.stopping_time*3600)
        stopping_time = format_str(hex_tmp,4)
        #8.charge
        hex_tmp = "%08X"%int(element_access.charge*100)
        charge = format_str(hex_tmp,4)
        #hex_tmp = "%08X"%int(element_access.actual*100)
        #actual = format_str(hex_tmp,4) 


        #9.item
        #item = '\x01'
        pay_row = list(payrecord.get_itemtotal(element_access.id))
        item= chr(pay_row[0].itemtotal)


        pay_data=[]
        query_charge = payrecord.get_payrow(element_access.id)
        for element_payrecords in query_charge:
            pay_mode = element_payrecords.pay_mode
            mode = chr(pay_mode)
       
            toll_collector = element_payrecords.toll_collector + '\x00'

            hex_tmp = "%08X"%int(element_payrecord.charge*100)
            charge = format_str(hex_tmp,4)
 
            serial = ''
            if pay_mode == 6:
                #e_coupon_row = list(e_coupon.get_licenceno(element_access.out_vpr_plate))
                #serial = e_coupon_row[0].serial_no
                serial = element_payrecords.serial_no
            serial=serial + '\x00'

            ptime = element_payrecords.pay_time.strftime(ISOTIMEFORMATS)
            hextime = ptime[2:4] + ptime[5:7] + ptime[8:10] + ptime[11:13] + ptime[14:16]+ptime[17:19] 
            pay_time = format_str(hextime,6)

            pay_data.append(dict(paytype = mode,
                                 serialno = serial, 
                                 collector = toll_collector,
                                 money = charge,
                                 time = pay_time
                            ))

        '''
        #9.1
        charge_method = '\x01'      

        if element_access.pay_mode:
            charge_method = chr(int(element_access.pay_mode))

        #9.2
        charge_serial = ''
        if element_access.pay_serial_no:
            charge_serial = element_access.pay_serial_no.encode("gbk")

        charge_serial = charge_serial + '\x00'
   
        #9.3
        toll_collector = ''
        if element_access.toll_collector:
            toll_collector = element_access.toll_collector.encode("gbk")

        toll_collector = toll_collector + '\x00'
        #9.4 actual
        charge_actual = actual
        #9.5 paytime 
        charge_time = out_time
        '''

        #msg_sub = record_id + plate + name + vtype + in_time + out_time + stopping_time + charge + actual + item+ \
        #            charge_method + charge_serial + charge_actual + charge_time + toll_collector
        msg_sub = record_id + plate + name + vtype + in_time + out_time + stopping_time + charge + actual + item+ \
                   pay_data 
        datastore = dict(msg = msg_sub,
                         pic = picpath
                        )
    return datastore 


def message_composite(msg_sub,message_id,msg_serial):
    msg_len = len(msg_sub)
    if msg_len < 1024:
        bin_len = dec2bin(str(msg_len))
        bin_len = '%010d'%int(bin_len)
        msg_pro = '00'+'0'+'000' + bin_len
        msg_pro = '%04x'%int(msg_pro,2)
        msg_pro = format_str(msg_pro,2)

        msg_head = message_id + msg_pro + config.ARMID + msg_serial

    tmp = msg_head + msg_sub + str_crc(msg_head + msg_sub)
    message=FLAGS + str_escape(tmp) + FLAGS
    return message

def update_schedule_img(element,state,picpath):
    str_path = ''
    n = picpath.find('img/')
    if n  > -1 :
        str_path = "/sddisk/pic/" + picpath[n+4 : len(picpath)]
        print str_path
        if not os.path.exists(str_path):
            print 'file' + str_path +' not exist'
            schedules.update_flags(element.id,'s_img_flags', 2)
        else:
            if state == 'in' : # In
                pic_file = "InImage"
                in_out = "1"    
            elif state == 'out':
                pic_file = "OutImage"
                in_out = "2"        
            # 在 urllib2 上注册 http 流处理句柄                      
            register_openers()          
            # upload pic 5 times    
            #loop = 0
            #for loop in range(5):      
            try :
                datagen, headers = multipart_encode({"InImage": open(str_path, "rb")})
                urlstr = config.WEBURL + "%s"%element.s_access_id + "/" + in_out
                print urlstr            
                request = urllib2.Request(urlstr, datagen, headers)
                ret = urllib2.urlopen(request).read()
                if ret != '1' :
                    print 'http return error :',ret
                    #schedules.update_flags(element.id,'s_img_flags', 6)
                else :
                    if element.id > 0 and element.id < 65501 :
                        try :
                            schedules.update_flags(element.id,'s_img_flags', 1)
                        except Exception, e :
                            log_exchange = poslog.Logger('log_exchange','/sddisk/log/exchange.log')
                            log_exchange.log('update img_flags error '+str(element.id)+str(e))
                            config.database_recon()
                            time.sleep(1)
                    print "update img flags"
                    #break

            except Exception, e:
                log_exchange = poslog.Logger('log_exchange','/sddisk/log/exchange.log')
                log_exchange.log('multipart_encode error '+str(element.id)+str(e))
                time.sleep(1)
                print str(e)

    else : # revise pic path
        schedules.update_flags(element.id,'s_img_flags', 2)
        print "error pic path"

def update_schedule(id):
    schedules.update_flags(id,'s_img_flags', 5)    
    schedules.update_flags(id,'s_flags', 5)

class SendThread(threading.Thread):
    def run(self): 
        global bs  
        socket.setdefaulttimeout(8)
        stat = False
        print "Send thread is running ..."
        try:
            bs = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            bs.connect( (config.SERVERIP,config.SERVERPORT) )
            stat = True
        except Exception, e:
            print str(e) ,"application is trying......"
            stat = False
            
        while True:
            try: 
                if not stat :  # re connect		        
                    stime = time.strftime(ISOTIMEFORMATS, time.localtime())
                    print "start time=",stime
		    bs = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    bs.connect((config.SERVERIP,config.SERVERPORT) )                    
                    stat = True
                    stime = time.strftime(ISOTIMEFORMATS, time.localtime())
                    print "connect success time=",stime
                else: 
                    time.sleep(15)
		    try :
                        query = schedules.get()
		    except :
			print "--------------reconnct database-------------"
                        config.database_recon()

	            for element in query:                         
		        try :
                            msg_id = element.s_message_id 
                            db_arm_id = element.s_arm_id
                            msg_sub = ''

                            if db_arm_id != config.STR_ARMID :
                                continue

                            if msg_id.lower() == 'in' : # In
                                messageID_UP = '\x01\x01'
                                state = 'in'
                                msg_pic_store = indata(element) 
                                msg_sub = msg_pic_store['msg'] 
                                pic = msg_pic_store['pic'] 
                            elif msg_id.lower() == 'out' : 
                                messageID_UP = '\x01\x02'
                                state = 'out'
                                msg_pic_store = outdata(element)
                                msg_sub = msg_pic_store['msg'] 
                                pic = msg_pic_store['pic'] 


                            if msg_sub != '' : # select access_records success                    
                                hexid = '%04x'%int(element.id)
                                msg_serial = format_str(hexid,2)

                                message = message_composite(msg_sub,messageID_UP,msg_serial)

                                if element.s_flags == 0:
                                    s_print = ''
                                    for i in range(0,len(message)):
                                         tmp = '%02X '%ord(message[i])
                                         s_print = s_print + tmp
                                    print "Send %d"%len(message) + ': ' + s_print
                                    try :
                                        bs.send(message)
                                    except :
                                        print "send data error"
                                        stat = False
                                        break
                                update_schedule_img(element,state,pic)
                            else : # select access_records failed
                                update_schedule(element.id)

                            query = schedules.delete(65500) 
                            time.sleep(2) 
		        except Exception , e:
	                    print str(e)
		            continue
            except Exception, e:
                print str(e) +" retry after 30 seconds "# DEBUG
                stime = time.strftime(ISOTIMEFORMATS, time.localtime())
                print "connect failed  time=",stime
                time.sleep(30)
                continue


# no field name        type     comment
# 1  record_id         WORD     equals terminal message serial number
# 2  responseID        WORD     equals terminal message ID
# 3  result            BYTE     0:success 1:failure 2:message error 3:don't support
#
#8001
#eg:7E 80 01 00 05 12 34 56 78 90 12 34 00 65 (00 64) (01 00) (00) 3A 7E
def response_common(recv):
    #---- test crc--------
    #tmp = recv[1:19]
    tmp = recv[1:len(recv) - 2]
    crcresult = recv[19]
    responseresult = recv[18]
    tmpid = '%02X'%ord(recv[14]) + '%02X'%ord(recv[15])
    record_id = int(tmpid,16) 

    s_print = ''      
    for i in range(0,len(tmp)):
        tmps = '%02X '%ord(tmp[i])
        s_print = s_print + tmps
    print "pre crc %d"%len(tmp) + ': ' + s_print 

    if responseresult == '\x00': # server response success
        if record_id > 0 and record_id < 65501 : 
            try :	
                schedules.update_flags(record_id,'s_flags',1)
            except Exception, e :    
                log_exchange = poslog.Logger('log_exchange','/sddisk/log/exchange.log')
                log_exchange.log('update flags error '+str(record_id)+str(e))
                config.database_recon()
                time.sleep(3)

# no field name        type     comment
# 1  vpr_plate         STRING    
# 2  order_no          STRING    
# 3  serial_no         STRING    
# 4  money             DWORD
# 5  paytime           BCD[6]
#
#8200
def response_payonline(recv):# pre_payment data
    print "response_payment start  "
    pos_start = 14
    vpr_plate = ''

    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
            pos_start = i + 1
            break
        vpr_plate = vpr_plate + recv[i]
    vpr_plate = unicode(vpr_plate,'gbk')
  
    order_no = ''
    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
              pos_start = i+1
              break
        order_no = order_no + recv[i]

    serial_no = ''
    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
            pos_start = i + 1
            break
        serial_no = serial_no + recv[i]

    tmp = "%02X"%ord(recv[pos_start]) + '%02X'%ord(recv[pos_start+1]) + '%02X'%ord(recv[pos_start+2]) + '%02X'%ord(recv[pos_start+3])
    money = int(tmp,16) / 100.0  

    pos_start = pos_start + 4
    paytime = "20%02X"%ord(recv[pos_start]) + '-%02X'%ord(recv[pos_start+1]) + '-%02X'%ord(recv[pos_start+2])+ \
               ' %02X'%ord(recv[pos_start+3]) + ':%02X'%ord(recv[pos_start+4]) + ':%02X'%ord(recv[pos_start+5])
    print "insert pre_payment data, send reply message "

    accessdata_row = list(records.get_vprplate_in(vpr_plate))
    records_id = accessdata[0].id
    pay_data = dict(
                    records_id=accessdata_row[0].id,
                    toll_collector=auth.session.email,#......
                    pay_time =paytime,
                    pay_mode = 4,
                    coupon_type = -1,
                    coupon_value = 0,
                    charge = money,
                    calc_in_time = paytime, #......
                    calc_out_time = paytime,#......
                    charge_device_id=order_no #......
                    serial_no = serial_no
                    )


    #if schedules.insert_prepayment(order_no,vpr_plate,serial_no,money,paytime) == 1 : # insert success
    if payrecord.insert(pay_data) == 1 : # insert success
        rtn = 0
    else :
        rtn = -1
    return rtn


# no field name        type     comment
# 1  vpr_plate         STRING
# 2  holder_id         DWORD
# 3  card_no           STRING
# 4  binding_time      BCD[6]
#8201
def response_bindcard(recv):# bind card
    print "response_bindcard start  "
    pos_start = 14
    vpr_plate = ''

    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
            pos_start = i + 1
            break
        vpr_plate = vpr_plate + recv[i]  
                      
    vpr_plate = unicode(vpr_plate,'gbk')

    tmp = "%02X"%ord(recv[pos_start]) + '%02X'%ord(recv[pos_start+1]) + '%02X'%ord(recv[pos_start+2])+'%02X'%ord(recv[pos_start+3])
    holder_id = int(tmp,16)
    pos_start = pos_start + 4

                      
    card_no = ''
    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
            pos_start = i + 1
            break
        card_no =card_no + recv[i]

    binding_time = "20%02X"%ord(recv[pos_start]) + '-%02X'%ord(recv[pos_start+1]) + '-%02X'%ord(recv[pos_start+2])+ \
                 ' %02X'%ord(recv[pos_start+3]) + ':%02X'%ord(recv[pos_start+4]) + ':%02X'%ord(recv[pos_start+5])
    print "binding card data, send reply message ",vpr_plate.encode('utf8')

    if schedules.insert_binding(vpr_plate,holder_id,card_no,binding_time) >= 0 : # insert success
        rtn = 0
    else :
        rtn = -1 

    return rtn 

# no field name        type     comment
# 1  vpr_plate         STRING
# 2  holder_id         DWORD
# 3  card_no           STRING
# 4  binding_time      BCD[6]
#8202
def response_unbindcard(recv):#unbind card 

    print "response_unbindcard start  "
    pos_start = 14
    vpr_plate = ''
    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
            pos_start = i + 1
            break
        vpr_plate = vpr_plate + recv[i]                        
    vpr_plate = unicode(vpr_plate,'gbk')
  
    tmp = "%02X"%ord(recv[pos_start]) + '%02X'%ord(recv[pos_start+1]) + '%02X'%ord(recv[pos_start+2]) + '%02X'%ord(recv[pos_start+3])
    holder_id = int(tmp,16)
    pos_start = pos_start + 4

                      
    card_no = ''
    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
            pos_start = i + 1
            break
        card_no = card_no + recv[i]

    binding_time = "20%02X"%ord(recv[pos_start]) + '-%02X'%ord(recv[pos_start+1]) + '-%02X'%ord(recv[pos_start+2])+ \
                 ' %02X'%ord(recv[pos_start+3]) + ':%02X'%ord(recv[pos_start+4]) + ':%02X'%ord(recv[pos_start+5])

    print "unbinding card data, send reply message ",vpr_plate.encode('utf8')
    if schedules.delete_binding(vpr_plate) == 1 : # delete success
        rtn = 0
    else :
        rtn = -1 

    return rtn 

# no field name        type     comment
# 1  vpr_plate         STRING
# 2  stime             BCD[6] 
# 3  etime             BCD[6]
#8205
def response_charge(recv):#charge
    print "response_charge start  "
    #vpr_plate
    pos_start = 14
    base_info = recv[pos_start:len(recv)-2]
    vpr_plate = ''
    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
            pos_start = i + 1
            break
        vpr_plate = vpr_plate + recv[i]                        
    vpr_plate = unicode(vpr_plate,'gbk')

    stime = "20%02X"%ord(recv[pos_start]) + '-%02X'%ord(recv[pos_start+1]) + '-%02X'%ord(recv[pos_start+2])+ \
                 ' %02X'%ord(recv[pos_start+3]) + ':%02X'%ord(recv[pos_start+4]) + ':%02X'%ord(recv[pos_start+5])

    pos_start = pos_start + 6
    etime = "20%02X"%ord(recv[pos_start]) + '-%02X'%ord(recv[pos_start+1]) + '-%02X'%ord(recv[pos_start+2])+ \
                ' %02X'%ord(recv[pos_start+3]) + ':%02X'%ord(recv[pos_start+4]) + ':%02X'%ord(recv[pos_start+5])

    charge_condition= dict(vpr_plate= vpr_plate,
                           stime= stime,
                           etime= etime
                          )
    #add select model

    query = list(records.get_vprplate_out(vpr_plate,stime,etime))
    access_id = query[0].id
    hex_tmp = "%08X"%int(query[0].charge*100)
    receivable= format_str(hex_tmp,4)

    payrecord_query = list(payrecord.get_chargesum(access_id,0,stime,etime))
    hextmp = '%08X'%int(payrecord_query[0].actualcharge*100)
    paid = format_str(hextmp,4) 

    base_and_charge= base_info+paid+receivable 
  
    hex_tmp= "%04X"%int(access_id)
    serialno = format_str(hex_tmp,2)

    condition = dict(charge_info = base_and_charge
                     serialno = serialno 
                    )
    return condition 

# no field name        type     comment
# 1  name              STRING 
# 2  card_no           STRING 
# 3  card_type         BYTE
# 4  start_time        BCD[6]
# 5  end_time          BCD[6]
# 6  coupon_serialno   STRING
# 7  telephone         STRING
# 8  room_no           STRING
# 9  email             STRING
# 10 free_value        WORD 
# 11 operator          STRING
# 12 vpr_plate         STRING
#8207
def response_addcardinfo(recv):#add card info
    print "response_addcardinfo start  "
    card_type_d = {65:u'固定车',66:u'按次数优惠',67:u'按分钟优惠',68:u'减免金额'}
    #name
    pos_start = 14
    name = ''
    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
            pos_start = i + 1
            break
        name = name + recv[i]                        
    name = unicode(name,'gbk')

    #card_no
    card_no = ''
    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
            pos_start = i + 1
            break
        card_no = card_no+recv[i]
                    
    #card_type
    card_type = recv[pos_start]
    #mem
    mem = card_type_d[ord(card_type)]

    #start_time
    pos_start = pos_start + 1
    start_time = "20%02X"%ord(recv[pos_start]) + '-%02X'%ord(recv[pos_start+1]) + '-%02X'%ord(recv[pos_start+2])+ \
                ' %02X'%ord(recv[pos_start+3]) + ':%02X'%ord(recv[pos_start+4]) + ':%02X'%ord(recv[pos_start+5])
    #end_time
    pos_start = pos_start + 6
    end_time = "20%02X"%ord(recv[pos_start]) + '-%02X'%ord(recv[pos_start+1]) + '-%02X'%ord(recv[pos_start+2])+ \
                ' %02X'%ord(recv[pos_start+3]) + ':%02X'%ord(recv[pos_start+4]) + ':%02X'%ord(recv[pos_start+5])
    #coupon_serialno
    pos_start = pos_start + 6
    coupon_serialno= ''
    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
            pos_start = i + 1
            break
        coupon_serialno= coupon_serialno+ recv[i]

    #telephone
    model = ''
    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
            pos_start = i + 1
            break
        model = model + recv[i]                        
                        
    #room_no
    room_no = ''
    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
            pos_start = i + 1
            break
        room_no = room_no + recv[i]                        
    room_no = unicode(room_no,'gbk')

    #email
    email = ''
    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
            pos_start = i + 1
            break
        email = email + recv[i]

    #free_value
    tmp = "%02X"%ord(recv[pos_start]) + '%02X'%ord(recv[pos_start + 1])
    free_value = int(tmp,16)

    #regist_operator
    pos_start = pos_start + 2
    regist_operator = ''
    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
            pos_start = i + 1
            break
        regist_operator = regist_operator + recv[i]
    regist_operator = unicode(regist_operator,'gbk')

    #licence_no
    licence_no = ''
    for i in range(pos_start, len(recv)):
        if recv[i] == '\x00' :
            pos_start = i + 1
            break
        licence_no = licence_no + recv[i]
    licence_no = unicode(licence_no,'gbk')

    print "reply message of Vehicle access "

    if ord(card_type) == 65:#固定车
        card_info = dict(card_no = card_no,
                     name = name,
                     user_no = card_no,
                     card_type = card_type,
                     licence_no = licence_no,
                     free_times = 0,#update by lxz 0410
                     model = model,
                     room_no = room_no,
                     access_region = 0,
                     start_time = start_time,
                     end_time = end_time,                        
                     loss = 0,
                     regist_operator = regist_operator,
                     regist_time = time.strftime(ISOTIMEFORMATS, time.localtime()),
                     access_time = time.strftime(ISOTIMEFORMATS, time.localtime()),
                     charge_rule_id = '',#update by lxz 0410
                     email = email
                     ) 
    else:
        card_info = dict(licence_no= licence_no,
                     etype= card_type,
                     start_time = start_time,
                     end_time = end_time,                        
                     serial_no = coupon_serialno,
                     value = free_value
                     mem = mem
                     )
    if cards.insert(card_info)  : 
        rtn = 0
    else :
        rtn = -1 

    return rtn 

# no field name        type     comment
# 1  vpr_plate         STRING 
#8208
def response_deletecardinfo(recv):#delete card info
    pos_start = 14  
    vpr_plate = ''  
    for i in range(pos_start, len(recv)) :
        if recv[i] == '\x00' :
            pos_start = i+1 
            break           
        vpr_plate = vpr_plate + recv[i]
    vpr_plate = unicode(vpr_plate,'gbk')


    print "reply message ",vpr_plate.encode('utf8')
    if cards.delete_plate(vpr_plate) == 1 : # delete success
        rtn = 0
    else :
        rtn = -1 

    return rtn 

#0205
def charge_up(info,msg_serial):
    messageID_UP = '\x02\x05'
    message = message_composite(info,messageID_UP,msg_serial)
    return message
#0001
def arm_common_response(rtn,Platform_serial,Platform_msg_id):
    tmp = '\x00\x01\x00\x05' + config.ARMID + '\xff\xfe' + Platform_serial + Platform_msg_id
    if rtn == 0 : # insert or update table success
        tmp = tmp + '\x00'
    else :
        tmp = tmp + '\x01'
    tmp = tmp + str_crc(tmp)
    message = FLAGS + str_escape(tmp) + FLAGS
    return message

class RecvThread(threading.Thread) :
    def run(self) :            
        print "Recv thread is running ..."       
        start_byte = '' 
        while True :
            try :
                global bs
                rs,ws,es = select.select([bs,],[],[],2)
                if not(rs or ws or es):
                    time.sleep(1)
                    continue 

                # Receive each byte , and judge
		if start_byte == FLAGS :
	            recv_not_escape = FLAGS
		else :
		    recv_not_escape = bs.recv(1)

		if recv_not_escape == FLAGS :
		    start_byte = bs.recv(1)
		    if start_byte != FLAGS :
			recv_not_escape = recv_not_escape + start_byte
			while True :
			    tmp = bs.recv(1)
			    recv_not_escape = recv_not_escape +tmp
			    if tmp == FLAGS :
				break

                if len(recv_not_escape) < 3 :
		    continue

                #restore 0x7e in message
                recv = str_rescape(recv_not_escape)
                    
                #print recv
		s_print = ''
                for i in range(0 , len(recv)):
                    tmp = '%02X '%ord(recv[i])
                    s_print = s_print+tmp
                print "Recv %d"%len(recv) + ': ' + s_print 
               
                messageID = recv[1:3]
                armID = recv[5:12]
                messageSerial = recv[12:14]

                #check armid 
		if armID != config.ARMID :
                    print "Incorrect ARMID"
		    continue

                #check crc
                tmp = recv[1:len(recv)-2]
                if str_crc(tmp) != recv[len(recv)-2] :
		    print "Incorrect CRC byte"
		    continue


                if messageID == '\x80\x01' : # server response ID
                    print "----- receive 8001 command-----"
                    response_common(recv)
                elif messageID == '\x82\x00': # pre_payment data
                    print "----- receive 8200 command-----"
                    result = response_payonline(recv)
                    bs.sendall(arm_common_response(result,messageID,messageSerial))
                elif messageID == '\x82\x01': # binding cards
                    print "----- receive 8201 command-----"
                    result = response_bindcard(recv)
                    bs.sendall(arm_common_response(result,messageID,messageSerial))
                elif messageID == '\x82\x02': # unbinding cards
                    print "----- receive 8202 command-----"
                    result = response_unbindcard(recv)
                    bs.sendall(arm_common_response(result,messageID,messageSerial))
                elif messageID == '\x82\x05': # payment
                    print "----- receive 8205 command-----"
                    car_charge_info  = response_charge(recv)
                    bs.sendall(arm_common_response(result,messageID,messageSerial))
                    bs.sendall(charge_up(car_charge_info['charge_info'],car_charge_info['serialno']))
                elif messageID == '\x82\x06': # restart system
                    print "----- receive restart command-----"
                    result = response_restart(recv)
                    bs.sendall(arm_common_response(result,messageID,messageSerial))
                    os.system('reboot')
                elif messageID == '\x82\x07': # Vehicle access
                    print "----- receive data of Vehicle access-----"
                    result = response_addcardinfo(recv)
                    bs.sendall(arm_common_response(result,messageID,messageSerial))
                elif messageID == '\x82\x08': # delete Vehicle
                    print "----- receive data of delete Vehicle-----"
                    result = response_deletecardinfo(recv)
                    bs.sendall(arm_common_response(result,messageID,messageSerial))
                else :
                    print "no normal data"

            except Exception, e:
                #print str(e)
                continue 

# no field name        type 
# 1  emptystall        WORD
# 2  time              BCD[6]
#
#eg:7E 01 00 00 08 12 34 56 78 90 12 34 00 64 (00 58) (12 02 08 14 02 18) 9D 7E
def emptystall_up():
    # park_empty serail no= FFFF                     
    park_row = list(parks.get('id','1'))                        
    n=park_row[0].empty
    print "empty is ",n
    hexempty="%04X"%int(n)
    empty=format_str(hexempty,2)
                
    #BCD[6]
    stime = time.strftime(ISOTIMEFORMATS, time.localtime())
    hextime=stime[2:4]+stime[5:7]+stime[8:10]+stime[11:13]+stime[14:16]+stime[17:19]
    cur_time=format_str(hextime,6)
               
    #message
    tmp='\x01\x00\x00\x08'+config.ARMID+'\xff\xff'+empty+cur_time
    tmp=tmp+str_crc(tmp)
    message=FLAGS+str_escape(tmp)+FLAGS                
    return message
                    
class BeatThread(threading.Thread):
    def run(self): 
        global bs     
        '''
        while True:
            try:   
                # HeartBeat    
		tmp='\x00\x02\x00\x00'+ARMID+'\x00\x00'
                tmp=tmp+str_crc(tmp)
                message=FLAGS+str_escape(tmp)+FLAGS                
                bs.sendall(message) 
                time.sleep(0.5) 
            except Exception, e:
                time.sleep(120) 
                continue 
        '''
        while True:
            try:   
                bs.sendall(emptystall_up())
                time.sleep(120)                      
            except Exception, e:
                time.sleep(120) 
                continue 

  

if __name__ == "__main__":
    
    th_exchange = RecvThread()
    th_exchange.start()
    th_exchange = SendThread()
    th_exchange.start()
    th_exchange = BeatThread()
    th_exchange.start()
    

