Ay='right_held'
Az='Choose sounds menu'
A_='Select a program option'
B0='left_held'
B1='/sd/menu_voice_commands/animations_are_now_active.wav'
B2='/sd/menu_voice_commands/create_sound_track_files.wav'
B3='/sd/menu_voice_commands/local.wav'
B4='/sd/menu_voice_commands/dot.wav'
B5='animator-christmas-park'
B6='Utility: '
B7='timestamp_mode_off'
B8='/sd/menu_voice_commands/timestamp_mode_on.wav'
B9='timestamp_mode_on'
BA='/sd/menu_voice_commands/continuous_mode_deactivated.wav'
BB='/sd/menu_voice_commands/continuous_mode_activated.wav'
BC='branches'
BD='ornaments'
BE='wav/no_card.wav'
BF=Exception
AO='Set Web Options'
AP='web_options'
AQ='light_string_setup_menu'
AR='choose_my_sounds'
AS='choose_sounds'
AT='right'
AU='left'
AV='/sd/menu_voice_commands/option_selected.wav'
AW='volume_pot_on'
AX='volume_pot_off'
AY='/sd/menu_voice_commands/timestamp_mode_off.wav'
AZ='/sd/menu_voice_commands/timestamp_instructions.wav'
Aa='silent_night'
Ab='random_my'
Ac='random_built_in'
Ad='utf8'
Ae='config wifi imports'
Af='main_menu'
Ag='serve_webpage'
A9='flashTime'
AA='/sd/customers_owned_music/'
AB='text'
AC='random_all'
AD='volume_settings'
A1='/sd/christmas_park_sounds/'
A2='add_sounds_animate'
z='action'
A0=1.
r='volume_pot'
s='.json'
t='customers_owned_music_'
u=str
l='volume'
m='HOST_NAME'
j=property
c='/sd/menu_voice_commands/'
d=''
e='rb'
f=open
Z='/sd/menu_voice_commands/all_changes_complete.wav'
Y=range
W='base_state'
T='/sd/config_christmas_park.json'
U=len
Q='.wav'
P='light_string'
M=print
H=True
G=False
F='option_selected'
import gc,files as E
def V(collection_point):gc.collect();A=gc.mem_free();E.log_item('Point '+collection_point+' Available memory: {} bytes'.format(A))
V('Imports gc, files')
import time as O,audiocore as g,audiomixer as BY,audiobusio as BZ,sdcardio as BG,storage as AE,busio,digitalio as p,board as a,random as K,rtc,microcontroller as Ah
from analogio import AnalogIn as Ba
from adafruit_debouncer import Debouncer as BH
def Bb():Ah.on_next_reset(Ah.RunMode.NORMAL);Ah.reset()
V('imports')
Bc=Ba(a.A0)
def Bd(pin,wait_for):
	B=wait_for/10;A=0
	for C in Y(10):O.sleep(B);A+=1;A=A/10
	return pin.value/65536
A3=p.DigitalInOut(a.GP28)
A3.direction=p.Direction.OUTPUT
A3.value=G
Be=a.GP6
Bf=a.GP7
Ai=p.DigitalInOut(Be)
Ai.direction=p.Direction.INPUT
Ai.pull=p.Pull.UP
I=BH(Ai)
Aj=p.DigitalInOut(Bf)
Aj.direction=p.Direction.INPUT
Aj.pull=p.Pull.UP
L=BH(Aj)
Bg=a.GP18
Bh=a.GP19
Bi=a.GP20
Bj=BZ.I2SOut(bit_clock=Bg,word_select=Bh,data=Bi)
A3.value=H
Bk=a.GP2
Bl=a.GP3
Bm=a.GP4
BI=a.GP5
BJ=busio.SPI(Bk,Bl,Bm)
Bn=2
B=BY.Mixer(voice_count=Bn,sample_rate=22050,channel_count=2,bits_per_sample=16,samples_signed=H,buffer_size=4096)
Bj.play(B)
BK=.2
B.voice[0].level=BK
B.voice[1].level=BK
try:Ak=BG.SDCard(BJ,BI);Al=AE.VfsFat(Ak);AE.mount(Al,'/sd')
except:
	A4=g.WaveFile(f(BE,e));B.voice[0].play(A4,loop=G)
	while B.voice[0].playing:0
	BL=G
	while not BL:
		I.update()
		if I.fell:
			try:
				Ak=BG.SDCard(BJ,BI);Al=AE.VfsFat(Ak);AE.mount(Al,'/sd');BL=H;A4=g.WaveFile(f('/sd/menu_voice_commands/micro_sd_card_success.wav',e));B.voice[0].play(A4,loop=G)
				while B.voice[0].playing:0
			except:
				A4=g.WaveFile(f(BE,e));B.voice[0].play(A4,loop=G)
				while B.voice[0].playing:0
A3.value=G
Bo=rtc.RTC()
Bo.datetime=O.struct_time((2019,5,29,15,14,15,0,-1,-1))
A=E.read_json_file(T)
v=A['options']
n=E.return_directory(t,'/sd/customers_owned_music',Q)
A5=[]
A5.extend(n)
A5.extend(v)
Bp=E.return_directory(d,'/sd/time_stamp_defaults',s)
AF=A[Ag]
Bq=E.read_json_file('/sd/menu_voice_commands/main_menu.json')
Am=Bq[Af]
Br=E.read_json_file('/sd/menu_voice_commands/web_menu.json')
An=Br['web_menu']
Bs=E.read_json_file('/sd/menu_voice_commands/light_string_menu.json')
Ao=Bs['light_string_menu']
Bt=E.read_json_file('/sd/menu_voice_commands/light_options.json')
w=Bt['light_options']
Bu=E.read_json_file('/sd/menu_voice_commands/volume_settings.json')
Ap=Bu[AD]
Bv=E.read_json_file('/sd/menu_voice_commands/add_sounds_animate.json')
Aq=Bv[A2]
V('config setup')
q=G
b=G
import neopixel as BM
from rainbowio import colorwheel as BN
AG=[]
AH=[]
AI=[]
AJ=[]
AK=[]
AL=[]
AM=[]
N=0
D=BM.NeoPixel(a.GP10,N)
def Ar(part):
	C=part;B=[]
	for E in AG:
		for A in E:D=A;break
		if C==BD:
			for A in Y(0,7):B.append(A+D)
		if C=='star':
			for A in Y(7,14):B.append(A+D)
		if C==BC:
			for A in Y(14,21):B.append(A+D)
	return B
def BO(part):
	B=[]
	for D in AH:
		for A in D:C=A;break
		if part=='end':
			for A in Y(0,2):B.append(A+C)
		if part=='start':
			for A in Y(2,4):B.append(A+C)
	return B
def A6():D.show();O.sleep(.3);D.fill((0,0,0));D.show()
def Bw():
	global AI,AJ,AK,AL,AM;AI=Ar(BD);AJ=Ar('star');AK=Ar(BC);AL=BO('start');AM=BO('end');A=0
	for B in AL:
		D[B]=50,50,50;A+=1
		if A>1:A6();A=0
	for B in AM:
		D[B]=50,50,50;A+=1
		if A>1:A6();A=0
	A=0
	for B in AI:
		D[B]=50,50,50;A+=1
		if A>6:A6();A=0
	for B in AJ:
		D[B]=50,50,50;A+=1
		if A>6:A6();A=0
	for B in AK:
		D[B]=50,50,50;A+=1
		if A>6:A6();A=0
def A7():
	global AG,AH,N,D,N;AG=[];AH=[];N=0;F=A[P].split(',')
	for H in F:
		C=H.split('-')
		if U(C)==2:
			E,B=C;B=int(B)
			if E=='grandtree':I=list(Y(N,N+B));AG.append(I);N+=B
			elif E=='cane':J=list(Y(N,N+B));AH.append(J);N+=B
	M('Number of pixels total: ',N);D.deinit();V('Deinit ledStrip');D=BM.NeoPixel(a.GP10,N);D.auto_write=G;D.brightness=A0;Bw()
A7()
V('Neopixels setup')
if AF:
	import socketpool as Bx,mdns;V(Ae);import wifi as x;V(Ae);from adafruit_httpserver import Server,Request,FileResponse as As,Response as h,POST as k;V(Ae);E.log_item('Connecting to WiFi');BP='jimmytrainsguest';BQ=d
	try:BR=E.read_json_file('/sd/env.json');BP=BR['WIFI_SSID'];BQ=BR['WIFI_PASSWORD'];V('wifi env');M('Using env ssid and password')
	except:M('Using default ssid and password')
	try:
		x.radio.connect(BP,BQ);V('wifi connect');At=mdns.Server(x.radio);At.hostname=A[m];At.advertise_service(service_type='_http',protocol='_tcp',port=80);By=[hex(A)for A in x.radio.mac_address];E.log_item('My MAC addr:'+u(By));Bz=u(x.radio.ipv4_address);E.log_item('My IP address is'+Bz);E.log_item('Connected to WiFi');B_=Bx.SocketPool(x.radio);X=Server(B_,'/static',debug=H);V('wifi server')
		@X.route('/')
		def BS(request):V('Home page.');return As(request,'index.html','/')
		@X.route('/mui.min.css')
		def BS(request):return As(request,'mui.min.css','/')
		@X.route('/mui.min.js')
		def BS(request):return As(request,'mui.min.js','/')
		@X.route('/animation',[k])
		def o(request):
			D='auld_lang_syne_jazzy_version';I='joy_to_the_world';J='away_in_a_manger';K='jingle_bells_orchestra';L='the_wassail_song';M='deck_the_halls_jazzy_version';N='dance_of_the_sugar_plum_fairy';O='carol_of_the_bells';P='joyful_snowman';Q='angels_we_have_heard_on_high';R='we_wish_you_a_merry_christmas';T=request;global A;global q;global b;B=T.raw_request.decode(Ad)
			if Ac in B:A[F]=Ac;S(A[F])
			elif Ab in B:A[F]=Ab;S(A[F])
			elif AC in B:A[F]=AC;S(A[F])
			elif R in B:A[F]=R;S(A[F])
			elif Q in B:A[F]=Q;S(A[F])
			elif P in B:A[F]=P;S(A[F])
			elif O in B:A[F]=O;S(A[F])
			elif N in B:A[F]=N;S(A[F])
			elif M in B:A[F]=M;S(A[F])
			elif L in B:A[F]=L;S(A[F])
			elif K in B:A[F]=K;S(A[F])
			elif J in B:A[F]=J;S(A[F])
			elif I in B:A[F]=I;S(A[F])
			elif Aa in B:A[F]=Aa;S(A[F])
			elif D in B:A[F]=D;S(A[F])
			elif t in B:
				for U in n:
					if U in B:A[F]=U;S(A[F]);break
			elif'cont_mode_on'in B:q=H;C(BB)
			elif'cont_mode_off'in B:q=G;C(BA)
			elif B9 in B:b=H;C(B8);C(AZ)
			elif B7 in B:b=G;C(AY)
			elif'reset_animation_timing_to_defaults'in B:
				for V in Bp:W=E.read_json_file('/sd/time_stamp_defaults/'+V+s);E.write_json_file(A1+V+s,W)
			return h(T,'Animation '+A[F]+' started.')
		@X.route('/utilities',[k])
		def o(request):
			F='reset_to_defaults';I='speaker_test';J=request;global A;B=d;D=J.raw_request.decode(Ad)
			if I in D:B=I;C('/sd/menu_voice_commands/left_speaker_right_speaker.wav')
			elif AX in D:B=AX;A[r]=G;E.write_json_file(T,A);C(Z)
			elif AW in D:B=AW;A[r]=H;E.write_json_file(T,A);C(Z)
			elif F in D:B=F;C0();E.write_json_file(T,A);C(Z);i.go_to_state(W)
			return h(J,B6+B)
		@X.route('/lights',[k])
		def o(request):
			E='set_to_100';F='set_to_80';G='set_to_60';H='set_to_40';I='set_to_20';J='set_to_0';K='set_to_white';L='set_to_blue';M='set_to_green';N='set_to_red';O=request;global A;B=d;C=O.raw_request.decode(Ad)
			if N in C:B=N;D.fill((255,0,0));D.show()
			elif M in C:B=M;D.fill((0,255,0));D.show()
			elif L in C:B=L;D.fill((0,0,255));D.show()
			elif K in C:B=K;D.fill((255,255,255));D.show()
			elif J in C:B=J;D.brightness=.0;D.show()
			elif I in C:B=I;D.brightness=.2;D.show()
			elif H in C:B=H;D.brightness=.4;D.show()
			elif G in C:B=G;D.brightness=.6;D.show()
			elif F in C:B=F;D.brightness=.8;D.show()
			elif E in C:B=E;D.brightness=A0;D.show()
			return h(O,B6+B)
		@X.route('/update-host-name',[k])
		def o(request):B=request;global A;C=B.json();A[m]=C[AB];E.write_json_file(T,A);At.hostname=A[m];BX();return h(B,A[m])
		@X.route('/get-host-name',[k])
		def o(request):return h(request,A[m])
		@X.route('/update-volume',[k])
		def o(request):B=request;global A;C=B.json();Aw(C[z]);return h(B,A[l])
		@X.route('/get-volume',[k])
		def o(request):return h(request,A[l])
		@X.route('/update-light-string',[k])
		def o(request):
			F=' data: ';G='action: ';D=request;global A;B=D.json()
			if B[z]=='save'or B[z]=='clear'or B[z]=='defaults':A[P]=B[AB];M(G+B[z]+F+A[P]);E.write_json_file(T,A);A7();C(Z);return h(D,A[P])
			if A[P]==d:A[P]=B[AB]
			else:A[P]=A[P]+','+B[AB]
			M(G+B[z]+F+A[P]);E.write_json_file(T,A);A7();C(Z);return h(D,A[P])
		@X.route('/get-light-string',[k])
		def o(request):return h(request,A[P])
		@X.route('/get-customers-sound-tracks',[k])
		def o(request):A=E.json_stringify(n);return h(request,A)
	except BF as Au:AF=G;E.log_item(Au)
V('web server')
import utilities as Av
V('utilities')
def R(seconds):
	D=seconds
	if A[r]:C=Bd(Bc,D);B.voice[0].level=C
	else:
		try:C=int(A[l])/100
		except:C=.5
		if C<0 or C>1:C=.5
		B.voice[0].level=C;B.voice[1].level=C;O.sleep(D)
def C0():global A;A[r]=H;A[m]=B5;A[F]=AC;A[l]=30;BT()
def BT():global A;A[P]='cane-4,cane-4,cane-4,cane-4,cane-4,cane-4,grandtree-21'
def Aw(action):
	D=action;B=int(A[l])
	if D=='lower1':B-=1
	if D=='lower10':B-=10
	if D=='raise10':B+=10
	if D=='raise1':B+=1
	if D=='lower':
		if B<10:B-=1
		else:B-=10
	if D=='raise':
		if B<10:B+=1
		else:B+=10
	if B>100:B=100
	if B<1:B=1
	A[l]=u(B);A[r]=G;E.write_json_file(T,A);C('/sd/menu_voice_commands/volume.wav');AN(A[l],G)
def C(file_name):
	if B.voice[0].playing:
		B.voice[0].stop()
		while B.voice[0].playing:R(.02)
	A=g.WaveFile(f(file_name,e));B.voice[0].play(A,loop=G)
	while B.voice[0].playing:C1()
def CO():
	B.voice[0].stop()
	while B.voice[0].playing:0
def C1():
	R(.02);I.update()
	if I.fell:B.voice[0].stop()
def AN(str_to_speak,addLocal):
	for A in str_to_speak:
		try:
			if A==' ':A='space'
			if A=='-':A='dash'
			if A=='.':A='dot'
			C(c+A+Q)
		except:M('invalid character in string to speak')
	if addLocal:C(B4);C(B3)
def C2():C('/sd/menu_voice_commands/sound_selection_menu.wav');y()
def C3():C('/sd/menu_voice_commands/choose_my_sounds_menu.wav');y()
def y():C('/sd/menu_voice_commands/press_left_button_right_button.wav')
def C4():C('/sd/menu_voice_commands/main_menu.wav');y()
def C5():C('/sd/menu_voice_commands/add_sounds_animate.wav');y()
def A8():C('/sd/menu_voice_commands/web_menu.wav');y()
def C6():C('/sd/menu_voice_commands/volume_settings_menu.wav');y()
def C7():C('/sd/menu_voice_commands/light_string_setup_menu.wav');y()
def C8():C('/sd/menu_voice_commands/park_string_instructions.wav')
def BU():C(AV)
def BV(play_intro):
	if play_intro:C('/sd/menu_voice_commands/current_light_settings_are.wav')
	B=A[P].split(',')
	for(D,E)in enumerate(B):C('/sd/menu_voice_commands/position.wav');C(c+u(D+1)+Q);C('/sd/menu_voice_commands/is.wav');C(c+E+Q)
def C9():
	C('/sd/menu_voice_commands/no_user_soundtrack_found.wav')
	while H:
		I.update();L.update()
		if I.fell:break
		if L.fell:C(B2);break
def S(file_name):
	E='Sound file: ';F='Random sound file: ';C=file_name;M(C);A=C
	if C==Ac:D=U(v)-4;B=K.randint(0,D);A=v[B];M(F+v[B]);M(E+A)
	elif C==Ab:D=U(n)-1;B=K.randint(0,D);A=n[B];M(F+n[B]);M(E+A)
	elif C==AC:D=U(A5)-4;B=K.randint(0,D);A=A5[B];M(F+A5[B]);M(E+A)
	if b:CB(A)
	else:CA(A)
	V('animation finished')
def CA(file_name):
	D=file_name;global b;P=1;S=3
	if D==Aa:P=3;S=3
	T=t in D
	if T:
		D=D.replace(t,d)
		try:V=E.read_json_file(AA+D+s)
		except:
			C('/sd/menu_voice_commands/no_timestamp_file_found.wav')
			while H:
				I.update();L.update()
				if I.fell:b=G;return
				if L.fell:b=H;C(AZ);return
	else:V=E.read_json_file(A1+D+s)
	N=V[A9];Z=U(N);F=0
	if T:W=g.WaveFile(f(AA+D+Q,e))
	else:W=g.WaveFile(f(A1+D+Q,e))
	B.voice[0].play(W,loop=G);a=O.monotonic();A=0
	while H:
		X=0;Y=O.monotonic()-a
		if F<U(N)-2:J=N[F+1]-N[F]-.25
		else:J=.25
		if J<0:J=0
		if Y>N[F]-.25:
			M('time elasped: '+u(Y)+' Timestamp: '+u(N[F]));F+=1;A=K.randint(P,S)
			while A==X:M('regenerating random selection');A=K.randint(P,S)
			if A==1:CC(.005,J)
			elif A==2:BW(.01);R(J)
			elif A==3:CD(J)
			elif A==4:CE(J)
			elif A==5:BW(J)
			X=A
		if Z==F:F=0
		I.update()
		if I.fell:B.voice[0].stop()
		if not B.voice[0].playing:break
		R(.001)
def CB(file_name):
	A=file_name;M('time stamp mode');global b;I=t in A;F=E.read_json_file('/sd/time_stamp_defaults/timestamp_mode.json');F[A9]=[];A=A.replace(t,d)
	if I:J=g.WaveFile(f(AA+A+Q,e))
	else:J=g.WaveFile(f(A1+A+Q,e))
	B.voice[0].play(J,loop=G);N=O.monotonic();R(.1)
	while H:
		K=O.monotonic()-N;L.update()
		if L.fell:F[A9].append(K);M(K)
		if not B.voice[0].playing:
			D.fill((0,0,0));D.show();F[A9].append(5000)
			if I:E.write_json_file(AA+A+s,F)
			else:E.write_json_file(A1+A+s,F)
			break
	b=G;C('/sd/menu_voice_commands/timestamp_saved.wav');C(AY);C(B1)
def CP():D.brightness=A0;A=K.randint(0,255);B=K.randint(0,255);C=K.randint(0,255);D.fill((A,B,C));D.show()
def CC(speed,duration):
	F=duration;G=speed;H=O.monotonic()
	for B in Y(0,255,1):
		for A in Y(N):C=A*256//N+B;D[A]=BN(C&255)
		D.show();R(G);E=O.monotonic()-H
		if E>F:return
	for B in reversed(Y(0,255,1)):
		for A in Y(N):C=A*256//N+B;D[A]=BN(C&255)
		D.show();R(G);E=O.monotonic()-H
		if E>F:return
def CD(duration):
	G=O.monotonic();D.brightness=A0;A=[];A.extend(AI);A.extend(AL);A.extend(AM);E=[];E.extend(AJ)
	for B in E:D[B]=255,255,255
	F=[];F.extend(AK)
	for B in F:D[B]=50,50,50
	I=K.randint(0,255);J=K.randint(0,255);L=K.randint(0,255);M(U(A))
	while H:
		for B in A:C=K.randint(0,110);N=Ax(I-C,0,255);P=Ax(J-C,0,255);Q=Ax(L-C,0,255);D[B]=N,P,Q;D.show()
		R(K.uniform(.05,.1));S=O.monotonic()-G
		if S>duration:return
def CE(duration):
	F=O.monotonic();D.brightness=A0
	while H:
		for G in Y(0,N):
			I=K.randint(0,255);J=K.randint(0,255);L=K.randint(0,255);A=K.randint(0,1)
			if A==0:B=I;C=0;E=0
			elif A==1:B=0;C=J;E=0
			elif A==2:B=0;C=0;E=L
			D[G]=B,C,E;D.show()
		R(K.uniform(.2,.3));M=O.monotonic()-F
		if M>duration:return
def Ax(my_color,lower,upper):
	B=upper;C=lower;A=my_color
	if A<C:A=C
	if A>B:A=B
	return A
def BW(duration):
	F=O.monotonic();D.brightness=A0
	while H:
		for G in Y(0,N):
			I=K.randint(128,255);J=K.randint(128,255);L=K.randint(128,255);A=K.randint(0,2)
			if A==0:B=I;C=0;E=0
			elif A==1:B=0;C=J;E=0
			elif A==2:B=0;C=0;E=L
			D[G]=B,C,E;D.show()
		R(K.uniform(.2,.3));M=O.monotonic()-F
		if M>duration:return
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
	def reset(A):A.firework_color=random_color();A.burst_count=0;A.shower_count=0;A.firework_step_time=O.monotonic()+.05
class J:
	def __init__(A):0
	@j
	def name(self):return d
	def enter(A,machine):0
	def exit(A,machine):0
	def update(B,machine):
		A=machine
		if I.fell:A.paused_state=A.state.name;A.pause();return G
		return H
class CG(J):
	def __init__(A):0
	@j
	def name(self):return W
	def enter(A,machine):C(B1);E.log_item('Entered base state');J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		global q;B=Av.switch_state(I,L,R,3.)
		if B==B0:
			if q:q=G;C(BA)
			else:q=H;C(BB)
		elif B==AU or q:S(A[F])
		elif B==AT:machine.go_to_state(Af)
class CH(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@j
	def name(self):return Af
	def enter(A,machine):E.log_item('Main menu');C4();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(A,machine):
		D=machine;I.update();L.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(c+Am[A.menuIndex]+Q);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>U(Am)-1:A.menuIndex=0
		if L.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				E=Am[A.selectedMenuIndex]
				if E==AS:D.go_to_state(AS)
				elif E==AR:D.go_to_state(AR)
				elif E==AQ:D.go_to_state(AQ)
				elif E==AP:D.go_to_state(AP)
				elif E==AD:D.go_to_state(AD)
				elif E==A2:D.go_to_state(A2)
				else:C(Z);D.go_to_state(W)
class CI(J):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@j
	def name(self):return AS
	def enter(A,machine):
		M(A_)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:E.log_item(Az);C2()
		J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(C,machine):
		I.update();L.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				D=g.WaveFile(f('/sd/christmas_park_options_voice_commands/option_'+v[C.optionIndex]+Q,e));B.voice[0].play(D,loop=G);C.currentOption=C.optionIndex;C.optionIndex+=1
				if C.optionIndex>U(v)-1:C.optionIndex=0
				while B.voice[0].playing:0
		if L.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				A[F]=v[C.currentOption];E.write_json_file(T,A);D=g.WaveFile(f(AV,e));B.voice[0].play(D,loop=G)
				while B.voice[0].playing:0
			machine.go_to_state(W)
class CJ(J):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@j
	def name(self):return AR
	def enter(A,machine):
		M(A_)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:E.log_item(Az);C3()
		J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(C,machine):
		D=machine;I.update();L.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				try:
					H=n[C.optionIndex].replace(t,d);AN(H,G);C.currentOption=C.optionIndex;C.optionIndex+=1
					if C.optionIndex>U(n)-1:C.optionIndex=0
					while B.voice[0].playing:0
				except:C9();D.go_to_state(W);return
		if L.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				try:
					A[F]=n[C.currentOption];E.write_json_file(T,A);J=g.WaveFile(f(AV,e));B.voice[0].play(J,loop=G)
					while B.voice[0].playing:0
				except:M('no sound track')
			D.go_to_state(W)
class CK(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@j
	def name(self):return A2
	def enter(A,machine):E.log_item(A2);C5();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(A,machine):
		E=machine;global b;I.update();L.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(c+Aq[A.menuIndex]+Q);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>U(Aq)-1:A.menuIndex=0
		if L.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				D=Aq[A.selectedMenuIndex]
				if D=='hear_instructions':C(B2)
				elif D==B9:b=H;C(B8);C(AZ);E.go_to_state(W)
				elif D==B7:b=G;C(AY)
				else:C(Z);E.go_to_state(W)
class CL(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@j
	def name(self):return AD
	def enter(A,machine):E.log_item(AO);C6();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		F=machine;I.update();L.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(c+Ap[D.menuIndex]+Q);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>U(Ap)-1:D.menuIndex=0
		if L.fell:
			J=Ap[D.selectedMenuIndex]
			if J=='volume_level_adjustment':
				C('/sd/menu_voice_commands/volume_adjustment_menu.wav')
				while H:
					K=Av.switch_state(I,L,R,3.)
					if K==AU:Aw('lower')
					elif K==AT:Aw('raise')
					elif K==Ay:E.write_json_file(T,A);C(Z);F.go_to_state(W);break
					R(.1)
			elif J==AX:
				A[r]=G
				if A[l]==0:A[l]=10
				E.write_json_file(T,A);C(Z);F.go_to_state(W)
			elif J==AW:A[r]=H;E.write_json_file(T,A);C(Z);F.go_to_state(W)
class CM(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@j
	def name(self):return AP
	def enter(A,machine):E.log_item(AO);A8();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		I.update();L.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(c+An[D.menuIndex]+Q);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>U(An)-1:D.menuIndex=0
		if L.fell:
			F=An[D.selectedMenuIndex]
			if F=='web_on':A[Ag]=H;BU();A8()
			elif F=='web_off':A[Ag]=G;BU();A8()
			elif F=='hear_url':AN(A[m],H);A8()
			elif F=='hear_instr_web':C('/sd/menu_voice_commands/web_instruct.wav');A8()
			else:E.write_json_file(T,A);C(Z);machine.go_to_state(W)
class CN(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0;A.lightIndex=0;A.selectedLightIndex=0
	@j
	def name(self):return AQ
	def enter(A,machine):E.log_item(AO);C7();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		K=machine;I.update();L.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(c+Ao[D.menuIndex]+Q);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>U(Ao)-1:D.menuIndex=0
		if L.fell:
			F=Ao[D.selectedMenuIndex]
			if F=='hear_light_setup_instructions':C8()
			elif F=='reset_lights_defaults':BT();C('/sd/menu_voice_commands/lights_reset_to.wav');BV(G)
			elif F=='hear_current_light_settings':BV(H)
			elif F=='clear_light_string':A[P]=d;C('/sd/menu_voice_commands/lights_cleared.wav')
			elif F=='add_lights':
				C('/sd/menu_voice_commands/add_light_menu.wav');M=H
				while M:
					J=Av.switch_state(I,L,R,3.)
					if J==AU:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							D.lightIndex-=1
							if D.lightIndex<0:D.lightIndex=U(w)-1
							D.selectedLightIndex=D.lightIndex;C(c+w[D.lightIndex]+Q)
					elif J==AT:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							D.lightIndex+=1
							if D.lightIndex>U(w)-1:D.lightIndex=0
							D.selectedLightIndex=D.lightIndex;C(c+w[D.lightIndex]+Q)
					elif J==Ay:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							if A[P]==d:A[P]=w[D.selectedLightIndex]
							else:A[P]=A[P]+','+w[D.selectedLightIndex]
							C(c+w[D.selectedLightIndex]+Q);C('/sd/menu_voice_commands/added.wav')
					elif J==B0:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:E.write_json_file(T,A);C(Z);A7();M=G;K.go_to_state(W)
					R(.1)
			else:E.write_json_file(T,A);C(Z);A7();K.go_to_state(W)
class CQ(J):
	def __init__(A):super().__init__()
	@j
	def name(self):return'example'
	def enter(A,machine):J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(A,machine):J.update(A,machine)
i=CF()
i.add_state(CG())
i.add_state(CH())
i.add_state(CI())
i.add_state(CJ())
i.add_state(CK())
i.add_state(CL())
i.add_state(CM())
i.add_state(CN())
A3.value=H
R(.5)
def BX():
	C('/sd/menu_voice_commands/animator_available_on_network.wav');C('/sd/menu_voice_commands/to_access_type.wav')
	if A[m]==B5:C('/sd/menu_voice_commands/animator_dash_christmas_dash_park.wav');C(B4);C(B3)
	else:AN(A[m],H)
	C('/sd/menu_voice_commands/in_your_browser.wav')
if AF:
	E.log_item('starting server...')
	try:X.start(u(x.radio.ipv4_address));E.log_item('Listening on http://%s:80'%x.radio.ipv4_address);BX()
	except OSError:O.sleep(5);E.log_item('restarting...');Bb()
i.go_to_state(W)
E.log_item('animator has started...')
V('animations started.')
while H:
	i.update();R(.02)
	if AF:
		try:X.poll()
		except BF as Au:E.log_item(Au);continue