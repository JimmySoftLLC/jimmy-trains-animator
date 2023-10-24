BX='right_held'
BW='Choose sounds menu'
BV='Select a program option'
BU='left_held'
BT='/sd/menu_voice_commands/animations_are_now_active.wav'
BS='/sd/menu_voice_commands/create_sound_track_files.wav'
BR='/sd/menu_voice_commands/local.wav'
BQ='/sd/menu_voice_commands/dot.wav'
BP='animator-christmas-park'
BO='Utility: '
BN='timestamp_mode_off'
BM='/sd/menu_voice_commands/timestamp_mode_on.wav'
BL='timestamp_mode_on'
BK='/sd/menu_voice_commands/continuous_mode_deactivated.wav'
BJ='/sd/menu_voice_commands/continuous_mode_activated.wav'
BI='branches'
BH='ornaments'
BG='wav/no_card.wav'
BF=Exception
Ax='Set Web Options'
Aw='web_options'
Av='light_string_setup_menu'
Au='choose_my_sounds'
At='choose_sounds'
As='right'
Ar='left'
Aq='/sd/menu_voice_commands/option_selected.wav'
Ap='volume_pot_on'
Ao='volume_pot_off'
An='/sd/menu_voice_commands/timestamp_mode_off.wav'
Am='/sd/menu_voice_commands/timestamp_instructions.wav'
Al='silent_night'
Ak='random_my'
Aj='random_built_in'
Ai='utf8'
Ah='config wifi imports'
Ag='main_menu'
Af='serve_webpage'
AN='flashTime'
AM='/sd/customers_owned_music/'
AL='text'
AK='random_all'
AJ='volume_settings'
A8='/sd/christmas_park_sounds/'
A7='add_sounds_animate'
A0='action'
z=1.
y='volume_pot'
x='.json'
w='customers_owned_music_'
v=str
o='volume'
n='HOST_NAME'
k=property
i='/sd/menu_voice_commands/'
h=''
g='rb'
f=open
a='/sd/menu_voice_commands/all_changes_complete.wav'
Y=range
X='base_state'
V='/sd/config_christmas_park.json'
U=len
S='.wav'
P='light_string'
M=print
J=True
G=False
F='option_selected'
import gc,files as E
def T(collection_point):gc.collect();A=gc.mem_free();E.log_item('Point '+collection_point+' Available memory: {} bytes'.format(A))
T('Imports gc, files')
import time as O,audiocore as c,audiomixer as BY,audiobusio as BZ,sdcardio as Ay,storage as A9,busio,digitalio as p,board as Z,random as K,rtc,microcontroller as AO
from analogio import AnalogIn as Ba
from adafruit_debouncer import Debouncer as Az
def Bb():AO.on_next_reset(AO.RunMode.NORMAL);AO.reset()
T('imports')
Bc=Ba(Z.A0)
def Bd(pin,wait_for):
	B=wait_for/10;A=0
	for C in Y(10):O.sleep(B);A+=1;A=A/10
	return pin.value/65536
A1=p.DigitalInOut(Z.GP28)
A1.direction=p.Direction.OUTPUT
A1.value=G
Be=Z.GP6
Bf=Z.GP7
AP=p.DigitalInOut(Be)
AP.direction=p.Direction.INPUT
AP.pull=p.Pull.UP
H=Az(AP)
AQ=p.DigitalInOut(Bf)
AQ.direction=p.Direction.INPUT
AQ.pull=p.Pull.UP
L=Az(AQ)
Bg=Z.GP18
Bh=Z.GP19
Bi=Z.GP20
Bj=BZ.I2SOut(bit_clock=Bg,word_select=Bh,data=Bi)
A1.value=J
Bk=Z.GP2
Bl=Z.GP3
Bm=Z.GP4
A_=Z.GP5
B0=busio.SPI(Bk,Bl,Bm)
Bn=2
B=BY.Mixer(voice_count=Bn,sample_rate=22050,channel_count=2,bits_per_sample=16,samples_signed=J,buffer_size=4096)
Bj.play(B)
B1=.2
B.voice[0].level=B1
B.voice[1].level=B1
try:AR=Ay.SDCard(B0,A_);AS=A9.VfsFat(AR);A9.mount(AS,'/sd')
except:
	A2=c.WaveFile(f(BG,g));B.voice[0].play(A2,loop=G)
	while B.voice[0].playing:0
	B2=G
	while not B2:
		H.update()
		if H.fell:
			try:
				AR=Ay.SDCard(B0,A_);AS=A9.VfsFat(AR);A9.mount(AS,'/sd');B2=J;A2=c.WaveFile(f('/sd/menu_voice_commands/micro_sd_card_success.wav',g));B.voice[0].play(A2,loop=G)
				while B.voice[0].playing:0
			except:
				A2=c.WaveFile(f(BG,g));B.voice[0].play(A2,loop=G)
				while B.voice[0].playing:0
A1.value=G
Bo=rtc.RTC()
Bo.datetime=O.struct_time((2019,5,29,15,14,15,0,-1,-1))
A=E.read_json_file(V)
r=A['options']
l=E.return_directory(w,'/sd/customers_owned_music',S)
A3=[]
A3.extend(l)
A3.extend(r)
Bp=E.return_directory(h,'/sd/time_stamp_defaults',x)
AA=A[Af]
Bq=E.read_json_file('/sd/menu_voice_commands/main_menu.json')
AT=Bq[Ag]
Br=E.read_json_file('/sd/menu_voice_commands/web_menu.json')
AU=Br['web_menu']
Bs=E.read_json_file('/sd/menu_voice_commands/light_string_menu.json')
AV=Bs['light_string_menu']
Bt=E.read_json_file('/sd/menu_voice_commands/light_options.json')
s=Bt['light_options']
Bu=E.read_json_file('/sd/menu_voice_commands/volume_settings.json')
AW=Bu[AJ]
Bv=E.read_json_file('/sd/menu_voice_commands/add_sounds_animate.json')
AX=Bv[A7]
T('config setup')
q=G
b=G
import neopixel as B3
from rainbowio import colorwheel as B4
AB=[]
AC=[]
AD=[]
AE=[]
AF=[]
AG=[]
AH=[]
N=0
D=B3.NeoPixel(Z.GP10,N)
def AY(part):
	C=part;B=[]
	for E in AB:
		for A in E:D=A;break
		if C==BH:
			for A in Y(0,7):B.append(A+D)
		if C=='star':
			for A in Y(7,14):B.append(A+D)
		if C==BI:
			for A in Y(14,21):B.append(A+D)
	return B
def B5(part):
	B=[]
	for D in AC:
		for A in D:C=A;break
		if part=='end':
			for A in Y(0,2):B.append(A+C)
		if part=='start':
			for A in Y(2,4):B.append(A+C)
	return B
def A4():D.show();O.sleep(.3);D.fill((0,0,0));D.show()
def Bw():
	global AD,AE,AF,AG,AH;AD=AY(BH);AE=AY('star');AF=AY(BI);AG=B5('start');AH=B5('end');A=0
	for B in AG:
		D[B]=50,50,50;A+=1
		if A>1:A4();A=0
	for B in AH:
		D[B]=50,50,50;A+=1
		if A>1:A4();A=0
	A=0
	for B in AD:
		D[B]=50,50,50;A+=1
		if A>6:A4();A=0
	for B in AE:
		D[B]=50,50,50;A+=1
		if A>6:A4();A=0
	for B in AF:
		D[B]=50,50,50;A+=1
		if A>6:A4();A=0
def A5():
	global AB,AC,N,D,N;AB=[];AC=[];N=0;F=A[P].split(',')
	for H in F:
		C=H.split('-')
		if U(C)==2:
			E,B=C;B=int(B)
			if E=='grandtree':I=list(Y(N,N+B));AB.append(I);N+=B
			elif E=='cane':J=list(Y(N,N+B));AC.append(J);N+=B
	M('Number of pixels total: ',N);D.deinit();T('Deinit ledStrip');D=B3.NeoPixel(Z.GP10,N);D.auto_write=G;D.brightness=z;Bw()
A5()
T('Neopixels setup')
if AA:
	import socketpool as Bx,mdns;T(Ah);import wifi as t;T(Ah);from adafruit_httpserver import Server,Request,FileResponse as AZ,Response as d,POST as j;T(Ah);E.log_item('Connecting to WiFi');B6='jimmytrainsguest';B7=h
	try:B8=E.read_json_file('/sd/env.json');B6=B8['WIFI_SSID'];B7=B8['WIFI_PASSWORD'];T('wifi env');M('Using env ssid and password')
	except:M('Using default ssid and password')
	try:
		t.radio.connect(B6,B7);T('wifi connect');Aa=mdns.Server(t.radio);Aa.hostname=A[n];Aa.advertise_service(service_type='_http',protocol='_tcp',port=80);By=[hex(A)for A in t.radio.mac_address];E.log_item('My MAC addr:'+v(By));Bz=v(t.radio.ipv4_address);E.log_item('My IP address is'+Bz);E.log_item('Connected to WiFi');B_=Bx.SocketPool(t.radio);W=Server(B_,'/static',debug=J);T('wifi server')
		@W.route('/')
		def B9(request):T('Home page.');return AZ(request,'index.html','/')
		@W.route('/mui.min.css')
		def B9(request):return AZ(request,'mui.min.css','/')
		@W.route('/mui.min.js')
		def B9(request):return AZ(request,'mui.min.js','/')
		@W.route('/animation',[j])
		def m(request):
			V='auld_lang_syne_jazzy_version';U='joy_to_the_world';T='away_in_a_manger';S='jingle_bells_orchestra';Q='the_wassail_song';P='deck_the_halls_jazzy_version';O='dance_of_the_sugar_plum_fairy';N='carol_of_the_bells';M='joyful_snowman';L='angels_we_have_heard_on_high';K='we_wish_you_a_merry_christmas';D=request;global A;global q;global b;B=D.raw_request.decode(Ai)
			if Aj in B:A[F]=Aj;R(A[F])
			elif Ak in B:A[F]=Ak;R(A[F])
			elif AK in B:A[F]=AK;R(A[F])
			elif K in B:A[F]=K;R(A[F])
			elif L in B:A[F]=L;R(A[F])
			elif M in B:A[F]=M;R(A[F])
			elif N in B:A[F]=N;R(A[F])
			elif O in B:A[F]=O;R(A[F])
			elif P in B:A[F]=P;R(A[F])
			elif Q in B:A[F]=Q;R(A[F])
			elif S in B:A[F]=S;R(A[F])
			elif T in B:A[F]=T;R(A[F])
			elif U in B:A[F]=U;R(A[F])
			elif Al in B:A[F]=Al;R(A[F])
			elif V in B:A[F]=V;R(A[F])
			elif w in B:
				for H in l:
					if H in B:A[F]=H;R(A[F]);break
			elif'cont_mode_on'in B:q=J;C(BJ)
			elif'cont_mode_off'in B:q=G;C(BK)
			elif BL in B:b=J;C(BM);C(Am)
			elif BN in B:b=G;C(An)
			elif'reset_animation_timing_to_defaults'in B:
				for I in Bp:W=E.read_json_file('/sd/time_stamp_defaults/'+I+x);E.write_json_file(A8+I+x,W)
			return d(D,'Animation '+A[F]+' started.')
		@W.route('/utilities',[j])
		def m(request):
			I='reset_to_defaults';H='speaker_test';F=request;global A;B=h;D=F.raw_request.decode(Ai)
			if H in D:B=H;C('/sd/menu_voice_commands/left_speaker_right_speaker.wav')
			elif Ao in D:B=Ao;A[y]=G;E.write_json_file(V,A);C(a)
			elif Ap in D:B=Ap;A[y]=J;E.write_json_file(V,A);C(a)
			elif I in D:B=I;C0();E.write_json_file(V,A);C(a);e.go_to_state(X)
			return d(F,BO+B)
		@W.route('/lights',[j])
		def m(request):
			O='set_to_100';N='set_to_80';M='set_to_60';L='set_to_40';K='set_to_20';J='set_to_0';I='set_to_white';H='set_to_blue';G='set_to_green';F='set_to_red';E=request;global A;B=h;C=E.raw_request.decode(Ai)
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
			return d(E,BO+B)
		@W.route('/update-host-name',[j])
		def m(request):B=request;global A;C=B.json();A[n]=C[AL];E.write_json_file(V,A);Aa.hostname=A[n];BE();return d(B,A[n])
		@W.route('/get-host-name',[j])
		def m(request):return d(request,A[n])
		@W.route('/update-volume',[j])
		def m(request):B=request;global A;C=B.json();Ad(C[A0]);return d(B,A[o])
		@W.route('/get-volume',[j])
		def m(request):return d(request,A[o])
		@W.route('/update-light-string',[j])
		def m(request):
			G=' data: ';F='action: ';D=request;global A;B=D.json()
			if B[A0]=='save'or B[A0]=='clear'or B[A0]=='defaults':A[P]=B[AL];M(F+B[A0]+G+A[P]);E.write_json_file(V,A);A5();C(a);return d(D,A[P])
			if A[P]==h:A[P]=B[AL]
			else:A[P]=A[P]+','+B[AL]
			M(F+B[A0]+G+A[P]);E.write_json_file(V,A);A5();C(a);return d(D,A[P])
		@W.route('/get-light-string',[j])
		def m(request):return d(request,A[P])
		@W.route('/get-customers-sound-tracks',[j])
		def m(request):A=E.json_stringify(l);return d(request,A)
	except BF as Ab:AA=G;E.log_item(Ab)
T('web server')
import utilities as Ac
T('utilities')
def Q(seconds):
	D=seconds
	if A[y]:C=Bd(Bc,D);B.voice[0].level=C
	else:
		try:C=int(A[o])/100
		except:C=.5
		if C<0 or C>1:C=.5
		B.voice[0].level=C;B.voice[1].level=C;O.sleep(D)
def C0():global A;A[y]=J;A[n]=BP;A[F]=AK;A[o]=30;BA()
def BA():global A;A[P]='cane-4,cane-4,cane-4,cane-4,cane-4,cane-4,grandtree-21'
def Ad(action):
	D=action;B=int(A[o])
	if D=='lower1':B-=1
	if D=='lower10':B-=10
	if D=='raise10':B+=10
	if D=='raise1':B+=1
	if B>100:B=100
	if B<1:B=1
	A[o]=v(B);A[y]=G;E.write_json_file(V,A);C('/sd/menu_voice_commands/volume.wav');AI(A[o],G)
def C(file_name):
	if B.voice[0].playing:
		B.voice[0].stop()
		while B.voice[0].playing:Q(.02)
	A=c.WaveFile(f(file_name,g));B.voice[0].play(A,loop=G)
	while B.voice[0].playing:C1()
def CO():
	B.voice[0].stop()
	while B.voice[0].playing:0
def C1():
	Q(.02);H.update()
	if H.fell:B.voice[0].stop()
def AI(str_to_speak,addLocal):
	for A in str_to_speak:
		try:
			if A==' ':A='space'
			if A=='-':A='dash'
			if A=='.':A='dot'
			C(i+A+S)
		except:M('invalid character in string to speak')
	if addLocal:C(BQ);C(BR)
def C2():C('/sd/menu_voice_commands/sound_selection_menu.wav');u()
def C3():C('/sd/menu_voice_commands/choose_my_sounds_menu.wav');u()
def u():C('/sd/menu_voice_commands/press_left_button_right_button.wav')
def C4():C('/sd/menu_voice_commands/main_menu.wav');u()
def C5():C('/sd/menu_voice_commands/add_sounds_animate.wav');u()
def A6():C('/sd/menu_voice_commands/web_menu.wav');u()
def C6():C('/sd/menu_voice_commands/volume_settings_menu.wav');u()
def C7():C('/sd/menu_voice_commands/light_string_setup_menu.wav');u()
def C8():C('/sd/menu_voice_commands/park_string_instructions.wav')
def BB():C(Aq)
def BC(play_intro):
	if play_intro:C('/sd/menu_voice_commands/current_light_settings_are.wav')
	B=A[P].split(',')
	for(D,E)in enumerate(B):C('/sd/menu_voice_commands/position.wav');C(i+v(D+1)+S);C('/sd/menu_voice_commands/is.wav');C(i+E+S)
def C9():
	C('/sd/menu_voice_commands/no_user_sountrack_found.wav')
	while J:
		H.update();L.update()
		if H.fell:break
		if L.fell:C(BS);break
def R(file_name):
	F='Sound file: ';E='Random sound file: ';C=file_name;M(C);A=C
	if C==Aj:D=U(r)-4;B=K.randint(0,D);A=r[B];M(E+r[B]);M(F+A)
	elif C==Ak:D=U(l)-1;B=K.randint(0,D);A=l[B];M(E+l[B]);M(F+A)
	elif C==AK:D=U(A3)-4;B=K.randint(0,D);A=A3[B];M(E+A3[B]);M(F+A)
	if b:CB(A)
	else:CA(A)
	T('animation finished')
def CA(file_name):
	D=file_name;global b;P=1;R=3
	if D==Al:P=3;R=3
	T=w in D
	if T:
		D=D.replace(w,h)
		try:V=E.read_json_file(AM+D+x)
		except:
			C('/sd/menu_voice_commands/no_timestamp_file_found.wav')
			while J:
				H.update();L.update()
				if H.fell:b=G;return
				if L.fell:b=J;C(Am);return
	else:V=E.read_json_file(A8+D+x)
	N=V[AN];Z=U(N);F=0
	if T:W=c.WaveFile(f(AM+D+S,g))
	else:W=c.WaveFile(f(A8+D+S,g))
	B.voice[0].play(W,loop=G);a=O.monotonic();A=0
	while J:
		X=0;Y=O.monotonic()-a
		if F<U(N)-2:I=N[F+1]-N[F]-.25
		else:I=.25
		if I<0:I=0
		if Y>N[F]-.25:
			M('time elasped: '+v(Y)+' Timestamp: '+v(N[F]));F+=1;A=K.randint(P,R)
			while A==X:M('regenerating random selection');A=K.randint(P,R)
			if A==1:CC(.005,I)
			elif A==2:BD(.01);Q(I)
			elif A==3:CD(I)
			elif A==4:CE(I)
			elif A==5:BD(I)
			X=A
		if Z==F:F=0
		H.update()
		if H.fell:B.voice[0].stop()
		if not B.voice[0].playing:break
		Q(.001)
def CB(file_name):
	A=file_name;M('time stamp mode');global b;H=w in A;F=E.read_json_file('/sd/time_stamp_defaults/timestamp_mode.json');F[AN]=[];A=A.replace(w,h)
	if H:I=c.WaveFile(f(AM+A+S,g))
	else:I=c.WaveFile(f(A8+A+S,g))
	B.voice[0].play(I,loop=G);N=O.monotonic();Q(.1)
	while J:
		K=O.monotonic()-N;L.update()
		if L.fell:F[AN].append(K);M(K)
		if not B.voice[0].playing:
			D.fill((0,0,0));D.show();F[AN].append(5000)
			if H:E.write_json_file(AM+A+x,F)
			else:E.write_json_file(A8+A+x,F)
			break
	b=G;C('/sd/menu_voice_commands/timestamp_saved.wav');C(An);C(BT)
def CP():D.brightness=z;A=K.randint(0,255);B=K.randint(0,255);C=K.randint(0,255);D.fill((A,B,C));D.show()
def CC(speed,duration):
	G=duration;F=speed;H=O.monotonic()
	for B in Y(0,255,1):
		for A in Y(N):C=A*256//N+B;D[A]=B4(C&255)
		D.show();Q(F);E=O.monotonic()-H
		if E>G:return
	for B in reversed(Y(0,255,1)):
		for A in Y(N):C=A*256//N+B;D[A]=B4(C&255)
		D.show();Q(F);E=O.monotonic()-H
		if E>G:return
def CD(duration):
	G=O.monotonic();D.brightness=z;A=[];A.extend(AD);A.extend(AG);A.extend(AH);E=[];E.extend(AE)
	for B in E:D[B]=255,255,255
	F=[];F.extend(AF)
	for B in F:D[B]=50,50,50
	H=K.randint(0,255);I=K.randint(0,255);L=K.randint(0,255);M(U(A))
	while J:
		for B in A:C=K.randint(0,110);N=Ae(H-C,0,255);P=Ae(I-C,0,255);R=Ae(L-C,0,255);D[B]=N,P,R;D.show()
		Q(K.uniform(.05,.1));S=O.monotonic()-G
		if S>duration:return
def CE(duration):
	F=O.monotonic();D.brightness=z
	while J:
		for G in Y(0,N):
			H=K.randint(0,255);I=K.randint(0,255);L=K.randint(0,255);A=K.randint(0,1)
			if A==0:B=H;C=0;E=0
			elif A==1:B=0;C=I;E=0
			elif A==2:B=0;C=0;E=L
			D[G]=B,C,E;D.show()
		Q(K.uniform(.2,.3));M=O.monotonic()-F
		if M>duration:return
def Ae(my_color,lower,upper):
	C=upper;B=lower;A=my_color
	if A<B:A=B
	if A>C:A=C
	return A
def BD(duration):
	F=O.monotonic();D.brightness=z
	while J:
		for G in Y(0,N):
			H=K.randint(128,255);I=K.randint(128,255);L=K.randint(128,255);A=K.randint(0,2)
			if A==0:B=H;C=0;E=0
			elif A==1:B=0;C=I;E=0
			elif A==2:B=0;C=0;E=L
			D[G]=B,C,E;D.show()
		Q(K.uniform(.2,.3));M=O.monotonic()-F
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
class I:
	def __init__(A):0
	@k
	def name(self):return h
	def enter(A,machine):0
	def exit(A,machine):0
	def update(B,machine):
		A=machine
		if H.fell:A.paused_state=A.state.name;A.pause();return G
		return J
class CG(I):
	def __init__(A):0
	@k
	def name(self):return X
	def enter(A,machine):C(BT);E.log_item('Entered base state');I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		global q;B=Ac.switch_state(H,L,Q,3.)
		if B==BU:
			if q:q=G;C(BK)
			else:q=J;C(BJ)
		elif B==Ar or q:R(A[F])
		elif B==As:machine.go_to_state(Ag)
class CH(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Ag
	def enter(A,machine):E.log_item('Main menu');C4();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(A,machine):
		D=machine;H.update();L.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AT[A.menuIndex]+S);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>U(AT)-1:A.menuIndex=0
		if L.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				E=AT[A.selectedMenuIndex]
				if E==At:D.go_to_state(At)
				elif E==Au:D.go_to_state(Au)
				elif E==Av:D.go_to_state(Av)
				elif E==Aw:D.go_to_state(Aw)
				elif E==AJ:D.go_to_state(AJ)
				elif E==A7:D.go_to_state(A7)
				else:C(a);D.go_to_state(X)
class CI(I):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@k
	def name(self):return At
	def enter(A,machine):
		M(BV)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:E.log_item(BW);C2()
		I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(C,machine):
		H.update();L.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				D=c.WaveFile(f('/sd/christmas_park_options_voice_commands/option_'+r[C.optionIndex]+S,g));B.voice[0].play(D,loop=G);C.currentOption=C.optionIndex;C.optionIndex+=1
				if C.optionIndex>U(r)-1:C.optionIndex=0
				while B.voice[0].playing:0
		if L.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				A[F]=r[C.currentOption];E.write_json_file(V,A);D=c.WaveFile(f(Aq,g));B.voice[0].play(D,loop=G)
				while B.voice[0].playing:0
			machine.go_to_state(X)
class CJ(I):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@k
	def name(self):return Au
	def enter(A,machine):
		M(BV)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:E.log_item(BW);C3()
		I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(C,machine):
		D=machine;H.update();L.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				try:
					I=l[C.optionIndex].replace(w,h);AI(I,G);C.currentOption=C.optionIndex;C.optionIndex+=1
					if C.optionIndex>U(l)-1:C.optionIndex=0
					while B.voice[0].playing:0
				except:C9();D.go_to_state(X);return
		if L.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				try:
					A[F]=l[C.currentOption];E.write_json_file(V,A);J=c.WaveFile(f(Aq,g));B.voice[0].play(J,loop=G)
					while B.voice[0].playing:0
				except:M('no sound track')
			D.go_to_state(X)
class CK(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return A7
	def enter(A,machine):E.log_item(A7);C5();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(A,machine):
		E=machine;global b;H.update();L.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AX[A.menuIndex]+S);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>U(AX)-1:A.menuIndex=0
		if L.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				D=AX[A.selectedMenuIndex]
				if D=='hear_instructions':C(BS)
				elif D==BL:b=J;C(BM);C(Am);E.go_to_state(X)
				elif D==BN:b=G;C(An)
				else:C(a);E.go_to_state(X)
class CL(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return AJ
	def enter(A,machine):E.log_item(Ax);C6();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		F=machine;H.update();L.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AW[D.menuIndex]+S);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>U(AW)-1:D.menuIndex=0
		if L.fell:
			I=AW[D.selectedMenuIndex]
			if I=='volume_level_adjustment':
				C('/sd/menu_voice_commands/volume_adjustment_menu.wav')
				while J:
					K=Ac.switch_state(H,L,Q,3.)
					if K==Ar:Ad('lower')
					elif K==As:Ad('raise')
					elif K==BX:E.write_json_file(V,A);C(a);F.go_to_state(X);break
					Q(.1)
			elif I==Ao:
				A[y]=G
				if A[o]==0:A[o]=10
				E.write_json_file(V,A);C(a);F.go_to_state(X)
			elif I==Ap:A[y]=J;E.write_json_file(V,A);C(a);F.go_to_state(X)
class CM(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Aw
	def enter(A,machine):E.log_item(Ax);A6();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		H.update();L.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AU[D.menuIndex]+S);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>U(AU)-1:D.menuIndex=0
		if L.fell:
			F=AU[D.selectedMenuIndex]
			if F=='web_on':A[Af]=J;BB();A6()
			elif F=='web_off':A[Af]=G;BB();A6()
			elif F=='hear_url':AI(A[n],J);A6()
			elif F=='hear_instr_web':C('/sd/menu_voice_commands/web_instruct.wav');A6()
			else:E.write_json_file(V,A);C(a);machine.go_to_state(X)
class CN(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0;A.lightIndex=0;A.selectedLightIndex=0
	@k
	def name(self):return Av
	def enter(A,machine):E.log_item(Ax);C7();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		K=machine;H.update();L.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AV[D.menuIndex]+S);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>U(AV)-1:D.menuIndex=0
		if L.fell:
			F=AV[D.selectedMenuIndex]
			if F=='hear_light_setup_instructions':C8()
			elif F=='reset_lights_defaults':BA();C('/sd/menu_voice_commands/lights_reset_to.wav');BC(G)
			elif F=='hear_current_light_settings':BC(J)
			elif F=='clear_light_string':A[P]=h;C('/sd/menu_voice_commands/lights_cleared.wav')
			elif F=='add_lights':
				C('/sd/menu_voice_commands/add_light_menu.wav');M=J
				while M:
					I=Ac.switch_state(H,L,Q,3.)
					if I==Ar:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							D.lightIndex-=1
							if D.lightIndex<0:D.lightIndex=U(s)-1
							D.selectedLightIndex=D.lightIndex;C(i+s[D.lightIndex]+S)
					elif I==As:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							D.lightIndex+=1
							if D.lightIndex>U(s)-1:D.lightIndex=0
							D.selectedLightIndex=D.lightIndex;C(i+s[D.lightIndex]+S)
					elif I==BX:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							if A[P]==h:A[P]=s[D.selectedLightIndex]
							else:A[P]=A[P]+','+s[D.selectedLightIndex]
							C(i+s[D.selectedLightIndex]+S);C('/sd/menu_voice_commands/added.wav')
					elif I==BU:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:E.write_json_file(V,A);C(a);A5();M=G;K.go_to_state(X)
					Q(.1)
			else:E.write_json_file(V,A);C(a);A5();K.go_to_state(X)
class CQ(I):
	def __init__(A):super().__init__()
	@k
	def name(self):return'example'
	def enter(A,machine):I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(A,machine):I.update(A,machine)
e=CF()
e.add_state(CG())
e.add_state(CH())
e.add_state(CI())
e.add_state(CJ())
e.add_state(CK())
e.add_state(CL())
e.add_state(CM())
e.add_state(CN())
A1.value=J
Q(.5)
def BE():
	C('/sd/menu_voice_commands/animator_available_on_network.wav');C('/sd/menu_voice_commands/to_access_type.wav')
	if A[n]==BP:C('/sd/menu_voice_commands/animator_dash_christmas_dash_park.wav');C(BQ);C(BR)
	else:AI(A[n],J)
	C('/sd/menu_voice_commands/in_your_browser.wav')
if AA:
	E.log_item('starting server...')
	try:W.start(v(t.radio.ipv4_address));E.log_item('Listening on http://%s:80'%t.radio.ipv4_address);BE()
	except OSError:O.sleep(5);E.log_item('restarting...');Bb()
e.go_to_state(X)
E.log_item('animator has started...')
T('animations started.')
while J:
	e.update();Q(.02)
	if AA:
		try:W.poll()
		except BF as Ab:E.log_item(Ab);continue