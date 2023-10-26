BX='right_held'
BW='Choose sounds menu'
BV='Select a program option'
BU='left_held'
BT='/sd/mvc/animations_are_now_active.wav'
BS='/sd/mvc/create_sound_track_files.wav'
BR='/sd/mvc/local.wav'
BQ='/sd/mvc/dot.wav'
BP='animator-lightning'
BO='Utility: '
BN='timestamp_mode_off'
BM='/sd/mvc/timestamp_mode_on.wav'
BL='timestamp_mode_on'
BK='/sd/mvc/continuous_mode_deactivated.wav'
BJ='/sd/mvc/continuous_mode_activated.wav'
BI='wav/no_card.wav'
BH=Exception
Az='Set Web Options'
Ay='web_options'
Ax='light_string_setup_menu'
Aw='choose_my_sounds'
Av='choose_sounds'
Au='right'
At='left'
As='/sd/mvc/option_selected.wav'
Ar='volume_pot_on'
Aq='volume_pot_off'
Ap='/sd/mvc/timestamp_mode_off.wav'
Ao='/sd/mvc/timestamp_instructions.wav'
An='alien_lightshow'
Am='inspiring_cinematic_ambient_lightshow'
Al='thunder_birds_rain'
Ak='random_all'
Aj='random_my'
Ai='random_built_in'
Ah='utf8'
Ag='config wifi imports'
Af='main_menu'
Ae='serve_webpage'
Ad=enumerate
AH='/sd/customers_owned_music/'
AG='text'
AF='end'
AE='start'
AD='volume_settings'
A9='flashTime'
A8='add_sounds_animate'
A2='action'
A1='volume_pot'
A0='/sd/lightning_sounds/'
t='.json'
s='customers_owned_music_'
r=str
o='HOST_NAME'
k=property
i='/sd/mvc/'
h='volume'
g=''
d='rb'
c=open
a='/sd/mvc/all_changes_complete.wav'
Z=range
W='base_state'
S='/sd/config_lightning.json'
R='light_string'
Q='.wav'
P=len
O=print
K=True
H='option_selected'
G=False
import gc,files as E
def U(collection_point):gc.collect();A=gc.mem_free();E.log_item('Point '+collection_point+' Available memory: {} bytes'.format(A))
U('Imports gc, files')
import time as L,audiocore as b,audiomixer as BY,audiobusio as BZ,sdcardio as A_,storage as AA,busio,digitalio as p,board as Y,neopixel as B0,random as F,rtc,microcontroller as AI
from analogio import AnalogIn as Ba
from rainbowio import colorwheel as B1
from adafruit_debouncer import Debouncer as B2
def Bb():AI.on_next_reset(AI.RunMode.NORMAL);AI.reset()
U('imports')
Bc=Ba(Y.A0)
def Bd(pin,wait_for):
	B=wait_for/10;A=0
	for C in Z(10):L.sleep(B);A+=1;A=A/10
	return pin.value/65536
A3=p.DigitalInOut(Y.GP28)
A3.direction=p.Direction.OUTPUT
A3.value=G
Be=Y.GP6
Bf=Y.GP7
AJ=p.DigitalInOut(Be)
AJ.direction=p.Direction.INPUT
AJ.pull=p.Pull.UP
I=B2(AJ)
AK=p.DigitalInOut(Bf)
AK.direction=p.Direction.INPUT
AK.pull=p.Pull.UP
M=B2(AK)
Bg=Y.GP18
Bh=Y.GP19
Bi=Y.GP20
Bj=BZ.I2SOut(bit_clock=Bg,word_select=Bh,data=Bi)
A3.value=K
Bk=Y.GP2
Bl=Y.GP3
Bm=Y.GP4
B3=Y.GP5
B4=busio.SPI(Bk,Bl,Bm)
Bn=2
B=BY.Mixer(voice_count=Bn,sample_rate=22050,channel_count=2,bits_per_sample=16,samples_signed=K,buffer_size=4096)
Bj.play(B)
B5=.2
B.voice[0].level=B5
B.voice[1].level=B5
try:AL=A_.SDCard(B4,B3);AM=AA.VfsFat(AL);AA.mount(AM,'/sd')
except:
	A4=b.WaveFile(c(BI,d));B.voice[0].play(A4,loop=G)
	while B.voice[0].playing:0
	B6=G
	while not B6:
		I.update()
		if I.fell:
			try:
				AL=A_.SDCard(B4,B3);AM=AA.VfsFat(AL);AA.mount(AM,'/sd');B6=K;A4=b.WaveFile(c('/sd/mvc/micro_sd_card_success.wav',d));B.voice[0].play(A4,loop=G)
				while B.voice[0].playing:0
			except:
				A4=b.WaveFile(c(BI,d));B.voice[0].play(A4,loop=G)
				while B.voice[0].playing:0
A3.value=G
Bo=rtc.RTC()
Bo.datetime=L.struct_time((2019,5,29,15,14,15,0,-1,-1))
A=E.read_json_file(S)
u=A['options']
l=E.return_directory(s,'/sd/customers_owned_music',Q)
A5=[]
A5.extend(l)
A5.extend(u)
Bp=E.return_directory(g,'/sd/time_stamp_defaults',t)
AB=A[Ae]
Bq=E.read_json_file('/sd/mvc/main_menu.json')
AN=Bq[Af]
Br=E.read_json_file('/sd/mvc/web_menu.json')
AO=Br['web_menu']
Bs=E.read_json_file('/sd/mvc/light_string_menu.json')
AP=Bs['light_string_menu']
Bt=E.read_json_file('/sd/mvc/light_options.json')
v=Bt['light_options']
Bu=E.read_json_file('/sd/mvc/volume_settings.json')
AQ=Bu[AD]
Bv=E.read_json_file('/sd/mvc/add_sounds_animate.json')
AR=Bv[A8]
U('config setup')
q=G
m=G
w=[]
x=[]
AS=[]
AT=[]
AU=[]
AV=[]
N=0
D=B0.NeoPixel(Y.GP10,N)
def B7(part):
	B=[]
	for D in w:
		for A in D:C=A;break
		if part==AE:
			for A in Z(0,5):B.append(A+C)
		if part==AF:
			for A in Z(5,10):B.append(A+C)
	return B
def B8(part):
	B=[]
	for D in x:
		for A in D:C=A;break
		if part==AE:
			for A in Z(0,2):B.append(A+C)
		if part==AF:
			for A in Z(2,4):B.append(A+C)
	return B
def Bw():
	global AS,AT,AU,AV;AS=B7(AE);AT=B7(AF);AU=B8(AE);AV=B8(AF)
	for B in w:
		for A in B:D[A]=50,50,50
		D.show();L.sleep(.3);D.fill((0,0,0));D.show()
	for C in x:
		for A in C:D[A]=50,50,50
		D.show();L.sleep(.3);D.fill((0,0,0));D.show()
def A6():
	global w,x,N,D,N;w=[];x=[];N=0;F=A[R].split(',')
	for H in F:
		C=H.split('-')
		if P(C)==2:
			E,B=C;B=int(B)
			if E=='bar':I=list(Z(N,N+B));w.append(I);N+=B
			elif E=='bolt':J=list(Z(N,N+B));x.append(J);N+=B
	O('Number of pixels total: ',N);D.deinit();U('Deinit ledStrip');D=B0.NeoPixel(Y.GP10,N);D.auto_write=G;D.brightness=1.;Bw()
A6()
U('Neopixels setup')
if AB:
	import socketpool as Bx,mdns;U(Ag);import wifi as y;U(Ag);from adafruit_httpserver import Server,Request,FileResponse as AW,Response as e,POST as j;U(Ag);E.log_item('Connecting to WiFi');B9='jimmytrainsguest';BA=g
	try:BB=E.read_json_file('/sd/env.json');B9=BB['WIFI_SSID'];BA=BB['WIFI_PASSWORD'];U('wifi env');O('Using env ssid and password')
	except:O('Using default ssid and password')
	try:
		y.radio.connect(B9,BA);U('wifi connect');AX=mdns.Server(y.radio);AX.hostname=A[o];AX.advertise_service(service_type='_http',protocol='_tcp',port=80);By=[hex(A)for A in y.radio.mac_address];E.log_item('My MAC addr:'+r(By));Bz=r(y.radio.ipv4_address);E.log_item('My IP address is'+Bz);E.log_item('Connected to WiFi');B_=Bx.SocketPool(y.radio);V=Server(B_,'/static',debug=K);U('wifi server')
		@V.route('/')
		def BC(request):U('Home page.');return AW(request,'index.html','/')
		@V.route('/mui.min.css')
		def BC(request):return AW(request,'mui.min.css','/')
		@V.route('/mui.min.js')
		def BC(request):return AW(request,'mui.min.js','/')
		@V.route('/animation',[j])
		def n(request):
			P='thunder_distant';O='thunder_and_rain';N='halloween_thunder';M='epic_thunder';L='dark_thunder';J='continuous_thunder';D=request;global A;global q;B=D.raw_request.decode(Ah)
			if Ai in B:A[H]=Ai;X(A[H])
			elif Aj in B:A[H]=Aj;X(A[H])
			elif Ak in B:A[H]=Ak;X(A[H])
			elif Al in B:A[H]=Al;X(A[H])
			elif J in B:A[H]=J;X(A[H])
			elif L in B:A[H]=L;X(A[H])
			elif M in B:A[H]=M;X(A[H])
			elif N in B:A[H]=N;X(A[H])
			elif O in B:A[H]=O;X(A[H])
			elif P in B:A[H]=P;X(A[H])
			elif Am in B:A[H]=Am;X(A[H])
			elif An in B:A[H]=An;X(A[H])
			elif s in B:
				for F in l:
					if F in B:A[H]=F;X(A[H]);break
			elif'cont_mode_on'in B:q=K;C(BJ)
			elif'cont_mode_off'in B:q=G;C(BK)
			elif BL in B:Q=K;C(BM);C(Ao)
			elif BN in B:Q=G;C(Ap)
			elif'reset_animation_timing_to_defaults'in B:
				for I in Bp:R=E.read_json_file('/sd/time_stamp_defaults/'+I+t);E.write_json_file(A0+I+t,R)
			E.write_json_file(S,A);return e(D,'Animation '+A[H]+' started.')
		@V.route('/utilities',[j])
		def n(request):
			I='reset_to_defaults';H='speaker_test';F=request;global A;B=g;D=F.raw_request.decode(Ah)
			if H in D:B=H;C('/sd/mvc/left_speaker_right_speaker.wav')
			elif Aq in D:B=Aq;A[A1]=G;E.write_json_file(S,A);C(a)
			elif Ar in D:B=Ar;A[A1]=K;E.write_json_file(S,A);C(a)
			elif I in D:B=I;C0();E.write_json_file(S,A);C(a);f.go_to_state(W)
			return e(F,BO+B)
		@V.route('/lights',[j])
		def n(request):
			O='set_to_100';N='set_to_80';M='set_to_60';L='set_to_40';K='set_to_20';J='set_to_0';I='set_to_white';H='set_to_blue';G='set_to_green';F='set_to_red';E=request;global A;B=g;C=E.raw_request.decode(Ah)
			if F in C:B=F;D.fill((255,0,0));D.show()
			elif G in C:B=G;D.fill((0,255,0));D.show()
			elif H in C:B=H;D.fill((0,0,255));D.show()
			elif I in C:B=I;D.fill((255,255,255));D.show()
			elif J in C:B=J;D.brightness=.0;D.show()
			elif K in C:B=K;D.brightness=.2;D.show()
			elif L in C:B=L;D.brightness=.4;D.show()
			elif M in C:B=M;D.brightness=.6;D.show()
			elif N in C:B=N;D.brightness=.8;D.show()
			elif O in C:B=O;D.brightness=1.;D.show()
			return e(E,BO+B)
		@V.route('/update-host-name',[j])
		def n(request):B=request;global A;C=B.json();A[o]=C[AG];E.write_json_file(S,A);AX.hostname=A[o];BG();return e(B,A[o])
		@V.route('/get-host-name',[j])
		def n(request):return e(request,A[o])
		@V.route('/update-volume',[j])
		def n(request):B=request;global A;C=B.json();Aa(C[A2]);return e(B,A[h])
		@V.route('/get-volume',[j])
		def n(request):return e(request,A[h])
		@V.route('/update-light-string',[j])
		def n(request):
			G=' data: ';F='action: ';D=request;global A;B=D.json()
			if B[A2]=='save'or B[A2]=='clear'or B[A2]=='defaults':A[R]=B[AG];O(F+B[A2]+G+A[R]);E.write_json_file(S,A);A6();C(a);return e(D,A[R])
			if A[R]==g:A[R]=B[AG]
			else:A[R]=A[R]+','+B[AG]
			O(F+B[A2]+G+A[R]);E.write_json_file(S,A);A6();C(a);return e(D,A[R])
		@V.route('/get-light-string',[j])
		def n(request):return e(request,A[R])
		@V.route('/get-customers-sound-tracks',[j])
		def n(request):A=E.json_stringify(l);return e(request,A)
	except BH as AY:AB=G;E.log_item(AY)
U('web server')
import utilities as AZ
U('utilities')
def T(seconds):
	D=seconds
	if A[A1]:C=Bd(Bc,D);B.voice[0].level=C
	else:
		try:C=int(A[h])/100
		except:C=.5
		if C<0 or C>1:C=.5
		B.voice[0].level=C;B.voice[1].level=C;L.sleep(D)
def BD():global A;A[R]='bar-10,bolt-4,bar-10,bolt-4,bar-10,bolt-4'
def C0():global A;A[A1]=K;A[o]=BP;A[H]=Al;A[h]='30';BD()
def Aa(action):
	D=action;B=int(A[h])
	if h in D:F=D.split(h);B=int(F[1])
	if D=='lower1':B-=1
	elif D=='raise1':B+=1
	elif D=='lower':
		if B<=10:B-=1
		else:B-=10
	elif D=='raise':
		if B<10:B+=1
		else:B+=10
	if B>100:B=100
	if B<1:B=1
	A[h]=r(B);A[A1]=G;E.write_json_file(S,A);C('/sd/mvc/volume.wav');AC(A[h],G)
def C(file_name):
	if B.voice[0].playing:
		B.voice[0].stop()
		while B.voice[0].playing:T(.02)
	A=b.WaveFile(c(file_name,d));B.voice[0].play(A,loop=G)
	while B.voice[0].playing:C1()
def CP():
	B.voice[0].stop()
	while B.voice[0].playing:0
def C1():
	T(.02);I.update()
	if I.fell:B.voice[0].stop()
def AC(str_to_speak,addLocal):
	for A in str_to_speak:
		if A==' ':A='space'
		if A=='-':A='dash'
		if A=='.':A='dot'
		C(i+A+Q)
	if addLocal:C(BQ);C(BR)
def C2():C('/sd/mvc/sound_selection_menu.wav');z()
def C3():C('/sd/mvc/choose_my_sounds_menu.wav');z()
def z():C('/sd/mvc/press_left_button_right_button.wav')
def C4():C('/sd/mvc/main_menu.wav');z()
def C5():C('/sd/mvc/add_sounds_animate.wav');z()
def A7():C('/sd/mvc/web_menu.wav');z()
def C6():C('/sd/mvc/volume_settings_menu.wav');z()
def C7():C('/sd/mvc/light_string_setup_menu.wav');z()
def C8():C('/sd/mvc/string_instructions.wav')
def BE():C(As)
def BF(play_intro):
	if play_intro:C('/sd/mvc/current_light_settings_are.wav')
	B=A[R].split(',')
	for(D,E)in Ad(B):C('/sd/mvc/position.wav');C(i+r(D+1)+Q);C('/sd/mvc/is.wav');C(i+E+Q)
def C9():
	C('/sd/mvc/no_user_soundtrack_found.wav')
	while K:
		I.update();M.update()
		if I.fell:break
		if M.fell:C(BS);break
def BG():
	C('/sd/mvc/animator_available_on_network.wav');C('/sd/mvc/to_access_type.wav')
	if A[o]==BP:C('/sd/mvc/animator_dash_lightning.wav');C(BQ);C(BR)
	else:AC(A[o],K)
	C('/sd/mvc/in_your_browser.wav')
def X(file_name):
	G='Sound file: ';E='Random sound file: ';C=file_name;O(C);A=C
	if C==Ai:D=P(u)-4;B=F.randint(0,D);A=u[B];O(E+u[B]);O(G+A)
	elif C==Aj:D=P(l)-1;B=F.randint(0,D);A=l[B];O(E+l[B]);O(G+A)
	elif C==Ak:D=P(A5)-4;B=F.randint(0,D);A=A5[B];O(E+A5[B]);O(G+A)
	if m:CA(A)
	elif s in A:Ab(A)
	elif A==An:Ab(A)
	elif A==Am:Ab(A)
	else:CB(A)
def Ab(file_name):
	H=file_name;global m;S=1;U=3;V=s in H
	if V:
		H=H.replace(s,g)
		try:W=E.read_json_file(AH+H+t)
		except:
			C('/sd/mvc/no_timestamp_file_found.wav')
			while K:
				I.update();M.update()
				if I.fell:m=G;return
				if M.fell:m=K;C(Ao);return
	else:W=E.read_json_file(A0+H+t)
	N=W[A9];a=P(N);A=0
	if V:X=b.WaveFile(c(AH+H+Q,d))
	else:X=b.WaveFile(c(A0+H+Q,d))
	B.voice[0].play(X,loop=G);e=L.monotonic();J=0
	while K:
		Y=0;Z=L.monotonic()-e
		if A<P(N)-2:R=N[A+1]-N[A]-.25
		else:R=.25
		if R<0:R=0
		if Z>N[A]-.25:
			O('time elasped: '+r(Z)+' Timestamp: '+r(N[A]));A+=1;J=F.randint(S,U)
			while J==Y:J=F.randint(S,U)
			if J==1:CC(.005,R)
			elif J==2:CE(.01);T(R)
			elif J==3:CD(R)
			Y=J
		if a==A:A=0
		I.update()
		if I.fell:B.voice[0].stop()
		if not B.voice[0].playing:D.fill((0,0,0));D.show();break
		T(.001)
def CA(file_name):
	A=file_name;O('time stamp mode');global m;H=s in A;F=E.read_json_file('/sd/time_stamp_defaults/timestamp_mode.json');F[A9]=[];A=A.replace(s,g)
	if H:I=b.WaveFile(c(AH+A+Q,d))
	else:I=b.WaveFile(c(A0+A+Q,d))
	B.voice[0].play(I,loop=G);N=L.monotonic();T(.1)
	while K:
		J=L.monotonic()-N;M.update()
		if M.fell:F[A9].append(J);O(J)
		if not B.voice[0].playing:
			D.fill((0,0,0));D.show();F[A9].append(5000)
			if H:E.write_json_file(AH+A+t,F)
			else:E.write_json_file(A0+A+t,F)
			break
	m=G;C('/sd/mvc/timestamp_saved.wav');C(Ap);C(BT)
def CB(file_name):
	C=file_name;J=E.read_json_file(A0+C+t);D=J[A9];N=P(D);A=0;R=b.WaveFile(c(A0+C+Q,d));B.voice[0].play(R,loop=G);S=L.monotonic()
	while K:
		T(.1);H=L.monotonic()-S;M.update()
		if M.fell:O(H)
		if H>D[A]-F.uniform(.5,1):A+=1;CF()
		if N==A:A=0
		I.update()
		if I.fell:B.voice[0].stop()
		if not B.voice[0].playing:break
def CQ(ledStrip):A=ledStrip;A.brightness=1.;B=F.randint(0,255);C=F.randint(0,255);D=F.randint(0,255);A.fill((B,C,D));A.show()
def CC(speed,duration):
	G=duration;F=speed;H=L.monotonic()
	for B in Z(0,255,1):
		for A in Z(N):C=A*256//N+B;D[A]=B1(C&255)
		D.show();T(F);E=L.monotonic()-H
		if E>G:return
	for B in reversed(Z(0,255,1)):
		for A in Z(N):C=A*256//N+B;D[A]=B1(C&255)
		D.show();T(F);E=L.monotonic()-H
		if E>G:return
def CD(duration):
	J=L.monotonic();D.brightness=1.;A=[];A.extend(AS);A.extend(AT);B=[];B.extend(AU);B.extend(AV);C=F.randint(0,255);E=F.randint(0,255);G=F.randint(0,255)
	for H in B:D[H]=C,E,G
	C=F.randint(0,255);E=F.randint(0,255);G=F.randint(0,255)
	while K:
		for H in A:I=F.randint(0,110);M=Ac(C-I,0,255);N=Ac(E-I,0,255);O=Ac(G-I,0,255);D[H]=M,N,O;D.show()
		T(F.uniform(.05,.1));P=L.monotonic()-J
		if P>duration:return
def CE(duration):
	G=L.monotonic();D.brightness=1.
	while K:
		for H in Z(0,N):
			I=F.randint(128,255);J=F.randint(128,255);M=F.randint(128,255);A=F.randint(0,2)
			if A==0:B=I;C=0;E=0
			elif A==1:B=0;C=J;E=0
			elif A==2:B=0;C=0;E=M
			D[H]=B,C,E;D.show()
		T(F.uniform(.2,.3));O=L.monotonic()-G
		if O>duration:return
def CF():
	E=[];O=F.randint(-1,P(x)-1)
	if O!=-1:
		for(M,N)in Ad(x):
			if M==O:E.extend(N)
	for(M,N)in Ad(w):
		if M==F.randint(0,P(w)-1):E.extend(N)
	G=F.randint(40,80);H=F.randint(10,25);I=F.randint(0,10);Q=F.randint(5,10);R=150;S=255;T=F.randint(R,S)/255;D.brightness=T;J=0;K=75;U=1;V=50
	for W in Z(0,Q):
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
class CG:
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
	def reset(A):A.firework_color=random_color();A.burst_count=0;A.shower_count=0;A.firework_step_time=L.monotonic()+.05
class J:
	def __init__(A):0
	@k
	def name(self):return g
	def enter(A,machine):0
	def exit(A,machine):0
	def update(B,machine):
		A=machine
		if I.fell:A.paused_state=A.state.name;A.pause();return G
		return K
class CH(J):
	def __init__(A):0
	@k
	def name(self):return W
	def enter(A,machine):C(BT);E.log_item('Entered base state');J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		global q;B=AZ.switch_state(I,M,T,3.)
		if B==BU:
			if q:q=G;C(BK)
			else:q=K;C(BJ)
		elif B==At or q:X(A[H])
		elif B==Au:machine.go_to_state(Af)
class CI(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Af
	def enter(A,machine):E.log_item('Main menu');C4();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(A,machine):
		D=machine;I.update();M.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AN[A.menuIndex]+Q);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>P(AN)-1:A.menuIndex=0
		if M.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				E=AN[A.selectedMenuIndex]
				if E==Av:D.go_to_state(Av)
				elif E==Aw:D.go_to_state(Aw)
				elif E==A8:D.go_to_state(A8)
				elif E==Ax:D.go_to_state(Ax)
				elif E==Ay:D.go_to_state(Ay)
				elif E==AD:D.go_to_state(AD)
				else:C(a);D.go_to_state(W)
class CJ(J):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@k
	def name(self):return Av
	def enter(A,machine):
		O(BV)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:E.log_item(BW);C2()
		J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(C,machine):
		I.update();M.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				D=b.WaveFile(c('/sd/lightning_options_voice_commands/option_'+u[C.optionIndex]+Q,d));B.voice[0].play(D,loop=G);C.currentOption=C.optionIndex;C.optionIndex+=1
				if C.optionIndex>P(u)-1:C.optionIndex=0
				while B.voice[0].playing:0
		if M.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				A[H]=u[C.currentOption];E.write_json_file(S,A);D=b.WaveFile(c(As,d));B.voice[0].play(D,loop=G)
				while B.voice[0].playing:0
			machine.go_to_state(W)
class CK(J):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@k
	def name(self):return Aw
	def enter(A,machine):
		O(BV)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:E.log_item(BW);C3()
		J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		F=machine;I.update();M.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				try:
					L=l[D.optionIndex].replace(s,g);J=r(D.optionIndex+1);C('/sd/mvc/song.wav');AC(J,G);D.currentOption=D.optionIndex;D.optionIndex+=1
					if D.optionIndex>P(l)-1:D.optionIndex=0
					while B.voice[0].playing:0
				except:C9();F.go_to_state(W);return
		if M.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				try:
					A[H]=l[D.currentOption];E.write_json_file(S,A);K=b.WaveFile(c(As,d));B.voice[0].play(K,loop=G)
					while B.voice[0].playing:0
				except:O('no sound track')
			F.go_to_state(W)
class CL(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return A8
	def enter(A,machine):E.log_item(A8);C5();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(A,machine):
		E=machine;global m;I.update();M.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AR[A.menuIndex]+Q);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>P(AR)-1:A.menuIndex=0
		if M.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				D=AR[A.selectedMenuIndex]
				if D=='hear_instructions':C(BS)
				elif D==BL:m=K;C(BM);C(Ao);E.go_to_state(W)
				elif D==BN:m=G;C(Ap)
				else:C(a);E.go_to_state(W)
class CM(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return AD
	def enter(A,machine):E.log_item(Az);C6();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		F=machine;I.update();M.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AQ[D.menuIndex]+Q);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>P(AQ)-1:D.menuIndex=0
		if M.fell:
			H=AQ[D.selectedMenuIndex]
			if H=='volume_level_adjustment':
				C('/sd/mvc/volume_adjustment_menu.wav')
				while K:
					J=AZ.switch_state(I,M,T,3.)
					if J==At:Aa('lower')
					elif J==Au:Aa('raise')
					elif J==BX:E.write_json_file(S,A);C(a);F.go_to_state(W);break
					T(.1)
			elif H==Aq:
				A[A1]=G
				if A[h]==0:A[h]=10
				E.write_json_file(S,A);C(a);F.go_to_state(W)
			elif H==Ar:A[A1]=K;E.write_json_file(S,A);C(a);F.go_to_state(W)
class CN(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Ay
	def enter(A,machine):E.log_item(Az);A7();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		I.update();M.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AO[D.menuIndex]+Q);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>P(AO)-1:D.menuIndex=0
		if M.fell:
			F=AO[D.selectedMenuIndex]
			if F=='web_on':A[Ae]=K;BE();A7()
			elif F=='web_off':A[Ae]=G;BE();A7()
			elif F=='hear_url':AC(A[o],K);A7()
			elif F=='hear_instr_web':C('/sd/mvc/web_instruct.wav');A7()
			else:E.write_json_file(S,A);C(a);machine.go_to_state(W)
class CO(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Ax
	def enter(A,machine):E.log_item(Az);C7();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		J=machine;I.update();M.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AP[D.menuIndex]+Q);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>P(AP)-1:D.menuIndex=0
		if M.fell:
			F=AP[D.selectedMenuIndex]
			if F=='hear_light_setup_instructions':C8()
			elif F=='reset_lights_defaults':BD();C('/sd/mvc/lights_reset_to.wav');BF(G)
			elif F=='hear_current_light_settings':BF(K)
			elif F=='clear_light_string':A[R]=g;C('/sd/mvc/lights_cleared.wav')
			elif F=='add_lights':
				C('/sd/mvc/add_light_menu.wav')
				while K:
					H=AZ.switch_state(I,M,T,3.)
					if H==At:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							D.menuIndex-=1
							if D.menuIndex<0:D.menuIndex=P(v)-1
							D.selectedMenuIndex=D.menuIndex;C(i+v[D.menuIndex]+Q)
					elif H==Au:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							D.menuIndex+=1
							if D.menuIndex>P(v)-1:D.menuIndex=0
							D.selectedMenuIndex=D.menuIndex;C(i+v[D.menuIndex]+Q)
					elif H==BX:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							if A[R]==g:A[R]=v[D.selectedMenuIndex]
							else:A[R]=A[R]+','+v[D.selectedMenuIndex]
							C(i+v[D.selectedMenuIndex]+Q);C('/sd/mvc/added.wav')
					elif H==BU:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:E.write_json_file(S,A);C(a);A6();J.go_to_state(W)
					T(.1)
			else:E.write_json_file(S,A);C(a);A6();J.go_to_state(W)
class CR(J):
	def __init__(A):super().__init__()
	@k
	def name(self):return'example'
	def enter(A,machine):J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(A,machine):J.update(A,machine)
f=CG()
f.add_state(CH())
f.add_state(CI())
f.add_state(CJ())
f.add_state(CK())
f.add_state(CL())
f.add_state(CM())
f.add_state(CN())
f.add_state(CO())
A3.value=K
if AB:
	E.log_item('starting server...')
	try:V.start(r(y.radio.ipv4_address));E.log_item('Listening on http://%s:80'%y.radio.ipv4_address);BG()
	except OSError:L.sleep(5);E.log_item('restarting...');Bb()
f.go_to_state(W)
E.log_item('animator has started...')
U('animations started.')
while K:
	f.update();T(.02)
	if AB:
		try:V.poll()
		except BH as AY:E.log_item(AY);continue