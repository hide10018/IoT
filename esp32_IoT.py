import dht
import machine
import ntptime
import time
import prequests
import ufirebase as firebase



messageid = ["XXX","XXX","XXX","XXX","XXX","XXX","XXX","XXX","XXX","XXX","XXX","XXX",]
timestamp = ["XXX","XXX","XXX","XXX","XXX","XXX","XXX","XXX","XXX","XXX","XXX","XXX",]
sign = ["XXX","XXX","XXX","XXX","XXX","XXX","XXX","XXX","XXX","XXX","XXX","XXX",]

def plug2_onoff(onoff,channel,messageid, timestamp, sign):
    URL = "XXX"
    payload = '{\n\t\"payload\": {\n\t\t\"togglex\": {\n\t\t\t\"onoff\": %s,\n\t\t\t\"channel\": %s\n\t\t}\n\t},\n\t\"header\": {\n\t\t\"messageId\": \"%s",\n\t\t\"method\": \"SET\",\n\t\t\"from\": \"XXX\",\n\t\t\"namespace\": \"Appliance.Control.ToggleX\",\n\t\t\"timestamp\": %s,\n\t\t\"sign\": "%s",\n\t\t\"payloadVersion\": 1,\n\t\t\"triggerSrc\": \"iOSLocal\",\n\t\t\"uuid\": \"XXX\"\n\t}\n}' % (onoff, channel, messageid,timestamp,sign)
    headers = {'content-type': 'application/json'}
    prequests.request("POST", URL, data=payload, headers=headers)
    
def index_judge():
    global index
    if index == len(messageid)-1:
        index = 0
    else:
        index = index + 1

# 単位をμg/m^3に変換
def pcs2ugm3 (pcs):
    pi = 3.14159
    # 全粒子密度(1.65E12μg/ m3)
    density = 1.65 * pow (10, 12)
    # PM2.5粒子の半径(0.44μm)
    r25 = 0.44 * pow (10, -6)
    vol25 = (4/3) * pi * pow (r25, 3)
    mass25 = density * vol25 # μg
    K = 3531.5 # per m^3 
    # μg/m^3に変換して返す
    return pcs * K * mass25

# pm2.5計測
def pcs2ugm3 (pcs):
  pi = 3.14159
  # 全粒子密度(1.65E12μg/ m3)
  density = 1.65 * pow (10, 12)
  # PM2.5粒子の半径(0.44μm)
  r25 = 0.44 * pow (10, -6)
  vol25 = (4/3) * pi * pow (r25, 3)
  mass25 = density * vol25 # μg
  K = 3531.5 # per m^3 
  # μg/m^3に変換して返す
  return pcs * K * mass25

# pm2.5計測
def get_pm25(PIN):
    t0 = time.time()
    # print(t0)
    t = 0
    ts = 30 # サンプリング時間
    while (1):
        # LOW状態の時間tを求める
        dt = machine.time_pulse_us(PIN, 1)/(10**6)
        print(PIN.value())
        t = t + dt
        print(time.time() - t0)
        # print(t)
        # print(dust.value())
        # print(adc.read())
        
        if ((time.time() - t0) >= ts):
            # LOWの割合[0-100%]
            ratio = (t*10)/ts
            # print(t)
            # ほこりの濃度を算出
            concent = 1.1 * pow(ratio,3) - 3.8 * pow(ratio,2) + 520 * ratio + 0.62
            
            print(t, "[sec]")
            print(ratio, " [%]")
            print(concent, " [pcs/0.01cf]")
            print(pcs2ugm3(concent), " [ug/m^3]")
            print("-------------------")
            break
    return pcs2ugm3(concent)

rtc = machine.RTC()
ntptime.NTP_DELTA = ntptime.NTP_DELTA -32400
ntptime.settime()
print(rtc.datetime()[4])
hours = rtc.datetime()[4]
dust_data = 0
index = 0
# dust_loop = 0
# temp_loop = 0
# hours = 26

url = 'XXX'

sensor = dht.DHT11(machine.Pin(21))
green = machine.Pin(5,machine.Pin.OUT)

while True:


    if rtc.datetime()[5] == 57:
        PIN = 25
        # ピン番号をGPIOで指定
        dust = machine.Pin(PIN, machine.Pin.IN, machine.Pin.PULL_UP)
        # adc = machine.ADC(dust)
        dust_data = get_pm25(dust)
        print(dust_data)

        firebase.patch("Firebase path", {"tag1": dust_data})
        time.sleep(5)
        firebase.patch("Firebase path", {str(rtc.datetime()[4]): dust_data})
        

        # ピン設定解除
        dust.off()
        time.sleep(60)
    
    if  rtc.datetime()[4] == hours:
        print(hours)
        print(rtc.datetime())
        rtc = machine.RTC()
    else:
        sensor.measure()
        t = sensor.temperature()
        h = sensor.humidity()
        url += "temperature="
        url += str(t)
        url += "&"
        url += "humidity="
        url += str(h)
        url += "&"
        url += "dust="
        url += str(dust_data)
        print(url)
        
        req = prequests.get(url)#Writing on Spreadsheets
        req.close()
        print("success!")
        for i in range(3):
            green.on()
            time.sleep(1)
            green.off()
            time.sleep(1)
        url = 'XXX'
        
        firebase.patch("Firebase path", {"tag1": t})
        time.sleep(2)
        
        firebase.patch("Firebase path", {str(rtc.datetime()[4]): t})
        time.sleep(2)
        
        firebase.patch("Firebase path", {"tag1": h})
        time.sleep(2)
        
        firebase.patch("Firebase path", {str(rtc.datetime()[4]): h})
        time.sleep(2)
        
        firebase.patch("Firebase path", {"tag1": dust_data})
        time.sleep(2)
        
        firebase.patch("Firebase path", {str(rtc.datetime()[4]): dust_data})
        
        if dust_data >= 1.7:#if dust_data >= 1.7 turn on Air Cleaner
            plug2_onoff(1,4,messageid[index],timestamp[index],sign[index])
            index_judge()
        else:
            plug2_onoff(0,4, messageid[index], timestamp[index], sign[index])
            index_judge()
        
        if  t >= 28:#if temperature >= 28, turn on Fan.
            plug2_onoff(1,1,messageid[index],timestamp[index],sign[index])
            index_judge()
        else:
            plug2_onoff(0,1, messageid[index], timestamp[index], sign[index])
            index_judge()
            
        if  h <= 50:#if humidity <= 50, turn on humidifier.
            plug2_onoff(1,2,messageid[index],timestamp[index],sign[index])
            index_judge()
        else:
            plug2_onoff(0,2, messageid[index], timestamp[index], sign[index])
            index_judge()
        
        print(rtc.datetime()[4])
        hours = rtc.datetime()[4]
        print(url)
    time.sleep(5)