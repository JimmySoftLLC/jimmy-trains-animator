BT='right_held'
BS='Choose sounds menu'
BR='Select a program option'
BQ='left_held'
BP='/sd/mvc/animations_are_now_active.wav'
BO='/sd/mvc/create_sound_track_files.wav'
BN='/sd/mvc/local.wav'
BM='/sd/mvc/dot.wav'
BL='animator-lightning'
BK='Utility: '
BJ='timestamp_mode_off'
BI='/sd/mvc/timestamp_mode_on.wav'
BH='timestamp_mode_on'
BG='/sd/mvc/continuous_mode_deactivated.wav'
BF='/sd/mvc/continuous_mode_activated.wav'
BE='wav/no_card.wav'
BD=Exception
At='Set Web Options'
As='web_options'
Ar='light_string_setup_menu'
Aq='choose_my_sounds'
Ap='choose_sounds'
Ao='right'
An='left'
Am='/sd/mvc/option_selected.wav'
Al='volume_pot_on'
Ak='volume_pot_off'
Aj='/sd/mvc/timestamp_mode_off.wav'
Ai='/sd/mvc/timestamp_instructions.wav'
Ah='utf8'
Ag='config wifi imports'
Af='main_menu'
Ae='serve_webpage'
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
s='.json'
r='customers_owned_music_'
q=str
n='option_selected'
m='HOST_NAME'
j=property
h='/sd/mvc/'
g='volume'
f=''
c='rb'
b=open
Y='/sd/mvc/all_changes_complete.wav'
X=range
V='base_state'
R='/sd/config_lightning.json'
Q='light_string'
P='.wav'
O=len
N=print
J=True
G=False
import gc,files as E
def T(collection_point):gc.collect();A=gc.mem_free();E.log_item('Point '+collection_point+' Available memory: {} bytes'.format(A))
T('Imports gc, files')
import time as L,audiocore as Z,audiomixer as BU,audiobusio as BV,sdcardio as Au,storage as A9,busio,digitalio as o,board as W,neopixel as Av,random as F,rtc,microcontroller as AH
from analogio import AnalogIn as BW
from rainbowio import colorwheel as Aw
from adafruit_debouncer import Debouncer as Ax
def Ay():AH.on_next_reset(AH.RunMode.NORMAL);AH.reset()
T('imports')
BX=BW(W.A0)
def BY(pin,wait_for):
	B=wait_for/10;A=0
	for C in X(10):L.sleep(B);A+=1;A=A/10
	return pin.value/65536
A2=o.DigitalInOut(W.GP28)
A2.direction=o.Direction.OUTPUT
A2.value=G
BZ=W.GP6
Ba=W.GP7
AI=o.DigitalInOut(BZ)
AI.direction=o.Direction.INPUT
AI.pull=o.Pull.UP
H=Ax(AI)
AJ=o.DigitalInOut(Ba)
AJ.direction=o.Direction.INPUT
AJ.pull=o.Pull.UP
K=Ax(AJ)
Bb=W.GP18
Bc=W.GP19
Bd=W.GP20
Be=BV.I2SOut(bit_clock=Bb,word_select=Bc,data=Bd)
A2.value=J
Bf=W.GP2
Bg=W.GP3
Bh=W.GP4
Az=W.GP5
A_=busio.SPI(Bf,Bg,Bh)
Bi=2
A=BU.Mixer(voice_count=Bi,sample_rate=22050,channel_count=2,bits_per_sample=16,samples_signed=J,buffer_size=4096)
Be.play(A)
B0=.2
A.voice[0].level=B0
A.voice[1].level=B0
try:AK=Au.SDCard(A_,Az);AL=A9.VfsFat(AK);A9.mount(AL,'/sd')
except:
	A3=Z.WaveFile(b(BE,c));A.voice[0].play(A3,loop=G)
	while A.voice[0].playing:0
	B1=G
	while not B1:
		H.update()
		if H.fell:
			try:
				AK=Au.SDCard(A_,Az);AL=A9.VfsFat(AK);A9.mount(AL,'/sd');B1=J;A3=Z.WaveFile(b('/sd/mvc/micro_sd_card_success.wav',c));A.voice[0].play(A3,loop=G)
				while A.voice[0].playing:0
			except:
				A3=Z.WaveFile(b(BE,c));A.voice[0].play(A3,loop=G)
				while A.voice[0].playing:0
A2.value=G
Bj=rtc.RTC()
Bj.datetime=L.struct_time((2019,5,29,15,14,15,0,-1,-1))
B=E.read_json_file(R)
t=B['options']
k=E.return_directory(r,'/sd/customers_owned_music',P)
A4=[]
A4.extend(k)
A4.extend(t)
B2=E.return_directory(f,'/sd/time_stamp_defaults',s)
AA=B[Ae]
Bk=E.read_json_file('/sd/mvc/main_menu.json')
AM=Bk[Af]
Bl=E.read_json_file('/sd/mvc/web_menu.json')
AN=Bl['web_menu']
Bm=E.read_json_file('/sd/mvc/light_string_menu.json')
AO=Bm['light_string_menu']
Bn=E.read_json_file('/sd/mvc/light_options.json')
u=Bn['light_options']
Bo=E.read_json_file('/sd/mvc/volume_settings.json')
AP=Bo[AC]
Bp=E.read_json_file('/sd/mvc/add_sounds_animate.json')
AQ=Bp[A7]
T('config setup')
p=G
a=G
v=[]
w=[]
AR=[]
AS=[]
AT=[]
AU=[]
M=0
D=Av.NeoPixel(W.GP10,M)
def B3(part):
	B=[]
	for D in v:
		for A in D:C=A;break
		if part==AD:
			for A in X(0,5):B.append(A+C)
		if part==AE:
			for A in X(5,10):B.append(A+C)
	return B
def B4(part):
	B=[]
	for D in w:
		for A in D:C=A;break
		if part==AD:
			for A in X(0,2):B.append(A+C)
		if part==AE:
			for A in X(2,4):B.append(A+C)
	return B
def Bq():
	global AR,AS,AT,AU;AR=B3(AD);AS=B3(AE);AT=B4(AD);AU=B4(AE)
	for B in v:
		for A in B:D[A]=50,50,50
		D.show();L.sleep(.3);D.fill((0,0,0));D.show()
	for C in w:
		for A in C:D[A]=50,50,50
		D.show();L.sleep(.3);D.fill((0,0,0));D.show()
def A5():
	global v,w,M,D,M;v=[];w=[];M=0;F=B[Q].split(',')
	for H in F:
		C=H.split('-')
		if O(C)==2:
			E,A=C;A=int(A)
			if E=='bar':I=list(X(M,M+A));v.append(I);M+=A
			elif E=='bolt':J=list(X(M,M+A));w.append(J);M+=A
	N('Number of pixels total: ',M);D.deinit();T('Deinit ledStrip');D=Av.NeoPixel(W.GP10,M);D.auto_write=G;D.brightness=1.;Bq()
A5()
T('Neopixels setup')
if AA:
	import socketpool as Br,mdns;T(Ag);import wifi as x;T(Ag);from adafruit_httpserver import Server,Request,FileResponse as AV,Response as d,POST as i;T(Ag);E.log_item('Connecting to WiFi');B5='jimmytrainsguest';B6=f
	try:B7=E.read_json_file('/sd/env.json');B5=B7['WIFI_SSID'];B6=B7['WIFI_PASSWORD'];T('wifi env');N('Using env ssid and password')
	except:N('Using default ssid and password')
	try:
		x.radio.connect(B5,B6);T('wifi connect');AW=mdns.Server(x.radio);AW.hostname=B[m];AW.advertise_service(service_type='_http',protocol='_tcp',port=80);Bs=[hex(A)for A in x.radio.mac_address];E.log_item('My MAC addr:'+q(Bs));Bt=q(x.radio.ipv4_address);E.log_item('My IP address is'+Bt);E.log_item('Connected to WiFi');Bu=Br.SocketPool(x.radio);U=Server(Bu,'/static',debug=J);T('wifi server')
		@U.route('/')
		def B8(request):T('Home page.');return AV(request,'index.html','/')
		@U.route('/mui.min.css')
		def B8(request):return AV(request,'mui.min.css','/')
		@U.route('/mui.min.js')
		def B8(request):return AV(request,'mui.min.js','/')
		@U.route('/animation',[i])
		def l(request):
			F=request;global B,p,a;A=F.raw_request.decode(Ah)
			if'cont_mode_on'in A:p=J;C(BF)
			elif'cont_mode_off'in A:p=G;C(BG)
			elif BH in A:a=J;C(BI);C(Ai)
			elif BJ in A:a=G;C(Aj)
			elif'reset_animation_timing_to_defaults'in A:
				for H in B2:I=E.read_json_file('/sd/time_stamp_defaults/'+H+s);E.write_json_file(z+H+s,I)
			elif r in A:
				for D in k:
					if D in A:B[n]=D;Aa(B[n]);break
			else:
				for D in B2:
					if D in A:B[n]=D;Aa(B[n]);break
			E.write_json_file(R,B);return d(F,'Animation '+B[n]+' started.')
		@U.route('/utilities',[i])
		def l(request):
			I='reset_to_defaults';H='speaker_test';F=request;global B;A=f;D=F.raw_request.decode(Ah)
			if H in D:A=H;C('/sd/mvc/left_speaker_right_speaker.wav')
			elif Ak in D:A=Ak;B[A0]=G;E.write_json_file(R,B);C(Y)
			elif Al in D:A=Al;B[A0]=J;E.write_json_file(R,B);C(Y)
			elif I in D:A=I;Bv();E.write_json_file(R,B);C(Y);e.go_to_state(V)
			return d(F,BK+A)
		@U.route('/lights',[i])
		def l(request):
			O='set_to_100';N='set_to_80';M='set_to_60';L='set_to_40';K='set_to_20';J='set_to_0';I='set_to_white';H='set_to_blue';G='set_to_green';F='set_to_red';E=request;global B;A=f;C=E.raw_request.decode(Ah)
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
			return d(E,BK+A)
		@U.route('/update-host-name',[i])
		def l(request):A=request;global B;C=A.json();B[m]=C[AF];E.write_json_file(R,B);AW.hostname=B[m];BC();return d(A,B[m])
		@U.route('/get-host-name',[i])
		def l(request):return d(request,B[m])
		@U.route('/update-volume',[i])
		def l(request):A=request;global B;C=A.json();AZ(C[A1]);return d(A,B[g])
		@U.route('/get-volume',[i])
		def l(request):return d(request,B[g])
		@U.route('/update-light-string',[i])
		def l(request):
			G=' data: ';F='action: ';D=request;global B;A=D.json()
			if A[A1]=='save'or A[A1]=='clear'or A[A1]=='defaults':B[Q]=A[AF];N(F+A[A1]+G+B[Q]);E.write_json_file(R,B);A5();C(Y);return d(D,B[Q])
			if B[Q]==f:B[Q]=A[AF]
			else:B[Q]=B[Q]+','+A[AF]
			N(F+A[A1]+G+B[Q]);E.write_json_file(R,B);A5();C(Y);return d(D,B[Q])
		@U.route('/get-light-string',[i])
		def l(request):return d(request,B[Q])
		@U.route('/get-customers-sound-tracks',[i])
		def l(request):A=E.json_stringify(k);return d(request,A)
	except BD as AX:AA=G;E.log_item(AX)
T('web server')
import utilities as AY
T('utilities')
def S(seconds):
	D=seconds
	if B[A0]:C=BY(BX,D);A.voice[0].level=C
	else:
		try:C=int(B[g])/100
		except:C=.5
		if C<0 or C>1:C=.5
		A.voice[0].level=C;A.voice[1].level=C;L.sleep(D)
def B9():global B;B[Q]='bar-10,bolt-4,bar-10,bolt-4,bar-10,bolt-4'
def Bv():global B;B[A0]=J;B[m]=BL;B[n]='thunder_birds_rain';B[g]='30';B9()
def AZ(action):
	D=action;A=int(B[g])
	if g in D:F=D.split(g);A=int(F[1])
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
	B[g]=q(A);B[A0]=G;E.write_json_file(R,B);C('/sd/mvc/volume.wav');AB(B[g],G)
def C(file_name):
	if A.voice[0].playing:
		A.voice[0].stop()
		while A.voice[0].playing:S(.02)
	B=Z.WaveFile(b(file_name,c));A.voice[0].play(B,loop=G)
	while A.voice[0].playing:Bw()
def CJ():
	A.voice[0].stop()
	while A.voice[0].playing:0
def Bw():
	S(.02);H.update()
	if H.fell:A.voice[0].stop()
def AB(str_to_speak,addLocal):
	for A in str_to_speak:
		if A==' ':A='space'
		if A=='-':A='dash'
		if A=='.':A='dot'
		C(h+A+P)
	if addLocal:C(BM);C(BN)
def Bx():C('/sd/mvc/sound_selection_menu.wav');y()
def By():C('/sd/mvc/choose_my_sounds_menu.wav');y()
def y():C('/sd/mvc/press_left_button_right_button.wav')
def Bz():C('/sd/mvc/main_menu.wav');y()
def B_():C('/sd/mvc/add_sounds_animate.wav');y()
def A6():C('/sd/mvc/web_menu.wav');y()
def C0():C('/sd/mvc/volume_settings_menu.wav');y()
def C1():C('/sd/mvc/light_string_setup_menu.wav');y()
def C2():C('/sd/mvc/string_instructions.wav')
def BA():C(Am)
def BB(play_intro):
	if play_intro:C('/sd/mvc/current_light_settings_are.wav')
	A=B[Q].split(',')
	for(D,E)in Ad(A):C('/sd/mvc/position.wav');C(h+q(D+1)+P);C('/sd/mvc/is.wav');C(h+E+P)
def C3():
	C('/sd/mvc/no_user_soundtrack_found.wav')
	while J:
		H.update();K.update()
		if H.fell:break
		if K.fell:C(BO);break
def BC():
	C('/sd/mvc/animator_available_on_network.wav');C('/sd/mvc/to_access_type.wav')
	if B[m]==BL:C('/sd/mvc/animator_dash_lightning.wav');C(BM);C(BN)
	else:AB(B[m],J)
	C('/sd/mvc/in_your_browser.wav')
def Aa(file_name):
	G='Sound file: ';E='Random sound file: ';C=file_name;N(C);A=C
	if C=='random_built_in':D=O(t)-4;B=F.randint(0,D);A=t[B];N(E+t[B]);N(G+A)
	elif C=='random_my':D=O(k)-1;B=F.randint(0,D);A=k[B];N(E+k[B]);N(G+A)
	elif C=='random_all':D=O(A4)-4;B=F.randint(0,D);A=A4[B];N(E+A4[B]);N(G+A)
	if a:C4(A)
	elif r in A:Ab(A)
	elif A=='alien_lightshow':Ab(A)
	elif A=='inspiring_cinematic_ambient_lightshow':Ab(A)
	else:C5(A)
def Ab(file_name):
	I=file_name;global a;T=1;U=3;V=r in I
	if V:
		I=I.replace(r,f)
		try:W=E.read_json_file(AG+I+s)
		except:
			C('/sd/mvc/no_timestamp_file_found.wav')
			while J:
				H.update();K.update()
				if H.fell:a=G;return
				if K.fell:a=J;C(Ai);return
	else:W=E.read_json_file(z+I+s)
	Q=W[A8];e=O(Q);B=0
	if V:X=Z.WaveFile(b(AG+I+P,c))
	else:X=Z.WaveFile(b(z+I+P,c))
	A.voice[0].play(X,loop=G);g=L.monotonic();M=0
	while J:
		Y=0;d=L.monotonic()-g
		if B<O(Q)-2:R=Q[B+1]-Q[B]-.25
		else:R=.25
		if R<0:R=0
		if d>Q[B]-.25:
			N('time elasped: '+q(d)+' Timestamp: '+q(Q[B]));B+=1;M=F.randint(T,U)
			while M==Y:M=F.randint(T,U)
			if M==1:C6(.005,R)
			elif M==2:C8(.01);S(R)
			elif M==3:C7(R)
			Y=M
		if e==B:B=0
		H.update()
		if H.fell:A.voice[0].stop()
		if not A.voice[0].playing:D.fill((0,0,0));D.show();break
		S(.001)
def C4(file_name):
	B=file_name;N('time stamp mode');global a;H=r in B;F=E.read_json_file('/sd/time_stamp_defaults/timestamp_mode.json');F[A8]=[];B=B.replace(r,f)
	if H:I=Z.WaveFile(b(AG+B+P,c))
	else:I=Z.WaveFile(b(z+B+P,c))
	A.voice[0].play(I,loop=G);O=L.monotonic();S(.1)
	while J:
		M=L.monotonic()-O;K.update()
		if K.fell:F[A8].append(M);N(M)
		if not A.voice[0].playing:
			D.fill((0,0,0));D.show();F[A8].append(5000)
			if H:E.write_json_file(AG+B+s,F)
			else:E.write_json_file(z+B+s,F)
			break
	a=G;C('/sd/mvc/timestamp_saved.wav');C(Aj);C(BP)
def C5(file_name):
	C=file_name;M=E.read_json_file(z+C+s);D=M[A8];Q=O(D);B=0;R=Z.WaveFile(b(z+C+P,c));A.voice[0].play(R,loop=G);T=L.monotonic()
	while J:
		S(.1);I=L.monotonic()-T;K.update()
		if K.fell:N(I)
		if I>D[B]-F.uniform(.5,1):B+=1;C9()
		if Q==B:B=0
		H.update()
		if H.fell:A.voice[0].stop()
		if not A.voice[0].playing:break
def CK(ledStrip):A=ledStrip;A.brightness=1.;B=F.randint(0,255);C=F.randint(0,255);D=F.randint(0,255);A.fill((B,C,D));A.show()
def C6(speed,duration):
	G=duration;F=speed;H=L.monotonic()
	for B in X(0,255,1):
		for A in X(M):C=A*256//M+B;D[A]=Aw(C&255)
		D.show();S(F);E=L.monotonic()-H
		if E>G:return
	for B in reversed(X(0,255,1)):
		for A in X(M):C=A*256//M+B;D[A]=Aw(C&255)
		D.show();S(F);E=L.monotonic()-H
		if E>G:return
def C7(duration):
	K=L.monotonic();D.brightness=1.;A=[];A.extend(AR);A.extend(AS);B=[];B.extend(AT);B.extend(AU);C=F.randint(0,255);E=F.randint(0,255);G=F.randint(0,255)
	for H in B:D[H]=C,E,G
	C=F.randint(0,255);E=F.randint(0,255);G=F.randint(0,255)
	while J:
		for H in A:I=F.randint(0,110);M=Ac(C-I,0,255);N=Ac(E-I,0,255);O=Ac(G-I,0,255);D[H]=M,N,O;D.show()
		S(F.uniform(.05,.1));P=L.monotonic()-K
		if P>duration:return
def C8(duration):
	G=L.monotonic();D.brightness=1.
	while J:
		for H in X(0,M):
			I=F.randint(128,255);K=F.randint(128,255);N=F.randint(128,255);A=F.randint(0,2)
			if A==0:B=I;C=0;E=0
			elif A==1:B=0;C=K;E=0
			elif A==2:B=0;C=0;E=N
			D[H]=B,C,E;D.show()
		S(F.uniform(.2,.3));O=L.monotonic()-G
		if O>duration:return
def C9():
	E=[];P=F.randint(-1,O(w)-1)
	if P!=-1:
		for(M,N)in Ad(w):
			if M==P:E.extend(N)
	for(M,N)in Ad(v):
		if M==F.randint(0,O(v)-1):E.extend(N)
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
class CA:
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
	def reset(A):Ay()
class I:
	def __init__(A):0
	@j
	def name(self):return f
	def enter(A,machine):0
	def exit(A,machine):0
	def update(B,machine):
		A=machine
		if H.fell:A.paused_state=A.state.name;A.pause();return G
		return J
class CB(I):
	def __init__(A):0
	@j
	def name(self):return V
	def enter(A,machine):C(BP);E.log_item('Entered base state');I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		global p;A=AY.switch_state(H,K,S,3.)
		if A==BQ:
			if p:p=G;C(BG)
			else:p=J;C(BF)
		elif A==An or p:Aa(B[n])
		elif A==Ao:machine.go_to_state(Af)
class CC(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@j
	def name(self):return Af
	def enter(A,machine):E.log_item('Main menu');Bz();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(B,machine):
		D=machine;H.update();K.update()
		if H.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				C(h+AM[B.menuIndex]+P);B.selectedMenuIndex=B.menuIndex;B.menuIndex+=1
				if B.menuIndex>O(AM)-1:B.menuIndex=0
		if K.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				E=AM[B.selectedMenuIndex]
				if E==Ap:D.go_to_state(Ap)
				elif E==Aq:D.go_to_state(Aq)
				elif E==A7:D.go_to_state(A7)
				elif E==Ar:D.go_to_state(Ar)
				elif E==As:D.go_to_state(As)
				elif E==AC:D.go_to_state(AC)
				else:C(Y);D.go_to_state(V)
class CD(I):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@j
	def name(self):return Ap
	def enter(B,machine):
		N(BR)
		if A.voice[0].playing:
			A.voice[0].stop()
			while A.voice[0].playing:0
		else:E.log_item(BS);Bx()
		I.enter(B,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(C,machine):
		H.update();K.update()
		if H.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				D=Z.WaveFile(b('/sd/lightning_options_voice_commands/option_'+t[C.optionIndex]+P,c));A.voice[0].play(D,loop=G);C.currentOption=C.optionIndex;C.optionIndex+=1
				if C.optionIndex>O(t)-1:C.optionIndex=0
				while A.voice[0].playing:0
		if K.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				B[n]=t[C.currentOption];E.write_json_file(R,B);D=Z.WaveFile(b(Am,c));A.voice[0].play(D,loop=G)
				while A.voice[0].playing:0
			machine.go_to_state(V)
class CE(I):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@j
	def name(self):return Aq
	def enter(B,machine):
		N(BR)
		if A.voice[0].playing:
			A.voice[0].stop()
			while A.voice[0].playing:0
		else:E.log_item(BS);By()
		I.enter(B,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		F=machine;H.update();K.update()
		if H.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				try:
					L=k[D.optionIndex].replace(r,f);I=q(D.optionIndex+1);C('/sd/mvc/song.wav');AB(I,G);D.currentOption=D.optionIndex;D.optionIndex+=1
					if D.optionIndex>O(k)-1:D.optionIndex=0
					while A.voice[0].playing:0
				except:C3();F.go_to_state(V);return
		if K.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				try:
					B[n]=k[D.currentOption];E.write_json_file(R,B);J=Z.WaveFile(b(Am,c));A.voice[0].play(J,loop=G)
					while A.voice[0].playing:0
				except:N('no sound track')
			F.go_to_state(V)
class CF(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@j
	def name(self):return A7
	def enter(A,machine):E.log_item(A7);B_();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(B,machine):
		E=machine;global a;H.update();K.update()
		if H.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				C(h+AQ[B.menuIndex]+P);B.selectedMenuIndex=B.menuIndex;B.menuIndex+=1
				if B.menuIndex>O(AQ)-1:B.menuIndex=0
		if K.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				D=AQ[B.selectedMenuIndex]
				if D=='hear_instructions':C(BO)
				elif D==BH:a=J;C(BI);C(Ai);E.go_to_state(V)
				elif D==BJ:a=G;C(Aj)
				else:C(Y);E.go_to_state(V)
class CG(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@j
	def name(self):return AC
	def enter(A,machine):E.log_item(At);C0();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		F=machine;H.update();K.update()
		if H.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				C(h+AP[D.menuIndex]+P);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>O(AP)-1:D.menuIndex=0
		if K.fell:
			I=AP[D.selectedMenuIndex]
			if I=='volume_level_adjustment':
				C('/sd/mvc/volume_adjustment_menu.wav');M=G
				while not M:
					L=AY.switch_state(H,K,S,3.)
					if L==An:AZ('lower')
					elif L==Ao:AZ('raise')
					elif L==BT:E.write_json_file(R,B);C(Y);M=J;F.go_to_state(V)
					S(.1)
			elif I==Ak:
				B[A0]=G
				if B[g]==0:B[g]=10
				E.write_json_file(R,B);C(Y);F.go_to_state(V)
			elif I==Al:B[A0]=J;E.write_json_file(R,B);C(Y);F.go_to_state(V)
class CH(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@j
	def name(self):return As
	def enter(A,machine):E.log_item(At);A6();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		H.update();K.update()
		if H.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				C(h+AN[D.menuIndex]+P);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>O(AN)-1:D.menuIndex=0
		if K.fell:
			F=AN[D.selectedMenuIndex]
			if F=='web_on':B[Ae]=J;BA();A6()
			elif F=='web_off':B[Ae]=G;BA();A6()
			elif F=='hear_url':AB(B[m],J);A6()
			elif F=='hear_instr_web':C('/sd/mvc/web_instruct.wav');A6()
			else:E.write_json_file(R,B);C(Y);machine.go_to_state(V)
class CI(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@j
	def name(self):return Ar
	def enter(A,machine):E.log_item(At);C1();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		L=machine;H.update();K.update()
		if H.fell:
			if A.voice[0].playing:
				A.voice[0].stop()
				while A.voice[0].playing:0
			else:
				C(h+AO[D.menuIndex]+P);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>O(AO)-1:D.menuIndex=0
		if K.fell:
			F=AO[D.selectedMenuIndex]
			if F=='hear_light_setup_instructions':C2()
			elif F=='reset_lights_defaults':B9();C('/sd/mvc/lights_reset_to.wav');BB(G)
			elif F=='hear_current_light_settings':BB(J)
			elif F=='clear_light_string':B[Q]=f;C('/sd/mvc/lights_cleared.wav')
			elif F=='add_lights':
				C('/sd/mvc/add_light_menu.wav')
				while J:
					I=AY.switch_state(H,K,S,3.)
					if I==An:
						if A.voice[0].playing:
							A.voice[0].stop()
							while A.voice[0].playing:0
						else:
							D.menuIndex-=1
							if D.menuIndex<0:D.menuIndex=O(u)-1
							D.selectedMenuIndex=D.menuIndex;C(h+u[D.menuIndex]+P)
					elif I==Ao:
						if A.voice[0].playing:
							A.voice[0].stop()
							while A.voice[0].playing:0
						else:
							D.menuIndex+=1
							if D.menuIndex>O(u)-1:D.menuIndex=0
							D.selectedMenuIndex=D.menuIndex;C(h+u[D.menuIndex]+P)
					elif I==BT:
						if A.voice[0].playing:
							A.voice[0].stop()
							while A.voice[0].playing:0
						else:
							if B[Q]==f:B[Q]=u[D.selectedMenuIndex]
							else:B[Q]=B[Q]+','+u[D.selectedMenuIndex]
							C(h+u[D.selectedMenuIndex]+P);C('/sd/mvc/added.wav')
					elif I==BQ:
						if A.voice[0].playing:
							A.voice[0].stop()
							while A.voice[0].playing:0
						else:E.write_json_file(R,B);C(Y);A5();L.go_to_state(V)
					S(.1)
			else:E.write_json_file(R,B);C(Y);A5();L.go_to_state(V)
class CL(I):
	def __init__(A):super().__init__()
	@j
	def name(self):return'example'
	def enter(A,machine):I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(A,machine):I.update(A,machine)
e=CA()
e.add_state(CB())
e.add_state(CC())
e.add_state(CD())
e.add_state(CE())
e.add_state(CF())
e.add_state(CG())
e.add_state(CH())
e.add_state(CI())
A2.value=J
if AA:
	E.log_item('starting server...')
	try:U.start(q(x.radio.ipv4_address));E.log_item('Listening on http://%s:80'%x.radio.ipv4_address);BC()
	except OSError:L.sleep(5);E.log_item('restarting...');Ay()
e.go_to_state(V)
E.log_item('animator has started...')
T('animations started.')
while J:
	e.update();S(.02)
	if AA:
		try:U.poll()
		except BD as AX:E.log_item(AX);continue