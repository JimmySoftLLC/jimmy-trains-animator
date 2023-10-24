BZ='right_held'
BY='Choose sounds menu'
BX='Select a program option'
BW='left_held'
BV='/sd/menu_voice_commands/animations_are_now_active.wav'
BU='/sd/menu_voice_commands/no_timestamp_file_found.wav'
BT='/sd/menu_voice_commands/create_sound_track_files.wav'
BS='/sd/menu_voice_commands/local.wav'
BR='/sd/menu_voice_commands/dot.wav'
BQ='animator-christmas-park'
BP='Utility: '
BO='timestamp_mode_off'
BN='/sd/menu_voice_commands/timestamp_mode_on.wav'
BM='timestamp_mode_on'
BL='/sd/menu_voice_commands/continuous_mode_deactivated.wav'
BK='/sd/menu_voice_commands/continuous_mode_activated.wav'
BJ='branches'
BI='ornaments'
BH='wav/no_card.wav'
BG=Exception
Ay='Set Web Options'
Ax='web_options'
Aw='light_string_setup_menu'
Av='choose_my_sounds'
Au='choose_sounds'
At='right'
As='left'
Ar='/sd/menu_voice_commands/option_selected.wav'
Aq='volume_pot_on'
Ap='volume_pot_off'
Ao='/sd/menu_voice_commands/timestamp_mode_off.wav'
An='silent_night'
Am='we_wish_you_a_merry_christmas'
Al='random_all'
Ak='random_my'
Aj='random_built_in'
Ai='utf8'
Ah='config wifi imports'
Ag='main_menu'
Af='serve_webpage'
AN='flashTime'
AM='/sd/customers_owned_music/'
AL='text'
AK='/sd/menu_voice_commands/timestamp_instructions.wav'
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
I=True
G=False
F='option_selected'
import gc,files as E
def T(collection_point):gc.collect();A=gc.mem_free();E.log_item('Point '+collection_point+' Available memory: {} bytes'.format(A))
T('Imports gc, files')
import time as O,audiocore as c,audiomixer as Ba,audiobusio as Bb,sdcardio as Az,storage as A9,busio,digitalio as p,board as Z,random as L,rtc,microcontroller as AO
from analogio import AnalogIn as Bc
from adafruit_debouncer import Debouncer as A_
def Bd():AO.on_next_reset(AO.RunMode.NORMAL);AO.reset()
T('imports')
Be=Bc(Z.A0)
def Bf(pin,wait_for):
	B=wait_for/10;A=0
	for C in Y(10):O.sleep(B);A+=1;A=A/10
	return pin.value/65536
A1=p.DigitalInOut(Z.GP28)
A1.direction=p.Direction.OUTPUT
A1.value=G
Bg=Z.GP6
Bh=Z.GP7
AP=p.DigitalInOut(Bg)
AP.direction=p.Direction.INPUT
AP.pull=p.Pull.UP
H=A_(AP)
AQ=p.DigitalInOut(Bh)
AQ.direction=p.Direction.INPUT
AQ.pull=p.Pull.UP
K=A_(AQ)
Bi=Z.GP18
Bj=Z.GP19
Bk=Z.GP20
Bl=Bb.I2SOut(bit_clock=Bi,word_select=Bj,data=Bk)
A1.value=I
Bm=Z.GP2
Bn=Z.GP3
Bo=Z.GP4
B0=Z.GP5
B1=busio.SPI(Bm,Bn,Bo)
Bp=2
B=Ba.Mixer(voice_count=Bp,sample_rate=22050,channel_count=2,bits_per_sample=16,samples_signed=I,buffer_size=4096)
Bl.play(B)
B2=.2
B.voice[0].level=B2
B.voice[1].level=B2
try:AR=Az.SDCard(B1,B0);AS=A9.VfsFat(AR);A9.mount(AS,'/sd')
except:
	A2=c.WaveFile(f(BH,g));B.voice[0].play(A2,loop=G)
	while B.voice[0].playing:0
	B3=G
	while not B3:
		H.update()
		if H.fell:
			try:
				AR=Az.SDCard(B1,B0);AS=A9.VfsFat(AR);A9.mount(AS,'/sd');B3=I;A2=c.WaveFile(f('/sd/menu_voice_commands/micro_sd_card_success.wav',g));B.voice[0].play(A2,loop=G)
				while B.voice[0].playing:0
			except:
				A2=c.WaveFile(f(BH,g));B.voice[0].play(A2,loop=G)
				while B.voice[0].playing:0
A1.value=G
Bq=rtc.RTC()
Bq.datetime=O.struct_time((2019,5,29,15,14,15,0,-1,-1))
A=E.read_json_file(V)
r=A['options']
l=E.return_directory(w,'/sd/customers_owned_music',S)
A3=[]
A3.extend(r)
A3.extend(l)
Br=E.return_directory(h,'/sd/time_stamp_defaults',x)
AA=A[Af]
Bs=E.read_json_file('/sd/menu_voice_commands/main_menu.json')
AT=Bs[Ag]
Bt=E.read_json_file('/sd/menu_voice_commands/web_menu.json')
AU=Bt['web_menu']
Bu=E.read_json_file('/sd/menu_voice_commands/light_string_menu.json')
AV=Bu['light_string_menu']
Bv=E.read_json_file('/sd/menu_voice_commands/light_options.json')
s=Bv['light_options']
Bw=E.read_json_file('/sd/menu_voice_commands/volume_settings.json')
AW=Bw[AJ]
Bx=E.read_json_file('/sd/menu_voice_commands/add_sounds_animate.json')
AX=Bx[A7]
T('config setup')
q=G
b=G
import neopixel as B4
from rainbowio import colorwheel as B5
AB=[]
AC=[]
AD=[]
AE=[]
AF=[]
AG=[]
AH=[]
N=0
D=B4.NeoPixel(Z.GP10,N)
def AY(part):
	C=part;B=[]
	for E in AB:
		for A in E:D=A;break
		if C==BI:
			for A in Y(0,7):B.append(A+D)
		if C=='star':
			for A in Y(7,14):B.append(A+D)
		if C==BJ:
			for A in Y(14,21):B.append(A+D)
	return B
def B6(part):
	B=[]
	for D in AC:
		for A in D:C=A;break
		if part=='end':
			for A in Y(0,2):B.append(A+C)
		if part=='start':
			for A in Y(2,4):B.append(A+C)
	return B
def A4():D.show();O.sleep(.3);D.fill((0,0,0));D.show()
def By():
	global AD,AE,AF,AG,AH;AD=AY(BI);AE=AY('star');AF=AY(BJ);AG=B6('start');AH=B6('end');A=0
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
	M('Number of pixels total: ',N);D.deinit();T('Deinit ledStrip');D=B4.NeoPixel(Z.GP10,N);D.auto_write=G;D.brightness=z;By()
A5()
T('Neopixels setup')
if AA:
	import socketpool as Bz,mdns;T(Ah);import wifi as t;T(Ah);from adafruit_httpserver import Server,Request,FileResponse as AZ,Response as d,POST as j;T(Ah);E.log_item('Connecting to WiFi');B7='jimmytrainsguest';B8=h
	try:B9=E.read_json_file('/sd/env.json');B7=B9['WIFI_SSID'];B8=B9['WIFI_PASSWORD'];T('wifi env');M('Using env ssid and password')
	except:M('Using default ssid and password')
	try:
		t.radio.connect(B7,B8);T('wifi connect');Aa=mdns.Server(t.radio);Aa.hostname=A[n];Aa.advertise_service(service_type='_http',protocol='_tcp',port=80);B_=[hex(A)for A in t.radio.mac_address];E.log_item('My MAC addr:'+v(B_));C0=v(t.radio.ipv4_address);E.log_item('My IP address is'+C0);E.log_item('Connected to WiFi');C1=Bz.SocketPool(t.radio);W=Server(C1,'/static',debug=I);T('wifi server')
		@W.route('/')
		def BA(request):T('Home page.');return AZ(request,'index.html','/')
		@W.route('/mui.min.css')
		def BA(request):return AZ(request,'mui.min.css','/')
		@W.route('/mui.min.js')
		def BA(request):return AZ(request,'mui.min.js','/')
		@W.route('/animation',[j])
		def m(request):
			U='auld_lang_syne_jazzy_version';T='joy_to_the_world';S='away_in_a_manger';Q='jingle_bells_orchestra';P='the_wassail_song';O='deck_the_halls_jazzy_version';N='dance_of_the_sugar_plum_fairy';M='carol_of_the_bells';L='joyful_snowman';K='angels_we_have_heard_on_high';D=request;global A;global q;global b;B=D.raw_request.decode(Ai)
			if Aj in B:A[F]=Aj;R(A[F])
			elif Ak in B:A[F]=Ak;R(A[F])
			elif Al in B:A[F]=Al;R(A[F])
			elif Am in B:A[F]=Am;R(A[F])
			elif K in B:A[F]=K;R(A[F])
			elif L in B:A[F]=L;R(A[F])
			elif M in B:A[F]=M;R(A[F])
			elif N in B:A[F]=N;R(A[F])
			elif O in B:A[F]=O;R(A[F])
			elif P in B:A[F]=P;R(A[F])
			elif Q in B:A[F]=Q;R(A[F])
			elif S in B:A[F]=S;R(A[F])
			elif T in B:A[F]=T;R(A[F])
			elif An in B:A[F]=An;R(A[F])
			elif U in B:A[F]=U;R(A[F])
			elif w in B:
				for H in l:
					if H in B:A[F]=H;R(A[F]);break
			elif'cont_mode_on'in B:q=I;C(BK)
			elif'cont_mode_off'in B:q=G;C(BL)
			elif BM in B:b=I;C(BN);C(AK)
			elif BO in B:b=G;C(Ao)
			elif'reset_animation_timing_to_defaults'in B:
				for J in Br:V=E.read_json_file('/sd/time_stamp_defaults/'+J+x);E.write_json_file(A8+J+x,V)
			return d(D,'Animation '+A[F]+' started.')
		@W.route('/utilities',[j])
		def m(request):
			J='reset_to_defaults';H='speaker_test';F=request;global A;B=h;D=F.raw_request.decode(Ai)
			if H in D:B=H;C('/sd/menu_voice_commands/left_speaker_right_speaker.wav')
			elif Ap in D:B=Ap;A[y]=G;E.write_json_file(V,A);C(a)
			elif Aq in D:B=Aq;A[y]=I;E.write_json_file(V,A);C(a)
			elif J in D:B=J;C2();E.write_json_file(V,A);C(a);e.go_to_state(X)
			return d(F,BP+B)
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
			return d(E,BP+B)
		@W.route('/update-host-name',[j])
		def m(request):B=request;global A;C=B.json();A[n]=C[AL];E.write_json_file(V,A);Aa.hostname=A[n];BF();return d(B,A[n])
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
	except BG as Ab:AA=G;E.log_item(Ab)
T('web server')
import utilities as Ac
T('utilities')
def Q(seconds):
	D=seconds
	if A[y]:C=Bf(Be,D);B.voice[0].level=C
	else:
		try:C=int(A[o])/100
		except:C=.5
		if C<0 or C>1:C=.5
		B.voice[0].level=C;B.voice[1].level=C;O.sleep(D)
def C2():global A;A[y]=I;A[n]=BQ;A[F]=Am;A[o]=30;BB()
def BB():global A;A[P]='cane-4,cane-4,cane-4,cane-4,cane-4,cane-4,grandtree-21'
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
	while B.voice[0].playing:C3()
def CQ():
	B.voice[0].stop()
	while B.voice[0].playing:0
def C3():
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
	if addLocal:C(BR);C(BS)
def C4():C('/sd/menu_voice_commands/sound_selection_menu.wav');u()
def C5():C('/sd/menu_voice_commands/choose_my_sounds_menu.wav');u()
def u():C('/sd/menu_voice_commands/press_left_button_right_button.wav')
def C6():C('/sd/menu_voice_commands/main_menu.wav');u()
def C7():C('/sd/menu_voice_commands/add_sounds_animate.wav');u()
def A6():C('/sd/menu_voice_commands/web_menu.wav');u()
def C8():C('/sd/menu_voice_commands/volume_settings_menu.wav');u()
def C9():C('/sd/menu_voice_commands/light_string_setup_menu.wav');u()
def CA():C('/sd/menu_voice_commands/park_string_instructions.wav')
def BC():C(Ar)
def BD(play_intro):
	if play_intro:C('/sd/menu_voice_commands/current_light_settings_are.wav')
	B=A[P].split(',')
	for(D,E)in enumerate(B):C('/sd/menu_voice_commands/position.wav');C(i+v(D+1)+S);C('/sd/menu_voice_commands/is.wav');C(i+E+S)
def CB():
	C('/sd/menu_voice_commands/no_user_sountrack_found.wav')
	while I:
		H.update();K.update()
		if H.fell:break
		if K.fell:C(BT);break
def R(file_name):
	F='Sound file: ';E='Random sound file: ';C=file_name;M(C);A=C
	if C==Aj:D=U(r)-1;B=L.randint(0,D);A=r[B];M(E+r[B]);M(F+A)
	elif C==Ak:D=U(l)-1;B=L.randint(0,D);A=l[B];M(E+l[B]);M(F+A)
	elif C==Al:D=U(A3)-1;B=L.randint(0,D);A=A3[B];M(E+A3[B]);M(F+A)
	if b:CD(A)
	else:CC(A)
	T('animation finished')
def CC(file_name):
	D=file_name;global b;P=1;R=3
	if D==An:P=3;R=3
	T=w in D
	if T:
		D=D.replace(w,h)
		try:V=E.read_json_file(AM+D+x)
		except:
			C(BU)
			while I:
				H.update();K.update()
				if H.fell:b=G;return
				if K.fell:b=I;C(AK);return
	else:V=E.read_json_file(A8+D+x)
	N=V[AN];Z=U(N);F=0
	if T:W=c.WaveFile(f(AM+D+S,g))
	else:W=c.WaveFile(f(A8+D+S,g))
	B.voice[0].play(W,loop=G);a=O.monotonic();A=0
	while I:
		X=0;Y=O.monotonic()-a
		if F<U(N)-2:J=N[F+1]-N[F]-.25
		else:J=.25
		if J<0:J=0
		if Y>N[F]-.25:
			M('time elasped: '+v(Y)+' Timestamp: '+v(N[F]));F+=1;A=L.randint(P,R)
			while A==X:M('regenerating random selection');A=L.randint(P,R)
			if A==1:CE(.005,J)
			elif A==2:BE(.01);Q(J)
			elif A==3:CF(J)
			elif A==4:CG(J)
			elif A==5:BE(J)
			X=A
		if Z==F:F=0
		H.update()
		if H.fell:B.voice[0].stop()
		if not B.voice[0].playing:break
		Q(.001)
def CD(file_name):
	A=file_name;M('time stamp mode');global b;H=w in A;F=E.read_json_file('/sd/time_stamp_defaults/timestamp_mode.json');F[AN]=[];A=A.replace(w,h)
	if H:J=c.WaveFile(f(AM+A+S,g))
	else:J=c.WaveFile(f(A8+A+S,g))
	B.voice[0].play(J,loop=G);N=O.monotonic();Q(.1)
	while I:
		L=O.monotonic()-N;K.update()
		if K.fell:F[AN].append(L);M(L)
		if not B.voice[0].playing:
			D.fill((0,0,0));D.show();F[AN].append(5000)
			if H:E.write_json_file(AM+A+x,F)
			else:E.write_json_file(A8+A+x,F)
			break
	b=G;C('/sd/menu_voice_commands/timestamp_saved.wav');C(Ao);C(BV)
def CR():D.brightness=z;A=L.randint(0,255);B=L.randint(0,255);C=L.randint(0,255);D.fill((A,B,C));D.show()
def CE(speed,duration):
	G=duration;F=speed;H=O.monotonic()
	for B in Y(0,255,1):
		for A in Y(N):C=A*256//N+B;D[A]=B5(C&255)
		D.show();Q(F);E=O.monotonic()-H
		if E>G:return
	for B in reversed(Y(0,255,1)):
		for A in Y(N):C=A*256//N+B;D[A]=B5(C&255)
		D.show();Q(F);E=O.monotonic()-H
		if E>G:return
def CF(duration):
	G=O.monotonic();D.brightness=z;A=[];A.extend(AD);A.extend(AG);A.extend(AH);E=[];E.extend(AE)
	for B in E:D[B]=255,255,255
	F=[];F.extend(AF)
	for B in F:D[B]=50,50,50
	H=L.randint(0,255);J=L.randint(0,255);K=L.randint(0,255);M(U(A))
	while I:
		for B in A:C=L.randint(0,110);N=Ae(H-C,0,255);P=Ae(J-C,0,255);R=Ae(K-C,0,255);D[B]=N,P,R;D.show()
		Q(L.uniform(.05,.1));S=O.monotonic()-G
		if S>duration:return
def CG(duration):
	F=O.monotonic();D.brightness=z
	while I:
		for G in Y(0,N):
			H=L.randint(0,255);J=L.randint(0,255);K=L.randint(0,255);A=L.randint(0,1)
			if A==0:B=H;C=0;E=0
			elif A==1:B=0;C=J;E=0
			elif A==2:B=0;C=0;E=K
			D[G]=B,C,E;D.show()
		Q(L.uniform(.2,.3));M=O.monotonic()-F
		if M>duration:return
def Ae(my_color,lower,upper):
	C=upper;B=lower;A=my_color
	if A<B:A=B
	if A>C:A=C
	return A
def BE(duration):
	F=O.monotonic();D.brightness=z
	while I:
		for G in Y(0,N):
			H=L.randint(128,255);J=L.randint(128,255);K=L.randint(128,255);A=L.randint(0,2)
			if A==0:B=H;C=0;E=0
			elif A==1:B=0;C=J;E=0
			elif A==2:B=0;C=0;E=K
			D[G]=B,C,E;D.show()
		Q(L.uniform(.2,.3));M=O.monotonic()-F
		if M>duration:return
class CH:
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
	@k
	def name(self):return h
	def enter(A,machine):0
	def exit(A,machine):0
	def update(B,machine):
		A=machine
		if H.fell:A.paused_state=A.state.name;A.pause();return G
		return I
class CI(J):
	def __init__(A):0
	@k
	def name(self):return X
	def enter(A,machine):C(BV);E.log_item('Entered base state');J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		global q;B=Ac.switch_state(H,K,Q,3.)
		if B==BW:
			if q:q=G;C(BL)
			else:q=I;C(BK)
		elif B==As or q:R(A[F])
		elif B==At:machine.go_to_state(Ag)
class CJ(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Ag
	def enter(A,machine):E.log_item('Main menu');C6();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(A,machine):
		D=machine;H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AT[A.menuIndex]+S);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>U(AT)-1:A.menuIndex=0
		if K.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				E=AT[A.selectedMenuIndex]
				if E==Au:D.go_to_state(Au)
				elif E==Av:D.go_to_state(Av)
				elif E=='new_feature':
					C(BU)
					while I:
						H.update();K.update()
						if H.fell:F=G;return
						if K.fell:F=I;C(AK);return
				elif E==Aw:D.go_to_state(Aw)
				elif E==Ax:D.go_to_state(Ax)
				elif E==AJ:D.go_to_state(AJ)
				elif E==A7:D.go_to_state(A7)
				else:C(a);D.go_to_state(X)
class CK(J):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@k
	def name(self):return Au
	def enter(A,machine):
		M(BX)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:E.log_item(BY);C4()
		J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(C,machine):
		H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				D=c.WaveFile(f('/sd/christmas_park_options_voice_commands/option_'+r[C.optionIndex]+S,g));B.voice[0].play(D,loop=G);C.currentOption=C.optionIndex;C.optionIndex+=1
				if C.optionIndex>U(r)-1:C.optionIndex=0
				while B.voice[0].playing:0
		if K.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				A[F]=r[C.currentOption];E.write_json_file(V,A);D=c.WaveFile(f(Ar,g));B.voice[0].play(D,loop=G)
				while B.voice[0].playing:0
			machine.go_to_state(X)
class CL(J):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@k
	def name(self):return Av
	def enter(A,machine):
		M(BX)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:E.log_item(BY);C5()
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
					I=l[C.optionIndex].replace(w,h);AI(I,G);C.currentOption=C.optionIndex;C.optionIndex+=1
					if C.optionIndex>U(l)-1:C.optionIndex=0
					while B.voice[0].playing:0
				except:CB();D.go_to_state(X);return
		if K.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				try:
					A[F]=l[C.currentOption];E.write_json_file(V,A);J=c.WaveFile(f(Ar,g));B.voice[0].play(J,loop=G)
					while B.voice[0].playing:0
				except:M('no sound track')
			D.go_to_state(X)
class CM(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return A7
	def enter(A,machine):E.log_item(A7);C7();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(A,machine):
		E=machine;global b;H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AX[A.menuIndex]+S);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>U(AX)-1:A.menuIndex=0
		if K.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				D=AX[A.selectedMenuIndex]
				if D=='hear_instructions':C(BT)
				elif D==BM:b=I;C(BN);C(AK);E.go_to_state(X)
				elif D==BO:b=G;C(Ao)
				else:C(a);E.go_to_state(X)
class CN(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return AJ
	def enter(A,machine):E.log_item(Ay);C8();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		F=machine;H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AW[D.menuIndex]+S);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>U(AW)-1:D.menuIndex=0
		if K.fell:
			J=AW[D.selectedMenuIndex]
			if J=='volume_level_adjustment':
				C('/sd/menu_voice_commands/volume_adjustment_menu.wav')
				while I:
					L=Ac.switch_state(H,K,Q,3.)
					if L==As:Ad('lower')
					elif L==At:Ad('raise')
					elif L==BZ:E.write_json_file(V,A);C(a);F.go_to_state(X);break
					Q(.1)
			elif J==Ap:
				A[y]=G
				if A[o]==0:A[o]=10
				E.write_json_file(V,A);C(a);F.go_to_state(X)
			elif J==Aq:A[y]=I;E.write_json_file(V,A);C(a);F.go_to_state(X)
class CO(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Ax
	def enter(A,machine):E.log_item(Ay);A6();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AU[D.menuIndex]+S);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>U(AU)-1:D.menuIndex=0
		if K.fell:
			F=AU[D.selectedMenuIndex]
			if F=='web_on':A[Af]=I;BC();A6()
			elif F=='web_off':A[Af]=G;BC();A6()
			elif F=='hear_url':AI(A[n],I);A6()
			elif F=='hear_instr_web':C('/sd/menu_voice_commands/web_instruct.wav');A6()
			else:E.write_json_file(V,A);C(a);machine.go_to_state(X)
class CP(J):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0;A.lightIndex=0;A.selectedLightIndex=0
	@k
	def name(self):return Aw
	def enter(A,machine):E.log_item(Ay);C9();J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(D,machine):
		L=machine;H.update();K.update()
		if H.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AV[D.menuIndex]+S);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>U(AV)-1:D.menuIndex=0
		if K.fell:
			F=AV[D.selectedMenuIndex]
			if F=='hear_light_setup_instructions':CA()
			elif F=='reset_lights_defaults':BB();C('/sd/menu_voice_commands/lights_reset_to.wav');BD(G)
			elif F=='hear_current_light_settings':BD(I)
			elif F=='clear_light_string':A[P]=h;C('/sd/menu_voice_commands/lights_cleared.wav')
			elif F=='add_lights':
				C('/sd/menu_voice_commands/add_light_menu.wav');M=I
				while M:
					J=Ac.switch_state(H,K,Q,3.)
					if J==As:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							D.lightIndex-=1
							if D.lightIndex<0:D.lightIndex=U(s)-1
							D.selectedLightIndex=D.lightIndex;C(i+s[D.lightIndex]+S)
					elif J==At:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							D.lightIndex+=1
							if D.lightIndex>U(s)-1:D.lightIndex=0
							D.selectedLightIndex=D.lightIndex;C(i+s[D.lightIndex]+S)
					elif J==BZ:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							if A[P]==h:A[P]=s[D.selectedLightIndex]
							else:A[P]=A[P]+','+s[D.selectedLightIndex]
							C(i+s[D.selectedLightIndex]+S);C('/sd/menu_voice_commands/added.wav')
					elif J==BW:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:E.write_json_file(V,A);C(a);A5();M=G;L.go_to_state(X)
					Q(.1)
			else:E.write_json_file(V,A);C(a);A5();L.go_to_state(X)
class CS(J):
	def __init__(A):super().__init__()
	@k
	def name(self):return'example'
	def enter(A,machine):J.enter(A,machine)
	def exit(A,machine):J.exit(A,machine)
	def update(A,machine):J.update(A,machine)
e=CH()
e.add_state(CI())
e.add_state(CJ())
e.add_state(CK())
e.add_state(CL())
e.add_state(CM())
e.add_state(CN())
e.add_state(CO())
e.add_state(CP())
A1.value=I
Q(.5)
def BF():
	C('/sd/menu_voice_commands/animator_available_on_network.wav');C('/sd/menu_voice_commands/to_access_type.wav')
	if A[n]==BQ:C('/sd/menu_voice_commands/animator_dash_christmas_dash_park.wav');C(BR);C(BS)
	else:AI(A[n],I)
	C('/sd/menu_voice_commands/in_your_browser.wav')
if AA:
	E.log_item('starting server...')
	try:W.start(v(t.radio.ipv4_address));E.log_item('Listening on http://%s:80'%t.radio.ipv4_address);BF()
	except OSError:O.sleep(5);E.log_item('restarting...');Bd()
e.go_to_state(X)
E.log_item('animator has started...')
T('animations started.')
while I:
	e.update();Q(.02)
	if AA:
		try:W.poll()
		except BG as Ab:E.log_item(Ab);continue