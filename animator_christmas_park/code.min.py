BX='right_held'
BW='Choose sounds menu'
BV='Select a program option'
BU='left_held'
BT='/sd/menu_voice_commands/animations_are_now_active.wav'
BS='/sd/menu_voice_commands/no_timestamp_file_found.wav'
BR='/sd/menu_voice_commands/create_sound_track_files.wav'
BQ='/sd/menu_voice_commands/local.wav'
BP='/sd/menu_voice_commands/dot.wav'
BO='animator-christmas-park'
BN='Utility: '
BM='timestamp_mode_off'
BL='/sd/menu_voice_commands/timestamp_mode_on.wav'
BK='timestamp_mode_on'
BJ='/sd/menu_voice_commands/continuous_mode_deactivated.wav'
BI='/sd/menu_voice_commands/continuous_mode_activated.wav'
BH='branches'
BG='ornaments'
BF='wav/no_card.wav'
BE=Exception
Aw='Set Web Options'
Av='web_options'
Au='light_string_setup_menu'
At='choose_my_sounds'
As='choose_sounds'
Ar='right'
Aq='left'
Ap='/sd/menu_voice_commands/option_selected.wav'
Ao='volume_pot_on'
An='volume_pot_off'
Am='/sd/menu_voice_commands/timestamp_mode_off.wav'
Al='silent_night'
Ak='we_wish_you_a_merry_christmas'
Aj='utf8'
Ai='config wifi imports'
Ah='main_menu'
Ag='serve_webpage'
AO='flashTime'
AN='/sd/customers_owned_music/'
AM='text'
AL='/sd/menu_voice_commands/timestamp_instructions.wav'
AK='volume_settings'
A8='/sd/christmas_park_sounds/'
A7='add_sounds_animate'
A6='random'
A0='action'
z=1.
w='volume_pot'
v='.json'
u='customers_owned_music_'
t=str
n='volume'
m='HOST_NAME'
k=property
i='/sd/menu_voice_commands/'
h=''
g='rb'
f=open
a='/sd/menu_voice_commands/all_changes_complete.wav'
Y=len
X=range
W='base_state'
T='/sd/config_christmas_park.json'
R='.wav'
Q=print
O='light_string'
I=True
G=False
F='option_selected'
import gc,files as E
def S(collection_point):gc.collect();A=gc.mem_free();E.log_item('Point '+collection_point+' Available memory: {} bytes'.format(A))
S('Imports gc, files')
import time as N,audiocore as c,audiomixer as BY,audiobusio as BZ,sdcardio as Ax,storage as A9,busio,digitalio as o,board as Z,random as L,rtc,microcontroller as AP
from analogio import AnalogIn as Ba
from adafruit_debouncer import Debouncer as Ay
def Bb():AP.on_next_reset(AP.RunMode.NORMAL);AP.reset()
S('imports')
Bc=Ba(Z.A0)
def Bd(pin,wait_for):
	B=wait_for/10;A=0
	for C in X(10):N.sleep(B);A+=1;A=A/10
	return pin.value/65536
A1=o.DigitalInOut(Z.GP28)
A1.direction=o.Direction.OUTPUT
A1.value=G
Be=Z.GP6
Bf=Z.GP7
AQ=o.DigitalInOut(Be)
AQ.direction=o.Direction.INPUT
AQ.pull=o.Pull.UP
H=Ay(AQ)
AR=o.DigitalInOut(Bf)
AR.direction=o.Direction.INPUT
AR.pull=o.Pull.UP
K=Ay(AR)
Bg=Z.GP18
Bh=Z.GP19
Bi=Z.GP20
Bj=BZ.I2SOut(bit_clock=Bg,word_select=Bh,data=Bi)
A1.value=I
Bk=Z.GP2
Bl=Z.GP3
Bm=Z.GP4
Az=Z.GP5
A_=busio.SPI(Bk,Bl,Bm)
Bn=2
B=BY.Mixer(voice_count=Bn,sample_rate=22050,channel_count=2,bits_per_sample=16,samples_signed=I,buffer_size=4096)
Bj.play(B)
B0=.2
B.voice[0].level=B0
B.voice[1].level=B0
try:AS=Ax.SDCard(A_,Az);AT=A9.VfsFat(AS);A9.mount(AT,'/sd')
except:
	A2=c.WaveFile(f(BF,g));B.voice[0].play(A2,loop=G)
	while B.voice[0].playing:0
	B1=G
	while not B1:
		H.update()
		if H.fell:
			try:
				AS=Ax.SDCard(A_,Az);AT=A9.VfsFat(AS);A9.mount(AT,'/sd');B1=I;A2=c.WaveFile(f('/sd/menu_voice_commands/micro_sd_card_success.wav',g));B.voice[0].play(A2,loop=G)
				while B.voice[0].playing:0
			except:
				A2=c.WaveFile(f(BF,g));B.voice[0].play(A2,loop=G)
				while B.voice[0].playing:0
A1.value=G
Bo=rtc.RTC()
Bo.datetime=N.struct_time((2019,5,29,15,14,15,0,-1,-1))
A=E.read_json_file(T)
AA=A['options']
x=E.return_directory(u,'/sd/customers_owned_music',R)
y=[]
y.extend(AA)
y.extend(x)
y.remove(A6)
Bp=E.return_directory(h,'/sd/time_stamp_defaults',v)
AB=A[Ag]
Bq=E.read_json_file('/sd/menu_voice_commands/main_menu.json')
AU=Bq[Ah]
Br=E.read_json_file('/sd/menu_voice_commands/web_menu.json')
AV=Br['web_menu']
Bs=E.read_json_file('/sd/menu_voice_commands/light_string_menu.json')
AW=Bs['light_string_menu']
Bt=E.read_json_file('/sd/menu_voice_commands/light_options.json')
q=Bt['light_options']
Bu=E.read_json_file('/sd/menu_voice_commands/volume_settings.json')
AX=Bu[AK]
Bv=E.read_json_file('/sd/menu_voice_commands/add_sounds_animate.json')
AY=Bv[A7]
S('config setup')
p=G
b=G
import neopixel as B2
from rainbowio import colorwheel as B3
AC=[]
AD=[]
AE=[]
AF=[]
AG=[]
AH=[]
AI=[]
M=0
D=B2.NeoPixel(Z.GP10,M)
def AZ(part):
	C=part;B=[]
	for E in AC:
		for A in E:D=A;break
		if C==BG:
			for A in X(0,7):B.append(A+D)
		if C=='star':
			for A in X(7,14):B.append(A+D)
		if C==BH:
			for A in X(14,21):B.append(A+D)
	return B
def B4(part):
	B=[]
	for D in AD:
		for A in D:C=A;break
		if part=='end':
			for A in X(0,2):B.append(A+C)
		if part=='start':
			for A in X(2,4):B.append(A+C)
	return B
def A3():D.show();N.sleep(.3);D.fill((0,0,0));D.show()
def Bw():
	global AE,AF,AG,AH,AI;AE=AZ(BG);AF=AZ('star');AG=AZ(BH);AH=B4('start');AI=B4('end');A=0
	for B in AH:
		D[B]=50,50,50;A+=1
		if A>1:A3();A=0
	for B in AI:
		D[B]=50,50,50;A+=1
		if A>1:A3();A=0
	A=0
	for B in AE:
		D[B]=50,50,50;A+=1
		if A>6:A3();A=0
	for B in AF:
		D[B]=50,50,50;A+=1
		if A>6:A3();A=0
	for B in AG:
		D[B]=50,50,50;A+=1
		if A>6:A3();A=0
def A4():
	global AC,AD,M,D,M;AC=[];AD=[];M=0;F=A[O].split(',')
	for H in F:
		C=H.split('-')
		if Y(C)==2:
			E,B=C;B=int(B)
			if E=='grandtree':I=list(X(M,M+B));AC.append(I);M+=B
			elif E=='cane':J=list(X(M,M+B));AD.append(J);M+=B
	Q('Number of pixels total: ',M);D.deinit();S('Deinit ledStrip');D=B2.NeoPixel(Z.GP10,M);D.auto_write=G;D.brightness=z;Bw()
A4()
S('Neopixels setup')
if AB:
	import socketpool as Bx,mdns;S(Ai);import wifi as r;S(Ai);from adafruit_httpserver import Server,Request,FileResponse as Aa,Response as d,POST as j;S(Ai);E.log_item('Connecting to WiFi');B5='jimmytrainsguest';B6=h
	try:B7=E.read_json_file('/sd/env.json');B5=B7['WIFI_SSID'];B6=B7['WIFI_PASSWORD'];S('wifi env');Q('Using env ssid and password')
	except:Q('Using default ssid and password')
	try:
		r.radio.connect(B5,B6);S('wifi connect');Ab=mdns.Server(r.radio);Ab.hostname=A[m];Ab.advertise_service(service_type='_http',protocol='_tcp',port=80);By=[hex(A)for A in r.radio.mac_address];E.log_item('My MAC addr:'+t(By));Bz=t(r.radio.ipv4_address);E.log_item('My IP address is'+Bz);E.log_item('Connected to WiFi');B_=Bx.SocketPool(r.radio);U=Server(B_,'/static',debug=I);S('wifi server')
		@U.route('/')
		def B8(request):S('Home page.');return Aa(request,'index.html','/')
		@U.route('/mui.min.css')
		def B8(request):return Aa(request,'mui.min.css','/')
		@U.route('/mui.min.js')
		def B8(request):return Aa(request,'mui.min.js','/')
		@U.route('/animation',[j])
		def l(request):
			T='auld_lang_syne_jazzy_version';S='joy_to_the_world';R='away_in_a_manger';Q='jingle_bells_orchestra';P='the_wassail_song';O='deck_the_halls_jazzy_version';N='dance_of_the_sugar_plum_fairy';M='carol_of_the_bells';L='joyful_snowman';K='angels_we_have_heard_on_high';D=request;global A;global p;global b;B=D.raw_request.decode(Aj)
			if A6 in B:A[F]=A6;V(A[F])
			elif Ak in B:A[F]=Ak;V(A[F])
			elif K in B:A[F]=K;V(A[F])
			elif L in B:A[F]=L;V(A[F])
			elif M in B:A[F]=M;V(A[F])
			elif N in B:A[F]=N;V(A[F])
			elif O in B:A[F]=O;V(A[F])
			elif P in B:A[F]=P;V(A[F])
			elif Q in B:A[F]=Q;V(A[F])
			elif R in B:A[F]=R;V(A[F])
			elif S in B:A[F]=S;V(A[F])
			elif Al in B:A[F]=Al;V(A[F])
			elif T in B:A[F]=T;V(A[F])
			elif u in B:
				for H in x:
					if H in B:A[F]=H;V(A[F]);break
			elif'cont_mode_on'in B:p=I;C(BI)
			elif'cont_mode_off'in B:p=G;C(BJ)
			elif BK in B:b=I;C(BL);C(AL)
			elif BM in B:b=G;C(Am)
			elif'reset_animation_timing_to_defaults'in B:
				for J in Bp:U=E.read_json_file('/sd/time_stamp_defaults/'+J+v);E.write_json_file(A8+J+v,U)
			return d(D,'Animation '+A[F]+' started.')
		@U.route('/utilities',[j])
		def l(request):
			J='reset_to_defaults';H='speaker_test';F=request;global A;B=h;D=F.raw_request.decode(Aj)
			if H in D:B=H;C('/sd/menu_voice_commands/left_speaker_right_speaker.wav')
			elif An in D:B=An;A[w]=G;E.write_json_file(T,A);C(a)
			elif Ao in D:B=Ao;A[w]=I;E.write_json_file(T,A);C(a)
			elif J in D:B=J;C0();E.write_json_file(T,A);C(a);e.go_to_state(W)
			return d(F,BN+B)
		@U.route('/lights',[j])
		def l(request):
			O='set_to_100';N='set_to_80';M='set_to_60';L='set_to_40';K='set_to_20';J='set_to_0';I='set_to_white';H='set_to_blue';G='set_to_green';F='set_to_red';E=request;global A;B=h;C=E.raw_request.decode(Aj)
			if F in C:B=F;D.fill((255,0,0));D.show()
			elif G in C:B=G;D.fill((0,255,0));D.show()
			elif H in C:B=H;D.fill((0,0,255));D.show()
			elif I in C:B=I;D.fill((255,255,255));D.show()
			elif J in C:B=J;D.brightness=.0;D.show()
			elif K in C:B=K;D.brightness=.2;D.show()
			elif L in C:B=L;D.brightness=.4;D.show()
			elif M in C:B=M;D.brightness=.6;D.show()
			elif N in C:B=N;D.brightness=.8;D.show()
			elif O in C:B=O;D.brightness=z;D.show()
			return d(E,BN+B)
		@U.route('/update-host-name',[j])
		def l(request):B=request;global A;C=B.json();A[m]=C[AM];E.write_json_file(T,A);Ab.hostname=A[m];BD();return d(B,A[m])
		@U.route('/get-host-name',[j])
		def l(request):return d(request,A[m])
		@U.route('/update-volume',[j])
		def l(request):B=request;global A;C=B.json();Ae(C[A0]);return d(B,A[n])
		@U.route('/get-volume',[j])
		def l(request):return d(request,A[n])
		@U.route('/update-light-string',[j])
		def l(request):
			G=' data: ';F='action: ';D=request;global A;B=D.json()
			if B[A0]=='save'or B[A0]=='clear'or B[A0]=='defaults':A[O]=B[AM];Q(F+B[A0]+G+A[O]);E.write_json_file(T,A);A4();C(a);return d(D,A[O])
			if A[O]==h:A[O]=B[AM]
			else:A[O]=A[O]+','+B[AM]
			Q(F+B[A0]+G+A[O]);E.write_json_file(T,A);A4();C(a);return d(D,A[O])
		@U.route('/get-light-string',[j])
		def l(request):return d(request,A[O])
		@U.route('/get-customers-sound-tracks',[j])
		def l(request):A=E.json_stringify(x);return d(request,A)
	except BE as Ac:AB=G;E.log_item(Ac)
S('web server')
import utilities as Ad
S('utilities')
def P(seconds):
	D=seconds
	if A[w]:C=Bd(Bc,D);B.voice[0].level=C
	else:
		try:C=int(A[n])/100
		except:C=.5
		if C<0 or C>1:C=.5
		B.voice[0].level=C;B.voice[1].level=C;N.sleep(D)
def C0():global A;A[w]=I;A[m]=BO;A[F]=Ak;A[n]=30;B9()
def B9():global A;A[O]='cane-4,cane-4,cane-4,cane-4,cane-4,cane-4,grandtree-21'
def Ae(action):
	D=action;B=int(A[n])
	if D=='lower1':B-=1
	if D=='lower10':B-=10
	if D=='raise10':B+=10
	if D=='raise1':B+=1
	if B>100:B=100
	if B<1:B=1
	A[n]=t(B);A[w]=G;E.write_json_file(T,A);C('/sd/menu_voice_commands/volume.wav');AJ(A[n],G)
def C(file_name):
	if B.voice[0].playing:
		B.voice[0].stop()
		while B.voice[0].playing:P(.02)
	A=c.WaveFile(f(file_name,g));B.voice[0].play(A,loop=G)
	while B.voice[0].playing:C1()
def CO():
	B.voice[0].stop()
	while B.voice[0].playing:0
def C1():
	P(.02);H.update()
	if H.fell:B.voice[0].stop()
def AJ(str_to_speak,addLocal):
	for A in str_to_speak:
		try:
			if A==' ':A='space'
			if A=='-':A='dash'
			if A=='.':A='dot'
			C(i+A+R)
		except:Q('invalid character in string to speak')
	if addLocal:C(BP);C(BQ)
def C2():C('/sd/menu_voice_commands/sound_selection_menu.wav');s()
def C3():C('/sd/menu_voice_commands/choose_my_sounds_menu.wav');s()
def s():C('/sd/menu_voice_commands/press_left_button_right_button.wav')
def C4():C('/sd/menu_voice_commands/main_menu.wav');s()
def C5():C('/sd/menu_voice_commands/add_sounds_animate.wav');s()
def A5():C('/sd/menu_voice_commands/web_menu.wav');s()
def C6():C('/sd/menu_voice_commands/volume_settings_menu.wav');s()
def C7():C('/sd/menu_voice_commands/light_string_setup_menu.wav');s()
def C8():C('/sd/menu_voice_commands/string_instructions.wav')
def BA():C(Ap)
def BB(play_intro):
	if play_intro:C('/sd/menu_voice_commands/current_light_settings_are.wav')
	B=A[O].split(',')
	for(D,E)in enumerate(B):C('/sd/menu_voice_commands/position.wav');C(i+t(D+1)+R);C('/sd/menu_voice_commands/is.wav');C(i+E+R)
def C9():
	C('/sd/menu_voice_commands/no_user_sountrack_found.wav')
	while I:
		H.update();K.update()
		if H.fell:break
		if K.fell:C(BR);break
def V(file_name):
	A=file_name;Q(A);B=A
	if A==A6:
		if A==A6:D=Y(y)-1;C=L.randint(0,D);B=y[C];Q('Random sound file: '+y[C]);Q('Sound file: '+B)
	if b:CB(B)
	else:CA(B)
	S('animation finished')
def CA(file_name):
	D=file_name;global b;O=1;S=3
	if D==Al:O=3;S=3
	T=u in D
	if T:
		D=D.replace(u,h)
		try:U=E.read_json_file(AN+D+v)
		except:
			C(BS)
			while I:
				H.update();K.update()
				if H.fell:b=G;return
				if K.fell:b=I;C(AL);return
	else:U=E.read_json_file(A8+D+v)
	M=U[AO];Z=Y(M);F=0
	if T:V=c.WaveFile(f(AN+D+R,g))
	else:V=c.WaveFile(f(A8+D+R,g))
	B.voice[0].play(V,loop=G);a=N.monotonic();A=0
	while I:
		W=0;X=N.monotonic()-a
		if F<Y(M)-2:J=M[F+1]-M[F]-.25
		else:J=.25
		if J<0:J=0
		if X>M[F]-.25:
			Q('time elasped: '+t(X)+' Timestamp: '+t(M[F]));F+=1;A=L.randint(O,S)
			while A==W:Q('regenerating random selection');A=L.randint(O,S)
			if A==1:CC(.005,J)
			elif A==2:BC(.01);P(J)
			elif A==3:CD(J)
			elif A==4:CE(J)
			elif A==5:BC(J)
			W=A
		if Z==F:F=0
		H.update()
		if H.fell:B.voice[0].stop()
		if not B.voice[0].playing:break
		P(.001)
def CB(file_name):
	A=file_name;Q('time stamp mode');global b;H=u in A;F=E.read_json_file('/sd/time_stamp_defaults/timestamp_mode.json');F[AO]=[];A=A.replace(u,h)
	if H:J=c.WaveFile(f(AN+A+R,g))
	else:J=c.WaveFile(f(A8+A+R,g))
	B.voice[0].play(J,loop=G);M=N.monotonic();P(.1)
	while I:
		L=N.monotonic()-M;K.update()
		if K.fell:F[AO].append(L);Q(L)
		if not B.voice[0].playing:
			D.fill((0,0,0));D.show();F[AO].append(5000)
			if H:E.write_json_file(AN+A+v,F)
			else:E.write_json_file(A8+A+v,F)
			break
	b=G;C('/sd/menu_voice_commands/timestamp_saved.wav');C(Am);C(BT)
def CP():D.brightness=z;A=L.randint(0,255);B=L.randint(0,255);C=L.randint(0,255);D.fill((A,B,C));D.show()
def CC(speed,duration):
	G=duration;F=speed;H=N.monotonic()
	for B in X(0,255,1):
		for A in X(M):C=A*256//M+B;D[A]=B3(C&255)
		D.show();P(F);E=N.monotonic()-H
		if E>G:return
	for B in reversed(X(0,255,1)):
		for A in X(M):C=A*256//M+B;D[A]=B3(C&255)
		D.show();P(F);E=N.monotonic()-H
		if E>G:return
def CD(duration):
	G=N.monotonic();D.brightness=z;A=[];A.extend(AE);A.extend(AH);A.extend(AI);E=[];E.extend(AF)
	for B in E:D[B]=255,255,255
	F=[];F.extend(AG)
	for B in F:D[B]=50,50,50
	H=L.randint(0,255);J=L.randint(0,255);K=L.randint(0,255);Q(Y(A))
	while I:
		for B in A:C=L.randint(0,110);M=Af(H-C,0,255);O=Af(J-C,0,255);R=Af(K-C,0,255);D[B]=M,O,R;D.show()
		P(L.uniform(.05,.1));S=N.monotonic()-G
		if S>duration:return
def CE(duration):
	F=N.monotonic();D.brightness=z
	while I:
		for G in X(0,M):
			H=L.randint(0,255);J=L.randint(0,255);K=L.randint(0,255);A=L.randint(0,1)
			if A==0:B=H;C=0;E=0
			elif A==1:B=0;C=J;E=0
			elif A==2:B=0;C=0;E=K
			D[G]=B,C,E;D.show()
		P(L.uniform(.2,.3));O=N.monotonic()-F
		if O>duration:return
def Af(my_color,lower,upper):
	C=upper;B=lower;A=my_color
	if A<B:A=B
	if A>C:A=C
	return A
def BC(duration):
	F=N.monotonic();D.brightness=z
	while I:
		for G in X(0,M):
			H=L.randint(128,255);J=L.randint(128,255);K=L.randint(128,255);A=L.randint(0,2)
			if A==0:B=H;C=0;E=0
			elif A==1:B=0;C=J;E=0
			elif A==2:B=0;C=0;E=K
			D[G]=B,C,E;D.show()
		P(L.uniform(.2,.3));O=N.monotonic()-F
		if O>duration:return
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
	def reset(A):A.firework_color=random_color();A.burst_count=0;A.shower_count=0;A.firework_step_time=N.monotonic()+.05
class J:
	def __init__(A):0
	@k
	def name(self):return h
	def enter(A,machine):0
	def exit(A,machine):0
	def update(B,machine):
		A=machine
		if H.fell:A.paused_state=A.state.name;A.pause();return G
		return I
class CG(J):
	def __init__(A):0
	@k
	def name(self):return W
	def enter(A,machine):C(BT);E.log_item('Entered base state');J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		global p;B=Ad.switch_state(H,K,P,3.)
		if B==BU:
			if p:p=G;C(BJ)
			else:p=I;C(BI)
		elif B==Aq or p:V(A[F])
		elif B==Ar:machine.go_to_state(Ah)
class CH(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Ah
	def enter(A,machine):E.log_item('Main menu');C4();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(A,machine):
		D=machine;H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AU[A.menuIndex]+R);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>Y(AU)-1:A.menuIndex=0
		if K.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				E=AU[A.selectedMenuIndex]
				if E==As:D.go_to_state(As)
				elif E==At:D.go_to_state(At)
				elif E=='new_feature':
					C(BS)
					while I:
						H.update();K.update()
						if H.fell:F=G;return
						if K.fell:F=I;C(AL);return
				elif E==Au:D.go_to_state(Au)
				elif E==Av:D.go_to_state(Av)
				elif E==AK:D.go_to_state(AK)
				elif E==A7:D.go_to_state(A7)
				else:C(a);D.go_to_state(W)
class CI(J):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@k
	def name(self):return As
	def enter(A,machine):
		Q(BV)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:E.log_item(BW);C2()
		J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(C,machine):
		H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				D=c.WaveFile(f('/sd/christmas_park_options_voice_commands/option_'+AA[C.optionIndex]+R,g));B.voice[0].play(D,loop=G);C.currentOption=C.optionIndex;C.optionIndex+=1
				if C.optionIndex>Y(AA)-1:C.optionIndex=0
				while B.voice[0].playing:0
		if K.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				A[F]=AA[C.currentOption];E.write_json_file(T,A);D=c.WaveFile(f(Ap,g));B.voice[0].play(D,loop=G)
				while B.voice[0].playing:0
			machine.go_to_state(W)
class CJ(J):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@k
	def name(self):return At
	def enter(A,machine):
		Q(BV)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:E.log_item(BW);C3()
		J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(C,machine):
		D=machine;H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				try:
					I=x[C.optionIndex].replace(u,h);AJ(I,G);C.currentOption=C.optionIndex;C.optionIndex+=1
					if C.optionIndex>Y(x)-1:C.optionIndex=0
					while B.voice[0].playing:0
				except:C9();D.go_to_state(W);return
		if K.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				try:
					A[F]=x[C.currentOption];E.write_json_file(T,A);J=c.WaveFile(f(Ap,g));B.voice[0].play(J,loop=G)
					while B.voice[0].playing:0
				except:Q('no sound track')
			D.go_to_state(W)
class CK(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return A7
	def enter(A,machine):E.log_item(A7);C5();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(A,machine):
		E=machine;global b;H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AY[A.menuIndex]+R);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>Y(AY)-1:A.menuIndex=0
		if K.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				D=AY[A.selectedMenuIndex]
				if D=='hear_instructions':C(BR)
				elif D==BK:b=I;C(BL);C(AL);E.go_to_state(W)
				elif D==BM:b=G;C(Am)
				else:C(a);E.go_to_state(W)
class CL(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return AK
	def enter(A,machine):E.log_item(Aw);C6();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		F=machine;H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AX[D.menuIndex]+R);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>Y(AX)-1:D.menuIndex=0
		if K.fell:
			J=AX[D.selectedMenuIndex]
			if J=='volume_level_adjustment':
				C('/sd/menu_voice_commands/volume_adjustment_menu.wav')
				while I:
					L=Ad.switch_state(H,K,P,3.)
					if L==Aq:Ae('lower')
					elif L==Ar:Ae('raise')
					elif L==BX:E.write_json_file(T,A);C(a);F.go_to_state(W);break
					P(.1)
			elif J==An:
				A[w]=G
				if A[n]==0:A[n]=10
				E.write_json_file(T,A);C(a);F.go_to_state(W)
			elif J==Ao:A[w]=I;E.write_json_file(T,A);C(a);F.go_to_state(W)
class CM(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Av
	def enter(A,machine):E.log_item(Aw);A5();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AV[D.menuIndex]+R);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>Y(AV)-1:D.menuIndex=0
		if K.fell:
			F=AV[D.selectedMenuIndex]
			if F=='web_on':A[Ag]=I;BA();A5()
			elif F=='web_off':A[Ag]=G;BA();A5()
			elif F=='hear_url':AJ(A[m],I);A5()
			elif F=='hear_instr_web':C('/sd/menu_voice_commands/web_instruct.wav');A5()
			else:E.write_json_file(T,A);C(a);machine.go_to_state(W)
class CN(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Au
	def enter(A,machine):E.log_item(Aw);C7();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		L=machine;H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AW[D.menuIndex]+R);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>Y(AW)-1:D.menuIndex=0
		if K.fell:
			F=AW[D.selectedMenuIndex]
			if F=='hear_light_setup_instructions':C8()
			elif F=='reset_lights_defaults':B9();C('/sd/menu_voice_commands/lights_reset_to.wav');BB(G)
			elif F=='hear_current_light_settings':BB(I)
			elif F=='clear_light_string':A[O]=h;C('/sd/menu_voice_commands/lights_cleared.wav')
			elif F=='add_lights':
				C('/sd/menu_voice_commands/add_light_menu.wav')
				while I:
					J=Ad.switch_state(H,K,P,3.)
					if J==Aq:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							D.menuIndex-=1
							if D.menuIndex<0:D.menuIndex=Y(q)-1
							D.selectedMenuIndex=D.menuIndex;C(i+q[D.menuIndex]+R)
					elif J==Ar:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							D.menuIndex+=1
							if D.menuIndex>Y(q)-1:D.menuIndex=0
							D.selectedMenuIndex=D.menuIndex;C(i+q[D.menuIndex]+R)
					elif J==BX:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							if A[O]==h:A[O]=q[D.selectedMenuIndex]
							else:A[O]=A[O]+','+q[D.selectedMenuIndex]
							C(i+q[D.selectedMenuIndex]+R);C('/sd/menu_voice_commands/added.wav')
					elif J==BU:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:E.write_json_file(T,A);C(a);A4();L.go_to_state(W)
					P(.1)
			else:E.write_json_file(T,A);C(a);A4();L.go_to_state(W)
class CQ(J):
	def __init__(A):super().__init__()
	@k
	def name(self):return'example'
	def enter(A,machine):J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(A,machine):J.update(A,machine)
e=CF()
e.add_state(CG())
e.add_state(CH())
e.add_state(CI())
e.add_state(CJ())
e.add_state(CK())
e.add_state(CL())
e.add_state(CM())
e.add_state(CN())
A1.value=I
P(.5)
def BD():
	C('/sd/menu_voice_commands/animator_available_on_network.wav');C('/sd/menu_voice_commands/to_access_type.wav')
	if A[m]==BO:C('/sd/menu_voice_commands/animator_dash_christmas_dash_park.wav');C(BP);C(BQ)
	else:AJ(A[m],I)
	C('/sd/menu_voice_commands/in_your_browser.wav')
if AB:
	E.log_item('starting server...')
	try:U.start(t(r.radio.ipv4_address));E.log_item('Listening on http://%s:80'%r.radio.ipv4_address);BD()
	except OSError:N.sleep(5);E.log_item('restarting...');Bb()
e.go_to_state(W)
E.log_item('animator has started...')
S('animations started.')
while I:
	e.update();P(.02)
	if AB:
		try:U.poll()
		except BE as Ac:E.log_item(Ac);continue