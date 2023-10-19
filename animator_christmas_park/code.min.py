BR='right_held'
BQ='Choose sounds menu'
BP='Select a program option'
BO='left_held'
BN='/sd/menu_voice_commands/animations_are_now_active.wav'
BM='/sd/menu_voice_commands/no_timestamp_file_found.wav'
BL='/sd/menu_voice_commands/local.wav'
BK='/sd/menu_voice_commands/dot.wav'
BJ='animator-christmas-park'
BI='Utility: '
BH='/sd/menu_voice_commands/timestamp_mode_off.wav'
BG='/sd/menu_voice_commands/continuous_mode_deactivated.wav'
BF='/sd/menu_voice_commands/continuous_mode_activated.wav'
BE='branches'
BD='ornaments'
BC='wav/micro_sd_card_not_inserted.mp3'
BB=Exception
Au='Set Web Options'
At='web_options'
As='light_string_setup_menu'
Ar='choose_my_sounds'
Aq='choose_sounds'
Ap='right'
Ao='left'
An='/sd/menu_voice_commands/option_selected.wav'
Am='volume_pot_on'
Al='volume_pot_off'
Ak='/sd/menu_voice_commands/timestamp_instructions.wav'
Aj='silent_night'
Ai='we_wish_you_a_merry_christmas'
Ah='utf8'
Ag='config wifi imports'
Af='main_menu'
Ae='serve_webpage'
AM='flashTime'
AL='/sd/christmas_park_sounds/'
AK='/sd/customers_owned_music/'
AJ='text'
AI='random'
AH='volume_settings'
A0='action'
z=1.
w='volume_pot'
v='.json'
u='customers_owned_music_'
t=str
m='volume'
l='HOST_NAME'
k=property
h='/sd/menu_voice_commands/'
e=''
d='rb'
c=open
a='/sd/menu_voice_commands/all_changes_complete.wav'
Z='base_state'
Y=len
W=range
S='.wav'
R='/sd/config_christmas_park.json'
Q=print
O='light_string'
I=False
G=True
F='option_selected'
import gc,files as E
def T(collection_point):gc.collect();A=gc.mem_free();E.log_item('Point '+collection_point+' Available memory: {} bytes'.format(A))
T('Imports gc, files')
import time as N,audiocore as n,audiomixer as BS,audiobusio as BT,sdcardio as Av,storage as A7,busio,digitalio as o,board as X,random as L,rtc,microcontroller as AN,audiomp3 as AO
from analogio import AnalogIn as BU
from adafruit_debouncer import Debouncer as Aw
def BV():AN.on_next_reset(AN.RunMode.NORMAL);AN.reset()
T('imports')
BW=BU(X.A0)
def BX(pin,wait_for):
	B=wait_for/10;A=0
	for C in W(10):N.sleep(B);A+=1;A=A/10
	return pin.value/65536
A1=o.DigitalInOut(X.GP28)
A1.direction=o.Direction.OUTPUT
A1.value=I
BY=X.GP6
BZ=X.GP7
AP=o.DigitalInOut(BY)
AP.direction=o.Direction.INPUT
AP.pull=o.Pull.UP
H=Aw(AP)
AQ=o.DigitalInOut(BZ)
AQ.direction=o.Direction.INPUT
AQ.pull=o.Pull.UP
K=Aw(AQ)
Ba=X.GP18
Bb=X.GP19
Bc=X.GP20
q=BT.I2SOut(bit_clock=Ba,word_select=Bb,data=Bc)
A1.value=G
Bd=X.GP2
Be=X.GP3
Bf=X.GP4
Ax=X.GP5
Ay=busio.SPI(Bd,Be,Bf)
try:AR=Av.SDCard(Ay,Ax);AS=A7.VfsFat(AR);A7.mount(AS,'/sd')
except:
	A2=AO.MP3Decoder(c(BC,d));q.play(A2)
	while q.playing:0
	Az=I
	while not Az:
		H.update()
		if H.fell:
			try:
				AR=Av.SDCard(Ay,Ax);AS=A7.VfsFat(AR);A7.mount(AS,'/sd');Az=G;A2=AO.MP3Decoder(c('wav/micro_sd_card_success.mp3',d));q.play(A2)
				while q.playing:0
			except:
				A2=AO.MP3Decoder(c(BC,d));q.play(A2)
				while q.playing:0
Bg=2
B=BS.Mixer(voice_count=Bg,sample_rate=22050,channel_count=2,bits_per_sample=16,samples_signed=G,buffer_size=4096)
q.play(B)
A1.value=I
Bh=rtc.RTC()
Bh.datetime=N.struct_time((2019,5,29,15,14,15,0,-1,-1))
A=E.read_json_file(R)
x=A['options']
A3=E.return_directory(u,'/sd/customers_owned_music',S)
Bi=E.return_directory(e,'/sd/time_stamp_defaults',v)
A8=A[Ae]
Bj=E.read_json_file('/sd/menu_voice_commands/main_menu.json')
AT=Bj[Af]
Bk=E.read_json_file('/sd/menu_voice_commands/web_menu.json')
AU=Bk['web_menu']
Bl=E.read_json_file('/sd/menu_voice_commands/light_string_menu.json')
AV=Bl['light_string_menu']
Bm=E.read_json_file('/sd/menu_voice_commands/light_options.json')
r=Bm['light_options']
Bn=E.read_json_file('/sd/menu_voice_commands/volume_settings.json')
AW=Bn[AH]
T('config setup')
p=I
i=I
import neopixel as A_
from rainbowio import colorwheel as B0
A9=[]
AA=[]
AB=[]
AC=[]
AD=[]
AE=[]
AF=[]
M=0
D=A_.NeoPixel(X.GP10,M)
def AX(part):
	C=part;B=[]
	for E in A9:
		for A in E:D=A;break
		if C==BD:
			for A in W(0,7):B.append(A+D)
		if C=='star':
			for A in W(7,14):B.append(A+D)
		if C==BE:
			for A in W(14,21):B.append(A+D)
	return B
def B1(part):
	B=[]
	for D in AA:
		for A in D:C=A;break
		if part=='end':
			for A in W(0,2):B.append(A+C)
		if part=='start':
			for A in W(2,4):B.append(A+C)
	return B
def A4():D.show();N.sleep(.3);D.fill((0,0,0));D.show()
def Bo():
	global AB,AC,AD,AE,AF;AB=AX(BD);AC=AX('star');AD=AX(BE);AE=B1('start');AF=B1('end');A=0
	for B in AE:
		D[B]=50,50,50;A+=1
		if A>1:A4();A=0
	for B in AF:
		D[B]=50,50,50;A+=1
		if A>1:A4();A=0
	A=0
	for B in AB:
		D[B]=50,50,50;A+=1
		if A>6:A4();A=0
	for B in AC:
		D[B]=50,50,50;A+=1
		if A>6:A4();A=0
	for B in AD:
		D[B]=50,50,50;A+=1
		if A>6:A4();A=0
def A5():
	global A9,AA,M,D,M;A9=[];AA=[];M=0;F=A[O].split(',')
	for G in F:
		C=G.split('-')
		if Y(C)==2:
			E,B=C;B=int(B)
			if E=='grandtree':H=list(W(M,M+B));A9.append(H);M+=B
			elif E=='cane':J=list(W(M,M+B));AA.append(J);M+=B
	Q('Number of pixels total: ',M);D.deinit();T('Deinit ledStrip');D=A_.NeoPixel(X.GP10,M);D.auto_write=I;D.brightness=z;Bo()
A5()
T('Neopixels setup')
if A8:
	import socketpool as Bp,mdns;T(Ag);import wifi as s;T(Ag);from adafruit_httpserver import Server,Request,FileResponse as AY,Response as b,POST as f;T(Ag);E.log_item('Connecting to WiFi');B2='jimmytrainsguest';B3=e
	try:B4=E.read_json_file('/sd/env.json');B2=B4['WIFI_SSID'];B3=B4['WIFI_PASSWORD'];T('wifi env');Q('Using env ssid and password')
	except:Q('Using default ssid and password')
	try:
		s.radio.connect(B2,B3);T('wifi connect');AZ=mdns.Server(s.radio);AZ.hostname=A[l];AZ.advertise_service(service_type='_http',protocol='_tcp',port=80);Bq=[hex(A)for A in s.radio.mac_address];E.log_item('My MAC addr:'+t(Bq));Br=t(s.radio.ipv4_address);E.log_item('My IP address is'+Br);E.log_item('Connected to WiFi');Bs=Bp.SocketPool(s.radio);U=Server(Bs,'/static',debug=G);T('wifi server')
		@U.route('/')
		def B5(request):T('Home page.');return AY(request,'index.html','/')
		@U.route('/mui.min.css')
		def B5(request):return AY(request,'mui.min.css','/')
		@U.route('/mui.min.js')
		def B5(request):return AY(request,'mui.min.js','/')
		@U.route('/animation',[f])
		def j(request):
			T='auld_lang_syne_jazzy_version';S='joy_to_the_world';R='away_in_a_manger';Q='jingle_bells_orchestra';P='the_wassail_song';O='deck_the_halls_jazzy_version';N='dance_of_the_sugar_plum_fairy';M='carol_of_the_bells';L='joyful_snowman';K='angels_we_have_heard_on_high';D=request;global A;global p;global i;B=D.raw_request.decode(Ah)
			if AI in B:A[F]=AI;V(A[F])
			elif Ai in B:A[F]=Ai;V(A[F])
			elif K in B:A[F]=K;V(A[F])
			elif L in B:A[F]=L;V(A[F])
			elif M in B:A[F]=M;V(A[F])
			elif N in B:A[F]=N;V(A[F])
			elif O in B:A[F]=O;V(A[F])
			elif P in B:A[F]=P;V(A[F])
			elif Q in B:A[F]=Q;V(A[F])
			elif R in B:A[F]=R;V(A[F])
			elif S in B:A[F]=S;V(A[F])
			elif Aj in B:A[F]=Aj;V(A[F])
			elif T in B:A[F]=T;V(A[F])
			elif u in B:
				for H in A3:
					if H in B:A[F]=H;V(A[F]);break
			elif'cont_mode_on'in B:p=G;C(BF)
			elif'cont_mode_off'in B:p=I;C(BG)
			elif'timestamp_mode_on'in B:i=G;C('/sd/menu_voice_commands/timestamp_mode_on.wav');C(Ak)
			elif'timestamp_mode_off'in B:i=I;C(BH)
			elif'reset_animation_timing_to_defaults'in B:
				for J in Bi:U=E.read_json_file('/sd/time_stamp_defaults/'+J+v);E.write_json_file('/sd/christmas_park_sounds2/'+J+v,U)
			return b(D,'Animation '+A[F]+' started.')
		@U.route('/utilities',[f])
		def j(request):
			J='reset_to_defaults';H='speaker_test';F=request;global A;B=e;D=F.raw_request.decode(Ah)
			if H in D:B=H;C('/sd/menu_voice_commands/left_speaker_right_speaker.wav')
			elif Al in D:B=Al;A[w]=I;E.write_json_file(R,A);C(a)
			elif Am in D:B=Am;A[w]=G;E.write_json_file(R,A);C(a)
			elif J in D:B=J;Bt();E.write_json_file(R,A);C(a);g.go_to_state(Z)
			return b(F,BI+B)
		@U.route('/lights',[f])
		def j(request):
			O='set_to_100';N='set_to_80';M='set_to_60';L='set_to_40';K='set_to_20';J='set_to_0';I='set_to_white';H='set_to_blue';G='set_to_green';F='set_to_red';E=request;global A;B=e;C=E.raw_request.decode(Ah)
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
			return b(E,BI+B)
		@U.route('/update-host-name',[f])
		def j(request):B=request;global A;C=B.json();A[l]=C[AJ];E.write_json_file(R,A);AZ.hostname=A[l];BA();return b(B,A[l])
		@U.route('/get-host-name',[f])
		def j(request):return b(request,A[l])
		@U.route('/update-volume',[f])
		def j(request):B=request;global A;C=B.json();Ac(C[A0]);return b(B,A[m])
		@U.route('/get-volume',[f])
		def j(request):return b(request,A[m])
		@U.route('/update-light-string',[f])
		def j(request):
			G=' data: ';F='action: ';D=request;global A;B=D.json()
			if B[A0]=='save'or B[A0]=='clear'or B[A0]=='defaults':A[O]=B[AJ];Q(F+B[A0]+G+A[O]);E.write_json_file(R,A);A5();C(a);return b(D,A[O])
			if A[O]==e:A[O]=B[AJ]
			else:A[O]=A[O]+','+B[AJ]
			Q(F+B[A0]+G+A[O]);E.write_json_file(R,A);A5();C(a);return b(D,A[O])
		@U.route('/get-light-string',[f])
		def j(request):return b(request,A[O])
		@U.route('/get-customers-sound-tracks',[f])
		def j(request):A=E.json_stringify(A3);return b(request,A)
	except BB as Aa:A8=I;E.log_item(Aa)
T('web server')
import utilities as Ab
T('utilities')
def P(seconds):
	D=seconds
	if A[w]:C=BX(BW,D);B.voice[0].level=C
	else:
		try:C=int(A[m])/100
		except:C=.5
		if C<0 or C>1:C=.5
		B.voice[0].level=C;B.voice[1].level=C;N.sleep(D)
def Bt():global A;A[w]=G;A[l]=BJ;A[F]=Ai;A[m]=30;B6()
def B6():global A;A[O]='cane-4,cane-4,cane-4,cane-4,cane-4,cane-4,grandtree-21'
def Ac(action):
	D=action;B=int(A[m])
	if D=='lower1':B-=1
	if D=='lower10':B-=10
	if D=='raise10':B+=10
	if D=='raise1':B+=1
	if B>100:B=100
	if B<1:B=1
	A[m]=t(B);A[w]=I;E.write_json_file(R,A);C('/sd/menu_voice_commands/volume.wav');AG(A[m],I)
def C(file_name):
	if B.voice[0].playing:
		B.voice[0].stop()
		while B.voice[0].playing:P(.02)
	A=n.WaveFile(c(file_name,d));B.voice[0].play(A,loop=I)
	while B.voice[0].playing:Bu()
def CE():
	B.voice[0].stop()
	while B.voice[0].playing:0
def Bu():
	P(.02);H.update()
	if H.fell:B.voice[0].stop()
def AG(str_to_speak,addLocal):
	for A in str_to_speak:
		try:
			if A==' ':A='space'
			if A=='-':A='dash'
			if A=='.':A='dot'
			C(h+A+S)
		except:Q('invalid character in string to speak')
	if addLocal:C(BK);C(BL)
def Bv():C('/sd/menu_voice_commands/sound_selection_menu.wav');y()
def Bw():C('/sd/menu_voice_commands/choose_my_sounds_menu.wav');y()
def y():C('/sd/menu_voice_commands/press_left_button_right_button.wav')
def Bx():C('/sd/menu_voice_commands/main_menu.wav');y()
def A6():C('/sd/menu_voice_commands/web_menu.wav');y()
def By():C('/sd/menu_voice_commands/volume_settings_menu.wav');y()
def Bz():C('/sd/menu_voice_commands/light_string_setup_menu.wav');y()
def B_():C('/sd/menu_voice_commands/string_instructions.wav')
def B7():C(An)
def B8(play_intro):
	if play_intro:C('/sd/menu_voice_commands/current_light_settings_are.wav')
	B=A[O].split(',')
	for(D,E)in enumerate(B):C('/sd/menu_voice_commands/position.wav');C(h+t(D+1)+S);C('/sd/menu_voice_commands/is.wav');C(h+E+S)
def C0():
	C('/sd/menu_voice_commands/no_user_sountrack_found.wav')
	while G:
		H.update();K.update()
		if H.fell:break
		if K.fell:C('/sd/menu_voice_commands/create_sound_track_files.wav');break
def V(file_name):
	A=file_name;Q(A);B=A
	if A==AI:
		if A==AI:D=Y(x)-2;C=L.randint(0,D);B=x[C];Q('Random sound file: '+x[C]);Q('Sound file: '+B)
	if i:C2(B)
	else:C1(B)
def C1(file_name):
	D=file_name;global i;O=1;R=3
	if D==Aj:O=3;R=3
	T=u in D
	if T:
		D=D.replace(u,e)
		try:U=E.read_json_file(AK+D+v)
		except:
			C(BM)
			while G:
				H.update();K.update()
				if H.fell:i=I;return
				if K.fell:i=G;C(Ak);return
	else:U=E.read_json_file(AL+D+v)
	M=U[AM];Z=Y(M);F=0
	if T:V=n.WaveFile(c(AK+D+S,d))
	else:V=n.WaveFile(c(AL+D+S,d))
	B.voice[0].play(V,loop=I);a=N.monotonic();A=0
	while G:
		W=0;X=N.monotonic()-a
		if F<Y(M)-2:J=M[F+1]-M[F]-.25
		else:J=.25
		if J<0:J=0
		if X>M[F]-.25:
			Q('time elasped: '+t(X)+' Timestamp: '+t(M[F]));F+=1;A=L.randint(O,R)
			while A==W:Q('regenerating random selection');A=L.randint(O,R)
			if A==1:C3(.005,J)
			elif A==2:B9(.01);P(J)
			elif A==3:C4(J)
			elif A==4:C5(J)
			elif A==5:B9(J)
			W=A
		if Z==F:F=0
		H.update()
		if H.fell:B.voice[0].stop()
		if not B.voice[0].playing:break
		P(.001)
def C2(file_name):
	A=file_name;Q('time stamp mode');global i;H=u in A;F=E.read_json_file('/sd/time_stamp_defaults/timestamp_mode.json');F[AM]=[];A=A.replace(u,e)
	if H:J=n.WaveFile(c(AK+A+S,d))
	else:J=n.WaveFile(c(AL+A+S,d))
	B.voice[0].play(J,loop=I);M=N.monotonic();P(.1)
	while G:
		L=N.monotonic()-M;K.update()
		if K.fell:F[AM].append(L);Q(L)
		if not B.voice[0].playing:
			D.fill((0,0,0));D.show();F[AM].append(5000)
			if H:E.write_json_file(AK+A+v,F)
			else:E.write_json_file(AL+A+v,F)
			break
	i=I;C('/sd/menu_voice_commands/timestamp_saved.wav');C(BH);C(BN)
def CF():D.brightness=z;A=L.randint(0,255);B=L.randint(0,255);C=L.randint(0,255);D.fill((A,B,C));D.show()
def C3(speed,duration):
	G=duration;F=speed;H=N.monotonic()
	for B in W(0,255,1):
		for A in W(M):C=A*256//M+B;D[A]=B0(C&255)
		D.show();P(F);E=N.monotonic()-H
		if E>G:return
	for B in reversed(W(0,255,1)):
		for A in W(M):C=A*256//M+B;D[A]=B0(C&255)
		D.show();P(F);E=N.monotonic()-H
		if E>G:return
def C4(duration):
	H=N.monotonic();D.brightness=z;A=[];A.extend(AB);A.extend(AE);A.extend(AF);E=[];E.extend(AC)
	for B in E:D[B]=255,255,255
	F=[];F.extend(AD)
	for B in F:D[B]=50,50,50
	I=L.randint(0,255);J=L.randint(0,255);K=L.randint(0,255);Q(Y(A))
	while G:
		for B in A:C=L.randint(0,110);M=Ad(I-C,0,255);O=Ad(J-C,0,255);R=Ad(K-C,0,255);D[B]=M,O,R;D.show()
		P(L.uniform(.05,.1));S=N.monotonic()-H
		if S>duration:return
def C5(duration):
	F=N.monotonic();D.brightness=z
	while G:
		for H in W(0,M):
			I=L.randint(0,255);J=L.randint(0,255);K=L.randint(0,255);A=L.randint(0,1)
			if A==0:B=I;C=0;E=0
			elif A==1:B=0;C=J;E=0
			elif A==2:B=0;C=0;E=K
			D[H]=B,C,E;D.show()
		P(L.uniform(.2,.3));O=N.monotonic()-F
		if O>duration:return
def Ad(my_color,lower,upper):
	C=upper;B=lower;A=my_color
	if A<B:A=B
	if A>C:A=C
	return A
def B9(duration):
	F=N.monotonic();D.brightness=z
	while G:
		for H in W(0,M):
			I=L.randint(128,255);J=L.randint(128,255);K=L.randint(128,255);A=L.randint(0,2)
			if A==0:B=I;C=0;E=0
			elif A==1:B=0;C=J;E=0
			elif A==2:B=0;C=0;E=K
			D[H]=B,C,E;D.show()
		P(L.uniform(.2,.3));O=N.monotonic()-F
		if O>duration:return
class C6:
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
	def name(self):return e
	def enter(A,machine):0
	def exit(A,machine):0
	def update(B,machine):
		A=machine
		if H.fell:A.paused_state=A.state.name;A.pause();return I
		return G
class C7(J):
	def __init__(A):0
	@k
	def name(self):return Z
	def enter(A,machine):C(BN);E.log_item('Entered base state');J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		global p;B=Ab.switch_state(H,K,P,3.)
		if B==BO:
			if p:p=I;C(BG)
			else:p=G;C(BF)
		elif B==Ao or p:V(A[F])
		elif B==Ap:machine.go_to_state(Af)
class C8(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Af
	def enter(A,machine):E.log_item('Main menu');Bx();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(A,machine):
		D=machine;H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(h+AT[A.menuIndex]+S);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>Y(AT)-1:A.menuIndex=0
		if K.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				E=AT[A.selectedMenuIndex]
				if E==Aq:D.go_to_state(Aq)
				elif E==Ar:D.go_to_state(Ar)
				elif E=='new_feature':
					C(BM)
					while G:
						H.update();K.update()
						if H.fell:F=I;return
						if K.fell:F=G;C(Ak);return
				elif E==As:D.go_to_state(As)
				elif E==At:D.go_to_state(At)
				elif E==AH:D.go_to_state(AH)
				else:C(a);D.go_to_state(Z)
class C9(J):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@k
	def name(self):return Aq
	def enter(A,machine):
		Q(BP)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:E.log_item(BQ);Bv()
		J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(C,machine):
		H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				D=n.WaveFile(c('/sd/christmas_park_options_voice_commands/option_'+x[C.optionIndex]+S,d));B.voice[0].play(D,loop=I);C.currentOption=C.optionIndex;C.optionIndex+=1
				if C.optionIndex>Y(x)-1:C.optionIndex=0
				while B.voice[0].playing:0
		if K.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				A[F]=x[C.currentOption];E.write_json_file(R,A);D=n.WaveFile(c(An,d));B.voice[0].play(D,loop=I)
				while B.voice[0].playing:0
			machine.go_to_state(Z)
class CA(J):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@k
	def name(self):return Ar
	def enter(A,machine):
		Q(BP)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:E.log_item(BQ);Bw()
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
					G=A3[C.optionIndex].replace(u,e);AG(G,I);C.currentOption=C.optionIndex;C.optionIndex+=1
					if C.optionIndex>Y(A3)-1:C.optionIndex=0
					while B.voice[0].playing:0
				except:C0();D.go_to_state(Z);return
		if K.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				try:
					A[F]=A3[C.currentOption];E.write_json_file(R,A);J=n.WaveFile(c(An,d));B.voice[0].play(J,loop=I)
					while B.voice[0].playing:0
				except:Q('no sound track')
			D.go_to_state(Z)
class CB(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return At
	def enter(A,machine):E.log_item(Au);A6();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(h+AU[D.menuIndex]+S);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>Y(AU)-1:D.menuIndex=0
		if K.fell:
			F=AU[D.selectedMenuIndex]
			if F=='web_on':A[Ae]=G;B7();A6()
			elif F=='web_off':A[Ae]=I;B7();A6()
			elif F=='hear_url':AG(A[l],G);A6()
			elif F=='hear_instr_web':C('/sd/menu_voice_commands/web_instruct.wav');A6()
			else:E.write_json_file(R,A);C(a);machine.go_to_state(Z)
class CC(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return As
	def enter(A,machine):E.log_item(Au);Bz();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		L=machine;H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(h+AV[D.menuIndex]+S);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>Y(AV)-1:D.menuIndex=0
		if K.fell:
			F=AV[D.selectedMenuIndex]
			if F=='hear_light_setup_instructions':B_()
			elif F=='reset_lights_defaults':B6();C('/sd/menu_voice_commands/lights_reset_to.wav');B8(I)
			elif F=='hear_current_light_settings':B8(G)
			elif F=='clear_light_string':A[O]=e;C('/sd/menu_voice_commands/lights_cleared.wav')
			elif F=='add_lights':
				C('/sd/menu_voice_commands/add_light_menu.wav')
				while G:
					J=Ab.switch_state(H,K,P,3.)
					if J==Ao:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							D.menuIndex-=1
							if D.menuIndex<0:D.menuIndex=Y(r)-1
							D.selectedMenuIndex=D.menuIndex;C(h+r[D.menuIndex]+S)
					elif J==Ap:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							D.menuIndex+=1
							if D.menuIndex>Y(r)-1:D.menuIndex=0
							D.selectedMenuIndex=D.menuIndex;C(h+r[D.menuIndex]+S)
					elif J==BR:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							if A[O]==e:A[O]=r[D.selectedMenuIndex]
							else:A[O]=A[O]+','+r[D.selectedMenuIndex]
							C(h+r[D.selectedMenuIndex]+S);C('/sd/menu_voice_commands/added.wav')
					elif J==BO:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:E.write_json_file(R,A);C(a);A5();L.go_to_state(Z)
					P(.1)
			else:E.write_json_file(R,A);C(a);A5();L.go_to_state(Z)
class CD(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return AH
	def enter(A,machine):E.log_item(Au);By();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		F=machine;H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(h+AW[D.menuIndex]+S);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>Y(AW)-1:D.menuIndex=0
		if K.fell:
			J=AW[D.selectedMenuIndex]
			if J=='volume_level_adjustment':
				C('/sd/menu_voice_commands/volume_adjustment_menu.wav')
				while G:
					L=Ab.switch_state(H,K,P,3.)
					if L==Ao:Ac('lower')
					elif L==Ap:Ac('raise')
					elif L==BR:E.write_json_file(R,A);C(a);F.go_to_state(Z);break
					P(.1)
			elif J==Al:
				A[w]=I
				if A[m]==0:A[m]=10
				E.write_json_file(R,A);C(a);F.go_to_state(Z)
			elif J==Am:A[w]=G;E.write_json_file(R,A);C(a);F.go_to_state(Z)
class CG(J):
	def __init__(A):super().__init__()
	@k
	def name(self):return'example'
	def enter(A,machine):J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(A,machine):J.update(A,machine)
g=C6()
g.add_state(C7())
g.add_state(C9())
g.add_state(CA())
g.add_state(C8())
g.add_state(CB())
g.add_state(CC())
g.add_state(CD())
A1.value=G
P(.5)
def BA():
	C('/sd/menu_voice_commands/animator_available_on_network.wav');C('/sd/menu_voice_commands/to_access_type.wav')
	if A[l]==BJ:C('/sd/menu_voice_commands/animator_dash_christmas_dash_park.wav');C(BK);C(BL)
	else:AG(A[l],G)
	C('/sd/menu_voice_commands/in_your_browser.wav')
if A8:
	E.log_item('starting server...')
	try:U.start(t(s.radio.ipv4_address));E.log_item('Listening on http://%s:80'%s.radio.ipv4_address);BA()
	except OSError:N.sleep(5);E.log_item('restarting...');BV()
g.go_to_state(Z)
E.log_item('animator has started...')
T('animations started.')
while G:
	g.update();P(.02)
	if A8:
		try:U.poll()
		except BB as Aa:E.log_item(Aa);continue