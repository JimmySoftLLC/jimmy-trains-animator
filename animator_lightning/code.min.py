BW='right_held'
BV='Choose sounds menu'
BU='Select a program option'
BT='left_held'
BS='/sd/mvc/animations_are_now_active.wav'
BR='/sd/mvc/create_sound_track_files.wav'
BQ='/sd/mvc/local.wav'
BP='/sd/mvc/dot.wav'
BO='animator-lightning'
BN='Utility: '
BM='timestamp_mode_off'
BL='/sd/mvc/timestamp_mode_on.wav'
BK='timestamp_mode_on'
BJ='/sd/mvc/continuous_mode_deactivated.wav'
BI='/sd/mvc/continuous_mode_activated.wav'
BH='wav/no_card.wav'
BG=Exception
Aw='Set Web Options'
Av='web_options'
Au='light_string_setup_menu'
At='choose_my_sounds'
As='choose_sounds'
Ar='right'
Aq='left'
Ap='/sd/mvc/option_selected.wav'
Ao='volume_pot_on'
An='volume_pot_off'
Am='/sd/mvc/timestamp_mode_off.wav'
Al='/sd/mvc/timestamp_instructions.wav'
Ak='utf8'
Aj='config wifi imports'
Ai='main_menu'
Ah='serve_webpage'
Ag='random my'
Af='random built in'
Ae='random all'
Ad=enumerate
AG='/sd/customers_owned_music/'
AF='text'
AE='end'
AD='start'
AC='volume_settings'
A8='flashTime'
A7='add_sounds_animate'
A1='action'
A0='volume_pot'
z='/sd/lightning_sounds/'
y='customers_owned_music_'
s='.json'
o='option_selected'
n='HOST_NAME'
m=str
l=property
i='/sd/mvc/'
h='volume'
g=''
d='rb'
c=open
Y='/sd/mvc/all_changes_complete.wav'
X=range
V='base_state'
R='/sd/config_lightning.json'
Q='light_string'
P=len
O='.wav'
N=print
J=True
G=False
import gc,files as E
def U(collection_point):gc.collect();A=gc.mem_free();E.log_item('Point '+collection_point+' Available memory: {} bytes'.format(A))
U('Imports gc, files')
import time as L,audiocore as Z,audiomixer as BX,audiobusio as BY,sdcardio as Ax,storage as A9,busio,digitalio as p,board as W,neopixel as Ay,random as F,rtc,microcontroller as AH
from analogio import AnalogIn as BZ
from rainbowio import colorwheel as Az
from adafruit_debouncer import Debouncer as A_
def B0():AH.on_next_reset(AH.RunMode.NORMAL);AH.reset()
U('imports')
Ba=BZ(W.A0)
def Bb(pin,wait_for):
	B=wait_for/10;A=0
	for C in X(10):L.sleep(B);A+=1;A=A/10
	return pin.value/65536
A2=p.DigitalInOut(W.GP28)
A2.direction=p.Direction.OUTPUT
A2.value=G
Bc=W.GP6
Bd=W.GP7
AI=p.DigitalInOut(Bc)
AI.direction=p.Direction.INPUT
AI.pull=p.Pull.UP
H=A_(AI)
AJ=p.DigitalInOut(Bd)
AJ.direction=p.Direction.INPUT
AJ.pull=p.Pull.UP
K=A_(AJ)
Be=W.GP18
Bf=W.GP19
Bg=W.GP20
Bh=BY.I2SOut(bit_clock=Be,word_select=Bf,data=Bg)
A2.value=J
Bi=W.GP2
Bj=W.GP3
Bk=W.GP4
B1=W.GP5
B2=busio.SPI(Bi,Bj,Bk)
Bl=2
A=BX.Mixer(voice_count=Bl,sample_rate=22050,channel_count=2,bits_per_sample=16,samples_signed=J,buffer_size=4096)
Bh.play(A)
B3=.2
A.voice[0].level=B3
A.voice[1].level=B3
try:AK=Ax.SDCard(B2,B1);AL=A9.VfsFat(AK);A9.mount(AL,'/sd')
except:
	A3=Z.WaveFile(c(BH,d));A.voice[0].play(A3,loop=G)
	while A.voice[0].playing:0
	B4=G
	while not B4:
		H.update()
		if H.fell:
			try:
				AK=Ax.SDCard(B2,B1);AL=A9.VfsFat(AK);A9.mount(AL,'/sd');B4=J;A3=Z.WaveFile(c('/sd/mvc/micro_sd_card_success.wav',d));A.voice[0].play(A3,loop=G)
				while A.voice[0].playing:0
			except:
				A3=Z.WaveFile(c(BH,d));A.voice[0].play(A3,loop=G)
				while A.voice[0].playing:0
A2.value=G
Bm=rtc.RTC()
Bm.datetime=L.struct_time((2019,5,29,15,14,15,0,-1,-1))
B=E.read_json_file(R)
j=E.return_directory(g,'/sd/lightning_sounds',O)
Bn=[Ae,Af,Ag]
j.extend(Bn)
q=E.return_directory(y,'/sd/customers_owned_music',O)
A4=[]
A4.extend(q)
A4.extend(j)
Bo=E.return_directory(g,'/sd/time_stamp_defaults',s)
AA=B[Ah]
Bp=E.read_json_file('/sd/mvc/main_menu.json')
AM=Bp[Ai]
Bq=E.read_json_file('/sd/mvc/web_menu.json')
AN=Bq['web_menu']
Br=E.read_json_file('/sd/mvc/light_string_menu.json')
AO=Br['light_string_menu']
Bs=E.read_json_file('/sd/mvc/light_options.json')
t=Bs['light_options']
Bt=E.read_json_file('/sd/mvc/volume_settings.json')
AP=Bt[AC]
Bu=E.read_json_file('/sd/mvc/add_sounds_animate.json')
AQ=Bu[A7]
U('config setup')
r=G
a=G
u=[]
v=[]
AR=[]
AS=[]
AT=[]
AU=[]
M=0
D=Ay.NeoPixel(W.GP10,M)
def B5(part):
	B=[]
	for D in u:
		for A in D:C=A;break
		if part==AD:
			for A in X(0,5):B.append(A+C)
		if part==AE:
			for A in X(5,10):B.append(A+C)
	return B
def B6(part):
	B=[]
	for D in v:
		for A in D:C=A;break
		if part==AD:
			for A in X(0,2):B.append(A+C)
		if part==AE:
			for A in X(2,4):B.append(A+C)
	return B
def Bv():
	global AR,AS,AT,AU;AR=B5(AD);AS=B5(AE);AT=B6(AD);AU=B6(AE)
	for B in u:
		for A in B:D[A]=50,50,50
		D.show();L.sleep(.3);D.fill((0,0,0));D.show()
	for C in v:
		for A in C:D[A]=50,50,50
		D.show();L.sleep(.3);D.fill((0,0,0));D.show()
def A5():
	global u,v,M,D,M;u=[];v=[];M=0;F=B[Q].split(',')
	for H in F:
		C=H.split('-')
		if P(C)==2:
			E,A=C;A=int(A)
			if E=='bar':I=list(X(M,M+A));u.append(I);M+=A
			elif E=='bolt':J=list(X(M,M+A));v.append(J);M+=A
	N('Number of pixels total: ',M);D.deinit();U('Deinit ledStrip');D=Ay.NeoPixel(W.GP10,M);D.auto_write=G;D.brightness=1.;Bv()
A5()
U('Neopixels setup')
if AA:
	import socketpool as Bw,mdns;U(Aj);import wifi as w;U(Aj);from adafruit_httpserver import Server,Request,FileResponse as AV,Response as b,POST as e;U(Aj);E.log_item('Connecting to WiFi');B7='jimmytrainsguest';B8=g
	try:B9=E.read_json_file('/sd/env.json');B7=B9['WIFI_SSID'];B8=B9['WIFI_PASSWORD'];U('wifi env');N('Using env ssid and password')
	except:N('Using default ssid and password')
	try:
		w.radio.connect(B7,B8);U('wifi connect');AW=mdns.Server(w.radio);AW.hostname=B[n];AW.advertise_service(service_type='_http',protocol='_tcp',port=80);Bx=[hex(A)for A in w.radio.mac_address];E.log_item('My MAC addr:'+m(Bx));By=m(w.radio.ipv4_address);E.log_item('My IP address is'+By);E.log_item('Connected to WiFi');Bz=Bw.SocketPool(w.radio);S=Server(Bz,'/static',debug=J);U('wifi server')
		@S.route('/')
		def BA(request):U('Home page.');return AV(request,'index.html','/')
		@S.route('/mui.min.css')
		def BA(request):return AV(request,'mui.min.css','/')
		@S.route('/mui.min.js')
		def BA(request):return AV(request,'mui.min.js','/')
		@S.route('/animation',[e])
		def k(request):
			F=request;global B,r,a;A=F.raw_request.decode(Ak)
			if'cont_mode_on'in A:r=J;C(BI)
			elif'cont_mode_off'in A:r=G;C(BJ)
			elif BK in A:a=J;C(BL);C(Al)
			elif BM in A:a=G;C(Am)
			elif'reset_animation_timing_to_defaults'in A:
				for H in Bo:I=E.read_json_file('/sd/time_stamp_defaults/'+H+s);E.write_json_file(z+H+s,I)
			elif y in A:
				for D in q:
					if D in A:B[o]=D;Aa(B[o]);break
			else:
				for D in j:
					if D in A:B[o]=D;Aa(B[o]);break
			E.write_json_file(R,B);return b(F,'Animation '+B[o]+' started.')
		@S.route('/utilities',[e])
		def k(request):
			I='reset_to_defaults';H='speaker_test';F=request;global B;A=g;D=F.raw_request.decode(Ak)
			if H in D:A=H;C('/sd/mvc/left_speaker_right_speaker.wav')
			elif An in D:A=An;B[A0]=G;E.write_json_file(R,B);C(Y)
			elif Ao in D:A=Ao;B[A0]=J;E.write_json_file(R,B);C(Y)
			elif I in D:A=I;B_();E.write_json_file(R,B);C(Y);f.go_to_state(V)
			return b(F,BN+A)
		@S.route('/lights',[e])
		def k(request):
			O='set_to_100';N='set_to_80';M='set_to_60';L='set_to_40';K='set_to_20';J='set_to_0';I='set_to_white';H='set_to_blue';G='set_to_green';F='set_to_red';E=request;global B;A=g;C=E.raw_request.decode(Ak)
			if F in C:A=F;D.fill((255,0,0));D.show()
			elif G in C:A=G;D.fill((0,255,0));D.show()
			elif H in C:A=H;D.fill((0,0,255));D.show()
			elif I in C:A=I;D.fill((255,255,255));D.show()
			elif J in C:A=J;D.brightness=.0;D.show()
			elif K in C:A=K;D.brightness=.2;D.show()
			elif L in C:A=L;D.brightness=.4;D.show()
			elif M in C:A=M;D.brightness=.6;D.show()
			elif N in C:A=N;D.brightness=.8;D.show()
			elif O in C:A=O;D.brightness=1.;D.show()
			return b(E,BN+A)
		@S.route('/update-host-name',[e])
		def k(request):A=request;global B;C=A.json();B[n]=C[AF];E.write_json_file(R,B);AW.hostname=B[n];BF();return b(A,B[n])
		@S.route('/get-host-name',[e])
		def k(request):return b(request,B[n])
		@S.route('/update-volume',[e])
		def k(request):A=request;global B;C=A.json();AZ(C[A1]);return b(A,B[h])
		@S.route('/get-volume',[e])
		def k(request):return b(request,B[h])
		@S.route('/update-light-string',[e])
		def k(request):
			G=' data: ';F='action: ';D=request;global B;A=D.json()
			if A[A1]=='save'or A[A1]=='clear'or A[A1]=='defaults':B[Q]=A[AF];N(F+A[A1]+G+B[Q]);E.write_json_file(R,B);A5();C(Y);return b(D,B[Q])
			if B[Q]==g:B[Q]=A[AF]
			else:B[Q]=B[Q]+','+A[AF]
			N(F+A[A1]+G+B[Q]);E.write_json_file(R,B);A5();C(Y);return b(D,B[Q])
		@S.route('/get-light-string',[e])
		def k(request):return b(request,B[Q])
		@S.route('/get-customers-sound-tracks',[e])
		def k(request):A=E.json_stringify(q);return b(request,A)
		@S.route('/get-built-in-sound-tracks',[e])
		def k(request):A=[];A.extend(j);A.remove(Ae);A.remove(Af);A.remove(Ag);B=E.json_stringify(A);return b(request,B)
	except BG as AX:AA=G;E.log_item(AX)
U('web server')
import utilities as AY
U('utilities')
def T(seconds):
	D=seconds
	if B[A0]:C=Bb(Ba,D);A.voice[0].level=C
	else:
		try:C=int(B[h])/100
		except:C=.5
		if C<0 or C>1:C=.5
		A.voice[0].level=C;A.voice[1].level=C;L.sleep(D)
def BB():global B;B[Q]='bar-10,bolt-4,bar-10,bolt-4,bar-10,bolt-4'
def B_():global B;B[A0]=J;B[n]=BO;B[o]='thunder_birds_rain';B[h]='30';BB()
def AZ(action):
	D=action;A=int(B[h])
	if h in D:F=D.split(h);A=int(F[1])
	if D=='lower1':A-=1
	elif D=='raise1':A+=1
	elif D=='lower':
		if A<=10:A-=1
		else:A-=10
	elif D=='raise':
		if A<10:A+=1
		else:A+=10
	if A>100:A=100
	if A<1:A=1
	B[h]=m(A);B[A0]=G;E.write_json_file(R,B);C('/sd/mvc/volume.wav');AB(B[h],G)
def C(file_name):
	if A.voice[0].playing:
		A.voice[0].stop()
		while A.voice[0].playing:T(.02)
	B=Z.WaveFile(c(file_name,d));A.voice[0].play(B,loop=G)
	while A.voice[0].playing:C0()
def CO():
	A.voice[0].stop()
	while A.voice[0].playing:0
def C0():
	T(.02);H.update()
	if H.fell:A.voice[0].stop()
def AB(str_to_speak,addLocal):
	for A in str_to_speak:
		if A==' ':A='space'
		if A=='-':A='dash'
		if A=='.':A='dot'
		C(i+A+O)
	if addLocal:C(BP);C(BQ)
def C1():C('/sd/mvc/sound_selection_menu.wav');x()
def C2():C('/sd/mvc/choose_my_sounds_menu.wav');x()
def x():C('/sd/mvc/press_left_button_right_button.wav')
def C3():C('/sd/mvc/main_menu.wav');x()
def C4():C('/sd/mvc/add_sounds_animate.wav');x()
def A6():C('/sd/mvc/web_menu.wav');x()
def C5():C('/sd/mvc/volume_settings_menu.wav');x()
def C6():C('/sd/mvc/light_string_setup_menu.wav');x()
def C7():C('/sd/mvc/string_instructions.wav')
def BC():C(Ap)
def BD(song_number):C('/sd/mvc/song.wav');AB(song_number,G)
def BE(play_intro):
	if play_intro:C('/sd/mvc/current_light_settings_are.wav')
	A=B[Q].split(',')
	for(D,E)in Ad(A):C('/sd/mvc/position.wav');C(i+m(D+1)+O);C('/sd/mvc/is.wav');C(i+E+O)
def C8():
	C('/sd/mvc/no_user_soundtrack_found.wav')
	while J:
		H.update();K.update()
		if H.fell:break
		if K.fell:C(BR);break
def BF():
	C('/sd/mvc/animator_available_on_network.wav');C('/sd/mvc/to_access_type.wav')
	if B[n]==BO:C('/sd/mvc/animator_dash_lightning.wav');C(BP);C(BQ)
	else:AB(B[n],J)
	C('/sd/mvc/in_your_browser.wav')
def Aa(file_name):
	G='Sound file: ';E='Random sound file: ';C=file_name;N(C);A=C
	if C==Af:D=P(j)-4;B=F.randint(0,D);A=j[B];N(E+j[B]);N(G+A)
	elif C==Ag:D=P(q)-1;B=F.randint(0,D);A=q[B];N(E+q[B]);N(G+A)
	elif C==Ae:D=P(A4)-4;B=F.randint(0,D);A=A4[B];N(E+A4[B]);N(G+A)
	if a:C9(A)
	elif y in A:Ab(A)
	elif A=='alien lightshow':Ab(A)
	elif A=='inspiring cinematic ambient lightshow':Ab(A)
	else:CA(A)
def Ab(file_name):
	I=file_name;global a;S=1;U=3;V=y in I
	if V:
		I=I.replace(y,g)
		try:W=E.read_json_file(AG+I+s)
		except:
			C('/sd/mvc/no_timestamp_file_found.wav')
			while J:
				H.update();K.update()
				if H.fell:a=G;return
				if K.fell:a=J;C(Al);return
	else:W=E.read_json_file(z+I+s)
	Q=W[A8];e=P(Q);B=0
	if V:X=Z.WaveFile(c(AG+I+O,d))
	else:X=Z.WaveFile(c(z+I+O,d))
	A.voice[0].play(X,loop=G);f=L.monotonic();M=0
	while J:
		Y=0;b=L.monotonic()-f
		if B<P(Q)-2:R=Q[B+1]-Q[B]-.25
		else:R=.25
		if R<0:R=0
		if b>Q[B]-.25:
			N('time elasped: '+m(b)+' Timestamp: '+m(Q[B]));B+=1;M=F.randint(S,U)
			while M==Y:M=F.randint(S,U)
			if M==1:CB(.005,R)
			elif M==2:CD(.01);T(R)
			elif M==3:CC(R)
			Y=M
		if e==B:B=0
		H.update()
		if H.fell:A.voice[0].stop()
		if not A.voice[0].playing:D.fill((0,0,0));D.show();break
		T(.001)
def C9(file_name):
	B=file_name;N('time stamp mode');global a;H=y in B;F=E.read_json_file('/sd/time_stamp_defaults/timestamp_mode.json');F[A8]=[];B=B.replace(y,g)
	if H:I=Z.WaveFile(c(AG+B+O,d))
	else:I=Z.WaveFile(c(z+B+O,d))
	A.voice[0].play(I,loop=G);P=L.monotonic();T(.1)
	while J:
		M=L.monotonic()-P;K.update()
		if K.fell:F[A8].append(M);N(M)
		if not A.voice[0].playing:
			D.fill((0,0,0));D.show();F[A8].append(5000)
			if H:E.write_json_file(AG+B+s,F)
			else:E.write_json_file(z+B+s,F)
			break
	a=G;C('/sd/mvc/timestamp_saved.wav');C(Am);C(BS)
def CA(file_name):
	C=file_name;M=E.read_json_file(z+C+s);D=M[A8];Q=P(D);B=0;R=Z.WaveFile(c(z+C+O,d));A.voice[0].play(R,loop=G);S=L.monotonic()
	while J:
		T(.1);I=L.monotonic()-S;K.update()
		if K.fell:N(I)
		if I>D[B]-F.uniform(.5,1):B+=1;CE()
		if Q==B:B=0
		H.update()
		if H.fell:A.voice[0].stop()
		if not A.voice[0].playing:break
def CP(ledStrip):A=ledStrip;A.brightness=1.;B=F.randint(0,255);C=F.randint(0,255);D=F.randint(0,255);A.fill((B,C,D));A.show()
def CB(speed,duration):
	G=duration;F=speed;H=L.monotonic()
	for B in X(0,255,1):
		for A in X(M):C=A*256//M+B;D[A]=Az(C&255)
		D.show();T(F);E=L.monotonic()-H
		if E>G:return
	for B in reversed(X(0,255,1)):
		for A in X(M):C=A*256//M+B;D[A]=Az(C&255)
		D.show();T(F);E=L.monotonic()-H
		if E>G:return
def CC(duration):
	K=L.monotonic();D.brightness=1.;A=[];A.extend(AR);A.extend(AS);B=[];B.extend(AT);B.extend(AU);C=F.randint(0,255);E=F.randint(0,255);G=F.randint(0,255)
	for H in B:D[H]=C,E,G
	C=F.randint(0,255);E=F.randint(0,255);G=F.randint(0,255)
	while J:
		for H in A:I=F.randint(0,110);M=Ac(C-I,0,255);N=Ac(E-I,0,255);O=Ac(G-I,0,255);D[H]=M,N,O;D.show()
		T(F.uniform(.05,.1));P=L.monotonic()-K
		if P>duration:return
def CD(duration):
	G=L.monotonic();D.brightness=1.
	while J:
		for H in X(0,M):
			I=F.randint(128,255);K=F.randint(128,255);N=F.randint(128,255);A=F.randint(0,2)
			if A==0:B=I;C=0;E=0
			elif A==1:B=0;C=K;E=0
			elif A==2:B=0;C=0;E=N
			D[H]=B,C,E;D.show()
		T(F.uniform(.2,.3));O=L.monotonic()-G
		if O>duration:return
def CE():
	E=[];O=F.randint(-1,P(v)-1)
	if O!=-1:
		for(M,N)in Ad(v):
			if M==O:E.extend(N)
	for(M,N)in Ad(u):
		if M==F.randint(0,P(u)-1):E.extend(N)
	G=F.randint(40,80);H=F.randint(10,25);I=F.randint(0,10);Q=F.randint(5,10);R=150;S=255;T=F.randint(R,S)/255;D.brightness=T;J=0;K=75;U=1;V=50
	for W in X(0,Q):
		B=F.randint(0,50)
		if B<0:B=0
		for C in E:D[C]=G+B,H+B,I+B
		D.show();A=F.randint(J,K);A=A/1000;L.sleep(A);D.fill((0,0,0));D.show()
		for C in E:D[C]=G+B,H+B,I+B
		D.show();A=F.randint(J,K);A=A/1000;L.sleep(A);D.fill((0,0,0));D.show()
		for C in E:D[C]=G+B,H+B,I+B
		D.show();A=F.randint(J,K);A=A/1000;L.sleep(A);D.fill((0,0,0));D.show()
		for C in E:D[C]=G+B,H+B,I+B
		D.show();A=F.randint(J,K);A=A/1000;L.sleep(A);D.fill((0,0,0));D.show();A=F.randint(U,V);A=A/1000;L.sleep(A);D.fill((0,0,0));D.show()
def Ac(my_color,lower,upper):
	C=upper;B=lower;A=my_color
	if A<B:A=B
	if A>C:A=C
	return A
class CF:
	def __init__(A):A.state=None;A.states={};A.paused_state=None
	def add_state(B,state):A=state;B.states[A.name]=A
	def go_to_state(A,state_name):
		if A.state:A.state.exit(A)
		A.state=A.states[state_name];A.state.enter(A)
	def update(A):
		if A.state:A.state.update(A)
	def pause(A):A.state=A.states['paused'];A.state.enter(A)
	def resume_state(A,state_name):
		if A.state:A.state.exit(A)
		A.state=A.states[state_name]
	def reset(A):B0()
class I:
	def __init__(A):0
	@l
	def name(self):return g
	def enter(A,machine):0
	def exit(A,machine):0
	def update(B,machine):
		A=machine
		if H.fell:A.paused_state=A.state.name;A.pause();return G
		return J
class CG(I):
	def __init__(A):0
	@l
	def name(self):return V
	def enter(A,machine):C(BS);E.log_item('Entered base state');I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		global r;A=AY.switch_state(H,K,T,3.)
		if A==BT:
			if r:r=G;C(BJ)
			else:r=J;C(BI)
		elif A==Aq or r:Aa(B[o])
		elif A==Ar:machine.go_to_state(Ai)
class CH(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@l
	def name(self):return Ai
	def enter(A,machine):E.log_item('Main menu');C3();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(B,machine):
		D=machine;H.update();K.update()
		if H.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				C(i+AM[B.menuIndex]+O);B.selectedMenuIndex=B.menuIndex;B.menuIndex+=1
				if B.menuIndex>P(AM)-1:B.menuIndex=0
		if K.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				E=AM[B.selectedMenuIndex]
				if E==As:D.go_to_state(As)
				elif E==At:D.go_to_state(At)
				elif E==A7:D.go_to_state(A7)
				elif E==Au:D.go_to_state(Au)
				elif E==Av:D.go_to_state(Av)
				elif E==AC:D.go_to_state(AC)
				else:C(Y);D.go_to_state(V)
class CI(I):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@l
	def name(self):return As
	def enter(B,machine):
		N(BU)
		if A.voice[0].playing:
			A.voice[0].stop()
			while A.voice[0].playing:0
		else:E.log_item(BV);C1()
		I.enter(B,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(C,machine):
		H.update();K.update()
		if H.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				try:D=Z.WaveFile(c('/sd/lightning_options_voice_commands/option_'+j[C.optionIndex]+O,d));A.voice[0].play(D,loop=G)
				except:BD(m(C.optionIndex+1))
				C.currentOption=C.optionIndex;C.optionIndex+=1
				if C.optionIndex>P(j)-1:C.optionIndex=0
				while A.voice[0].playing:0
		if K.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				B[o]=j[C.currentOption];E.write_json_file(R,B);D=Z.WaveFile(c(Ap,d));A.voice[0].play(D,loop=G)
				while A.voice[0].playing:0
			machine.go_to_state(V)
class CJ(I):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@l
	def name(self):return At
	def enter(B,machine):
		N(BU)
		if A.voice[0].playing:
			A.voice[0].stop()
			while A.voice[0].playing:0
		else:E.log_item(BV);C2()
		I.enter(B,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(C,machine):
		D=machine;H.update();K.update()
		if H.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				try:
					BD(m(C.optionIndex+1));C.currentOption=C.optionIndex;C.optionIndex+=1
					if C.optionIndex>P(q)-1:C.optionIndex=0
					while A.voice[0].playing:0
				except:C8();D.go_to_state(V);return
		if K.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				try:
					B[o]=q[C.currentOption];E.write_json_file(R,B);F=Z.WaveFile(c(Ap,d));A.voice[0].play(F,loop=G)
					while A.voice[0].playing:0
				except:N('no sound track')
			D.go_to_state(V)
class CK(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@l
	def name(self):return A7
	def enter(A,machine):E.log_item(A7);C4();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(B,machine):
		E=machine;global a;H.update();K.update()
		if H.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				C(i+AQ[B.menuIndex]+O);B.selectedMenuIndex=B.menuIndex;B.menuIndex+=1
				if B.menuIndex>P(AQ)-1:B.menuIndex=0
		if K.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				D=AQ[B.selectedMenuIndex]
				if D=='hear_instructions':C(BR)
				elif D==BK:a=J;C(BL);C(Al);E.go_to_state(V)
				elif D==BM:a=G;C(Am)
				else:C(Y);E.go_to_state(V)
class CL(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@l
	def name(self):return AC
	def enter(A,machine):E.log_item(Aw);C5();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		F=machine;H.update();K.update()
		if H.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				C(i+AP[D.menuIndex]+O);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>P(AP)-1:D.menuIndex=0
		if K.fell:
			I=AP[D.selectedMenuIndex]
			if I=='volume_level_adjustment':
				C('/sd/mvc/volume_adjustment_menu.wav');M=G
				while not M:
					L=AY.switch_state(H,K,T,3.)
					if L==Aq:AZ('lower')
					elif L==Ar:AZ('raise')
					elif L==BW:E.write_json_file(R,B);C(Y);M=J;F.go_to_state(V)
					T(.1)
			elif I==An:
				B[A0]=G
				if B[h]==0:B[h]=10
				E.write_json_file(R,B);C(Y);F.go_to_state(V)
			elif I==Ao:B[A0]=J;E.write_json_file(R,B);C(Y);F.go_to_state(V)
class CM(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@l
	def name(self):return Av
	def enter(A,machine):E.log_item(Aw);A6();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		H.update();K.update()
		if H.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				C(i+AN[D.menuIndex]+O);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>P(AN)-1:D.menuIndex=0
		if K.fell:
			F=AN[D.selectedMenuIndex]
			if F=='web_on':B[Ah]=J;BC();A6()
			elif F=='web_off':B[Ah]=G;BC();A6()
			elif F=='hear_url':AB(B[n],J);A6()
			elif F=='hear_instr_web':C('/sd/mvc/web_instruct.wav');A6()
			else:E.write_json_file(R,B);C(Y);machine.go_to_state(V)
class CN(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@l
	def name(self):return Au
	def enter(A,machine):E.log_item(Aw);C6();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		L=machine;H.update();K.update()
		if H.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				C(i+AO[D.menuIndex]+O);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>P(AO)-1:D.menuIndex=0
		if K.fell:
			F=AO[D.selectedMenuIndex]
			if F=='hear_light_setup_instructions':C7()
			elif F=='reset_lights_defaults':BB();C('/sd/mvc/lights_reset_to.wav');BE(G)
			elif F=='hear_current_light_settings':BE(J)
			elif F=='clear_light_string':B[Q]=g;C('/sd/mvc/lights_cleared.wav')
			elif F=='add_lights':
				C('/sd/mvc/add_light_menu.wav')
				while J:
					I=AY.switch_state(H,K,T,3.)
					if I==Aq:
						if A.voice[0].playing:
							A.voice[0].stop()
							while A.voice[0].playing:0
						else:
							D.menuIndex-=1
							if D.menuIndex<0:D.menuIndex=P(t)-1
							D.selectedMenuIndex=D.menuIndex;C(i+t[D.menuIndex]+O)
					elif I==Ar:
						if A.voice[0].playing:
							A.voice[0].stop()
							while A.voice[0].playing:0
						else:
							D.menuIndex+=1
							if D.menuIndex>P(t)-1:D.menuIndex=0
							D.selectedMenuIndex=D.menuIndex;C(i+t[D.menuIndex]+O)
					elif I==BW:
						if A.voice[0].playing:
							A.voice[0].stop()
							while A.voice[0].playing:0
						else:
							if B[Q]==g:B[Q]=t[D.selectedMenuIndex]
							else:B[Q]=B[Q]+','+t[D.selectedMenuIndex]
							C(i+t[D.selectedMenuIndex]+O);C('/sd/mvc/added.wav')
					elif I==BT:
						if A.voice[0].playing:
							A.voice[0].stop()
							while A.voice[0].playing:0
						else:E.write_json_file(R,B);C(Y);A5();L.go_to_state(V)
					T(.1)
			else:E.write_json_file(R,B);C(Y);A5();L.go_to_state(V)
class CQ(I):
	def __init__(A):super().__init__()
	@l
	def name(self):return'example'
	def enter(A,machine):I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(A,machine):I.update(A,machine)
f=CF()
f.add_state(CG())
f.add_state(CH())
f.add_state(CI())
f.add_state(CJ())
f.add_state(CK())
f.add_state(CL())
f.add_state(CM())
f.add_state(CN())
A2.value=J
if AA:
	E.log_item('starting server...')
	try:S.start(m(w.radio.ipv4_address));E.log_item('Listening on http://%s:80'%w.radio.ipv4_address);BF()
	except OSError:L.sleep(5);E.log_item('restarting...');B0()
f.go_to_state(V)
E.log_item('animator has started...')
U('animations started.')
while J:
	f.update();T(.02)
	if AA:
		try:S.poll()
		except BG as AX:E.log_item(AX);continue