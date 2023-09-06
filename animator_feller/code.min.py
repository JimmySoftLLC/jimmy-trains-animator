BR='move_tree_to_fallen_position'
BQ='move_tree_to_upright_position'
BP='move_feller_to_chop_position'
BO='move_feller_to_rest_position'
BN='/sd/feller_menu/to_exit_press_and_hold_button_down.wav'
BM='Dialog option cal saved.'
BL='opening_dialog_off'
BK='opening_dialog_on'
BJ=' cal saved.'
BI='Redirected to home page.'
BH='/sd/feller_menu/continuous_mode_deactivated.wav'
BG='/sd/feller_menu/continuous_mode_activated.wav'
BF='feller_girlfriend'
BE='feller_buddy'
BD='feller_poem'
BC='feller_wife'
BB='wav/micro_sd_card_not_inserted.mp3'
BA=Exception
Am='web_options'
Al='set_dialog_options'
Ak='happy_birthday'
Aj='alien'
Ai='random'
Ah='config wifi imports'
Ag='serve_webpage'
Af='main_menu'
AN='move_feller_and_tree'
AM='adjust_feller_and_tree'
AL='choose_sounds'
AF='utf8'
AE='deinit wave0'
AA='/sd/feller_menu/'
A9='feller_advice'
A8='opening_dialog'
A7=print
A3='left_held'
s='/sd/feller_menu/all_changes_complete.wav'
r='HOST_NAME'
q='/sd/config_feller.json'
i=property
h=len
g=range
a='tree_down_pos'
X='rb'
W=str
V=open
S='.wav'
R='feller_chop_pos'
P='base_state'
O='option_selected'
M='feller_rest_pos'
L=True
K='tree_up_pos'
F=False
import gc,files as D
def H(collection_point):gc.collect();A=gc.mem_free();D.log_item('Point '+collection_point+' Available memory: {} bytes'.format(A))
H('Imports gc, files')
import sdcardio as An,storage as AG,audiomp3 as AO,audiocore as b,audiomixer as BS,audiobusio as Ao,time,board as T,microcontroller as AP,busio,pwmio as Ap,digitalio as j,random as t
from analogio import AnalogIn as BT
from adafruit_motor import servo as Aq
from adafruit_debouncer import Debouncer as Ar
def As():AP.on_next_reset(AP.RunMode.NORMAL);AP.reset()
H('imports')
BU=BT(T.A0)
def BV(pin,wait_for):
	B=wait_for/10;A=0
	for C in g(10):time.sleep(B);A+=1;A=A/10
	return pin.value/65536
AB=j.DigitalInOut(T.GP28)
AB.direction=j.Direction.OUTPUT
AB.value=F
BW=Ap.PWMOut(T.GP10,duty_cycle=2**15,frequency=50)
BX=Ap.PWMOut(T.GP11,duty_cycle=2**15,frequency=50)
u=Aq.Servo(BW)
v=Aq.Servo(BX)
BY=T.GP6
BZ=T.GP7
AQ=j.DigitalInOut(BY)
AQ.direction=j.Direction.INPUT
AQ.pull=j.Pull.UP
G=Ar(AQ)
AR=j.DigitalInOut(BZ)
AR.direction=j.Direction.INPUT
AR.pull=j.Pull.UP
J=Ar(AR)
At=T.GP18
Au=T.GP19
Av=T.GP20
f=Ao.I2SOut(bit_clock=At,word_select=Au,data=Av)
AB.value=L
Ba=T.GP2
Bb=T.GP3
Bc=T.GP4
Aw=T.GP5
Ax=busio.SPI(Ba,Bb,Bc)
try:AS=An.SDCard(Ax,Aw);AT=AG.VfsFat(AS);AG.mount(AT,'/sd')
except:
	k=AO.MP3Decoder(V(BB,X));f.play(k)
	while f.playing:0
	k.deinit();H(AE);Ay=F
	while not Ay:
		G.update()
		if G.fell:
			try:
				AS=An.SDCard(Ax,Aw);AT=AG.VfsFat(AS);AG.mount(AT,'/sd');Ay=L;k=AO.MP3Decoder(V('wav/micro_sd_card_success.mp3',X));f.play(k)
				while f.playing:0
				k.deinit();H(AE)
			except:
				k=AO.MP3Decoder(V(BB,X));f.play(k)
				while f.playing:0
				k.deinit();H(AE)
f.deinit()
AB.value=F
H('deinit audio')
f=Ao.I2SOut(bit_clock=At,word_select=Au,data=Av)
Bd=2
B=BS.Mixer(voice_count=Bd,sample_rate=22050,channel_count=2,bits_per_sample=16,samples_signed=L,buffer_size=8192)
f.play(B)
H('audio setup')
import utilities as w
H('animator_feller, utilities')
A=D.read_json_file(q)
x=A[K]
l=60
m=180
if A[a]<l or A[a]>m:A[a]=l
if A[K]<l or A[K]>m:A[K]=m
y=A[M]
n=0
o=170
if A[M]<n or A[M]>o:A[M]=n
if A[R]>o or A[R]<n:A[R]=o
Be=D.read_json_file('/sd/feller_menu/main_menu.json')
AU=Be[Af]
Bf=D.read_json_file('/sd/feller_menu/choose_sounds.json')
A4=Bf[AL]
Bg=D.read_json_file('/sd/feller_dialog/feller_dialog.json')
Az=Bg['feller_dialog']
Bh=D.read_json_file('/sd/feller_wife/feller_wife.json')
Bi=Bh[BC]
Bj=D.read_json_file('/sd/feller_poem/feller_poem.json')
Bk=Bj[BD]
Bl=D.read_json_file('/sd/feller_buddy/feller_buddy.json')
Bm=Bl[BE]
Bn=D.read_json_file('/sd/feller_girlfriend/feller_girlfriend.json')
Bo=Bn[BF]
Bp=D.read_json_file('/sd/feller_menu/adjust_feller_and_tree.json')
AV=Bp[AM]
Bq=D.read_json_file('/sd/feller_menu/move_feller_and_tree.json')
AW=Bq[AN]
Br=D.read_json_file('/sd/feller_menu/dialog_selection_menu.json')
AX=Br['dialog_selection_menu']
Bs=D.read_json_file('/sd/feller_menu/web_menu.json')
AY=Bs['web_menu']
AH=A[Ag]
c=M
d=K
p=F
H('config setup')
if AH:
	import socketpool as Bt,mdns;H(Ah);import wifi as z;H(Ah);from adafruit_httpserver import Server,Request,FileResponse as AZ,Response as N,POST as A0;H(Ah);D.log_item('Connecting to WiFi');A_='jimmytrainsguest';B0=''
	try:B1=D.read_json_file('/sd/env.json');A_=B1['WIFI_SSID'];B0=B1['WIFI_PASSWORD'];H('wifi env');A7('Using env ssid and password')
	except:A7('Using default ssid and password')
	try:
		z.radio.connect(A_,B0);H('wifi connect');Aa=mdns.Server(z.radio);Aa.hostname=A[r];Aa.advertise_service(service_type='_http',protocol='_tcp',port=80);Bu=[hex(A)for A in z.radio.mac_address];D.log_item('My MAC addr:'+W(Bu));Bv=W(z.radio.ipv4_address);D.log_item('My IP address is'+Bv);D.log_item('Connected to WiFi');Bw=Bt.SocketPool(z.radio);Y=Server(Bw,'/static',debug=L);H('wifi server')
		@Y.route('/')
		def B2(request):H('Home page.');return AZ(request,'index.html','/')
		@Y.route('/mui.min.css')
		def B2(request):return AZ(request,'mui.min.css','/')
		@Y.route('/mui.min.js')
		def B2(request):return AZ(request,'mui.min.js','/')
		@Y.route('/animation',[A0])
		def A5(request):
			S='owl';R='no_sounds';P='machines';M='just_birds';K='birds_dogs';J='birds_dogs_short_version';I='train';H='halloween';G='christmas';E='forth_of_july';D=request;global A;global p;B=D.raw_request.decode(AF)
			if Ai in B:A[O]=Ai;Q()
			elif E in B:A[O]=E;Q()
			elif G in B:A[O]=G;Q()
			elif H in B:A[O]=H;Q()
			elif I in B:A[O]=I;Q()
			elif Aj in B:A[O]=Aj;Q()
			elif J in B:A[O]=J;Q()
			elif K in B:A[O]=K;Q()
			elif M in B:A[O]=M;Q()
			elif P in B:A[O]=P;Q()
			elif R in B:A[O]=R;Q()
			elif S in B:A[O]=S;Q()
			elif Ak in B:A[O]=Ak;Q()
			elif'cont_mode_on'in B:p=L;C(BG)
			elif'cont_mode_off'in B:p=F;C(BH)
			return N(D,'Animation '+A[O]+' started.')
		@Y.route('/feller',[A0])
		def A5(request):
			B=request;global A;global c;C=B.raw_request.decode(AF)
			if M in C:c=M;e(A[c],.01);return N(B,'Moved feller to rest position.')
			elif R in C:c=R;e(A[c],.01);return N(B,'Moved feller to chop position.')
			elif'feller_adjust'in C:c=M;e(A[c],.01);return N(B,'Redirected to feller-adjust page.')
			elif'feller_home'in C:return N(B,BI)
			elif'feller_clockwise'in C:Ac(u,c,1,n,o);return N(B,'Moved feller clockwise.')
			elif'feller_counter_clockwise'in C:Ad(u,c,1,n,o);return N(B,'Moved feller counter clockwise.')
			elif'feller_cal_saved'in C:Ae();Z.go_to_state(P);return N(B,'Feller '+c+BJ)
		@Y.route('/tree',[A0])
		def A5(request):
			B=request;global A;global d;C=B.raw_request.decode(AF)
			if K in C:d=K;U(A[d],.01);return N(B,'Moved tree to up position.')
			elif a in C:d=a;U(A[d],.01);return N(B,'Moved tree to fallen position.')
			elif'tree_adjust'in C:d=K;U(A[d],.01);return N(B,'Redirected to tree-adjust page.')
			elif'tree_home'in C:return N(B,BI)
			elif'tree_up'in C:Ac(v,d,-1,l,m);return N(B,'Moved tree up.')
			elif'tree_down'in C:Ad(v,d,-1,l,m);return N(B,'Moved tree down.')
			elif'tree_cal_saved'in C:Ae();Z.go_to_state(P);return N(B,'Tree '+d+BJ)
		@Y.route('/dialog',[A0])
		def A5(request):
			E=request;global A;B=E.raw_request.decode(AF)
			if BK in B:A[A8]=L
			elif BL in B:A[A8]=F
			elif'feller_advice_on'in B:A[A9]=L
			elif'feller_advice_off'in B:A[A9]=F
			D.write_json_file(q,A);C(s);return N(E,BM)
		@Y.route('/utilities',[A0])
		def A5(request):
			B=request;global A;E=B.raw_request.decode(AF)
			if'speaker_test'in E:C('/sd/feller_menu/left_speaker_right_speaker.wav')
			elif'reset_to_defaults'in E:Bx();D.write_json_file(q,A);C(s);Z.go_to_state(P)
			return N(B,BM)
		@Y.route('/update-host-name',[A0])
		def A5(request):B=request;global A;C=B.json();A[r]=C['text'];D.write_json_file(q,A);Aa.hostname=A[r];B9();return N(B,A[r])
		@Y.route('/get-host-name',[A0])
		def A5(request):return N(request,A[r])
	except BA as Ab:AH=F;D.log_item(Ab)
H('web server')
def Bx():global A;A[K]=165;A[a]=100;A[M]=0;A[R]=150;A[A8]=F;A[A9]=L
def E(seconds):A=BV(BU,seconds);B.voice[0].level=A;B.voice[1].level=A
H('global variable and methods')
def C(file_name):
	if B.voice[0].playing:
		B.voice[0].stop()
		while B.voice[0].playing:E(.02)
	A=b.WaveFile(V(file_name,X));B.voice[0].play(A,loop=F)
	while B.voice[0].playing:B3()
def By():
	B.voice[0].stop()
	while B.voice[0].playing:0
def B3():
	while L:
		E(.05);G.update()
		if G.fell:By();return
def A6():C('/sd/feller_menu/press_left_button_right_button.wav')
def A1():C('/sd/feller_menu/option_selected.wav')
def B4():C('/sd/feller_menu/now_we_can_adjust_the_feller_position.wav');C(BN)
def B5():C('/sd/feller_menu/now_we_can_adjust_the_tree_position.wav');C(BN)
def Bz():C('/sd/feller_menu/main_menu.wav');A6()
def B_():C('/sd/feller_menu/sound_selection_menu.wav');A6()
def C0():C('/sd/feller_menu/adjust_feller_and_tree_menu.wav');A6()
def C1():C('/sd/feller_menu/move_feller_and_tree_menu.wav');A6()
def AC():C('/sd/feller_menu/dialog_selection_menu.wav');A6()
def AD():C('/sd/feller_menu/web_menu.wav');A6()
def B6(min_servo_pos,max_servo_pos,servo_pos):
	B='/sd/feller_menu/limit_reached.wav';A=servo_pos
	if A<min_servo_pos:C(B);return F
	if A>max_servo_pos:C(B);return F
	return L
def B3():
	E(.02);G.update()
	if G.fell:B.voice[0].stop()
def B7(str_to_speak,addLocal):
	for A in str_to_speak:
		if A=='-':A='dash'
		if A=='.':A='dot'
		C(AA+A+S)
	if addLocal:C('/sd/feller_menu/dot.wav');C('/sd/feller_menu/local.wav')
H('dialog methods')
def Ac(servo,movement_type,sign,min_servo_pos,max_servo_pos):
	B=movement_type;global A;A[B]-=1*sign
	if B6(min_servo_pos,max_servo_pos,A[B]):servo.angle=A[B]
	else:A[B]+=1*sign
def Ad(servo,movement_type,sign,min_servo_pos,max_servo_pos):
	B=movement_type;global A;A[B]+=1*sign
	if B6(min_servo_pos,max_servo_pos,A[B]):servo.angle=A[B]
	else:A[B]-=1*sign
def Ae():C(s);global A;D.write_json_file(q,A)
def AI(servo,movement_type):
	C=servo;B=movement_type
	if B==M or B==R:D=n;H=o;I=1
	else:D=l;H=m;I=-1
	K=F
	while not K:
		C.angle=A[B];G.update();J.update()
		if G.fell:Ac(C,B,I,D,H)
		if J.fell:
			N=L;O=0
			while N:
				E(.1);J.update();O+=1
				if O>30:Ae();N=F;K=L
				if J.rose:N=F
			if not K:Ad(C,B,I,D,H)
	if B==M or B==R:global y;y=A[B]
	else:global x;x=A[B]
def e(new_position,speed):
	A=new_position;global y;B=1
	if y>A:B=-1
	for C in g(y,A,B):AJ(C);E(speed)
	AJ(A)
def U(new_position,speed):
	A=new_position;global x;B=1
	if x>A:B=-1
	for C in g(x,A,B):A2(C);E(speed)
	A2(A)
def AJ(servo_pos):
	A=servo_pos
	if A<n:A=n
	if A>o:A=o
	u.angle=A;global y;y=A
def A2(servo_pos):
	A=servo_pos
	if A<l:A=l
	if A>m:A=m
	v.angle=A;global x;x=A
def Q():C3()
H('servo helpers')
def B8():
	D=7;C=.2
	while B.voice[0].playing:
		F=w.switch_state(G,J,E,5)
		if F==A3:
			B.voice[0].stop()
			while B.voice[0].playing:0
			return
		u.angle=D+A[M];E(C);u.angle=A[M];E(C)
def C2():
	D=2;C=.2
	while B.voice[0].playing:
		F=w.switch_state(G,J,E,5)
		if F==A3:
			B.voice[0].stop()
			while B.voice[0].playing:0
			return
		v.angle=A[K];E(C);v.angle=A[K]-D;E(C)
def AK(sound_files,folder):
	C=folder;A=sound_files;L=h(A)-1;I=t.randint(0,L);D.log_item(C+': '+W(I));K=b.WaveFile(V('/sd/'+C+'/'+A[I]+S,X));B.voice[0].play(K,loop=F)
	while B.voice[0].playing:
		E(.1);M=w.switch_state(G,J,E,5)
		if M==A3:
			B.voice[0].stop()
			while B.voice[0].playing:0
	K.deinit();H(AE)
def C3():
	p='Sound file: ';o='/sd/feller_sounds/sounds_';i='/sd/feller_menu/animation_canceled.wav';E(.05)
	if A[A8]:
		Y=t.randint(0,3)
		if Y==0:AK(Bi,BC)
		if Y==1:AK(Bm,BE)
		if Y==2:AK(Bk,BD)
		if Y==3:AK(Bo,BF)
	P=1;Z=t.randint(2,7);d=h(Az)-1;j=t.randint(0,d);k=t.randint(2,Z);D.log_item('Chop total: '+W(Z)+' what to speak: '+W(j)+' when to speak: '+W(k));l=F;q=A[K]-3;N=A[O]
	if N==Ai:d=h(A4)-2;Q=t.randint(0,d);N=A4[Q];A7('Random sound file: '+A4[Q])
	if N==Ak:Q=t.randint(0,6);I=o+N+W(Q)+S;A7(p+N+W(Q))
	else:I=o+N+S;A7(p+N)
	m=b.WaveFile(V(I,X))
	while P<=Z:
		if k==P and not l and A[A9]:l=L;I='/sd/feller_dialog/'+Az[j]+S;C=b.WaveFile(V(I,X));B.voice[0].play(C,loop=F);B8();C.deinit();H(AE)
		C=b.WaveFile(V('/sd/feller_chops/chop'+W(P)+S,X));P+=1
		for c in g(A[M],A[R]+5,10):
			AJ(c)
			if c>=A[R]-10:
				B.voice[0].play(C,loop=F);f=2;E(.2)
				for r in g(f):A2(q);E(.1);A2(A[K]);E(.1)
				break
		if P<=Z:
			for c in g(A[R],A[M],-5):AJ(c);E(.02)
	while B.voice[0].playing:E(.1)
	B.voice[0].play(m,loop=F)
	for s in g(A[K],A[a],-5):A2(s);E(.06)
	f=8
	for r in g(f):A2(A[a]);E(.1);A2(7+A[a]);E(.1)
	if N==Aj:
		A7('Alien sequence starting....');E(2);e(A[M],.01);U(A[K],.01);u=A[K];v=A[K]-8
		while B.voice[0].playing:
			T=w.switch_state(G,J,E,5)
			if T==A3:
				B.voice[0].stop()
				while B.voice[0].playing:0
				I=i;C=b.WaveFile(V(I,X));B.voice[0].play(C,loop=F)
				while B.voice[0].playing:0
				break
			U(u,.1);U(v,.1)
		U(A[K],.04)
		for n in g(7):
			I='/sd/feller_alien/human_'+W(n+1)+S;C=b.WaveFile(V(I,X));B.voice[0].play(C,loop=F);B8();I='/sd/feller_alien/alien_'+W(n+1)+S;C=b.WaveFile(V(I,X));B.voice[0].play(C,loop=F);C2();T=w.switch_state(G,J,E,5)
			if T==A3:
				B.voice[0].stop()
				while B.voice[0].playing:0
				I=i;C=b.WaveFile(V(I,X));B.voice[0].play(C,loop=F)
				while B.voice[0].playing:0
				break
	else:
		while B.voice[0].playing:
			T=w.switch_state(G,J,E,5)
			if T==A3:
				B.voice[0].stop()
				while B.voice[0].playing:0
				I=i;C=b.WaveFile(V(I,X));B.voice[0].play(C,loop=F)
				while B.voice[0].playing:0
				break
	C.deinit();m.deinit();H('deinit wave0 wave1');e(A[M],.01);E(.02);U(A[K],.01)
class C4:
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
	def reset(A):As()
class I:
	def __init__(A):0
	@i
	def name(self):return''
	def enter(A,machine):0
	def exit(A,machine):0
	def update(B,machine):
		A=machine
		if G.fell:A.paused_state=A.state.name;A.pause();return F
		return L
class C5(I):
	def __init__(A):0
	@i
	def name(self):return P
	def enter(F,machine):
		E(.1)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:e(A[M],.01);U(A[K],.01);C('/sd/feller_menu/animations_are_now_active.wav')
		D.log_item('Entered base state');I.enter(F,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(B,machine):
		global p;A=w.switch_state(G,J,E,30)
		if A==A3:
			if p:p=F;C(BH)
			else:p=L;C(BG)
		elif A=='left'or p:Q()
		elif A=='right':machine.go_to_state(Af)
class C6(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@i
	def name(self):return AN
	def enter(A,machine):D.log_item('Move feller and tree menu');C1();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(B,machine):
		G.update();J.update()
		if G.fell:
			C(AA+AW[B.menuIndex]+S);B.selectedMenuIndex=B.menuIndex;B.menuIndex+=1
			if B.menuIndex>h(AW)-1:B.menuIndex=0
		if J.fell:
			D=AW[B.selectedMenuIndex]
			if D==BO:e(A[M],.01)
			elif D==BP:e(A[R],.01)
			elif D==BQ:U(A[K],.01)
			elif D==BR:U(A[a],.01)
			else:C(s);machine.go_to_state(P)
class C7(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@i
	def name(self):return AM
	def enter(A,machine):D.log_item('Adjust feller and tree menu');C0();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		E=machine;G.update();J.update()
		if G.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(AA+AV[D.menuIndex]+S);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>h(AV)-1:D.menuIndex=0
		if J.fell:
			F=AV[D.selectedMenuIndex]
			if F==BO:e(A[M],.01);B4();AI(u,M);E.go_to_state(P)
			elif F==BP:e(A[R],.01);B4();AI(u,R);E.go_to_state(P)
			elif F==BQ:U(A[K],.01);B5();AI(v,K);E.go_to_state(P)
			elif F==BR:U(A[a],.01);B5();AI(v,a);E.go_to_state(P)
			else:C(s);E.go_to_state(P)
class C8(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@i
	def name(self):return Al
	def enter(A,machine):D.log_item('Set Dialog Options');AC();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(E,machine):
		G.update();J.update()
		if G.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(AA+AX[E.menuIndex]+S);E.selectedMenuIndex=E.menuIndex;E.menuIndex+=1
				if E.menuIndex>h(AX)-1:E.menuIndex=0
		if J.fell:
			H=AX[E.selectedMenuIndex]
			if H==BK:A[A8]=L;A1();AC()
			elif H==BL:A[A8]=F;A1();AC()
			elif H=='lumberjack_advice_on':A[A9]=L;A1();AC()
			elif H=='lumberjack_advice_off':A[A9]=F;A1();AC()
			else:D.write_json_file(q,A);C(s);machine.go_to_state(P)
class C9(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@i
	def name(self):return Am
	def enter(A,machine):D.log_item('Set Web Options');AD();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(E,machine):
		G.update();J.update()
		if G.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(AA+AY[E.menuIndex]+S);E.selectedMenuIndex=E.menuIndex;E.menuIndex+=1
				if E.menuIndex>h(AY)-1:E.menuIndex=0
		if J.fell:
			H=AY[E.selectedMenuIndex]
			if H=='web_on':A[Ag]=L;A1();AD()
			elif H=='web_off':A[Ag]=F;A1();AD()
			elif H=='hear_url':B7(A[r],L);AD()
			elif H=='hear_instr_web':C('/sd/feller_menu/web_instruct.wav');AD()
			else:D.write_json_file(q,A);C(s);machine.go_to_state(P)
class CA(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@i
	def name(self):return AL
	def enter(A,machine):D.log_item('Choose sounds menu');B_();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(E,machine):
		G.update();J.update()
		if G.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C('/sd/feller_menu/option_'+A4[E.menuIndex]+S);E.selectedMenuIndex=E.menuIndex;E.menuIndex+=1
				if E.menuIndex>h(A4)-1:E.menuIndex=0
		if J.fell:A[O]=A4[E.selectedMenuIndex];D.log_item('Selected index: '+W(E.selectedMenuIndex)+' Saved option: '+A[O]);D.write_json_file(q,A);A1();machine.go_to_state(P)
class CB(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@i
	def name(self):return Af
	def enter(A,machine):D.log_item('Main menu');Bz();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(A,machine):
		D=machine;G.update();J.update()
		if G.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(AA+AU[A.menuIndex]+S);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>h(AU)-1:A.menuIndex=0
		if J.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				E=AU[A.selectedMenuIndex]
				if E==AL:D.go_to_state(AL)
				elif E==AM:D.go_to_state(AM)
				elif E==AN:D.go_to_state(AN)
				elif E==Al:D.go_to_state(Al)
				elif E==Am:D.go_to_state(Am)
				else:C(s);D.go_to_state(P)
class CC(I):
	def __init__(A):super().__init__()
	@i
	def name(self):return'example'
	def enter(A,machine):I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(A,machine):I.update(A,machine)
H('state machine')
Z=C4()
Z.add_state(C5())
Z.add_state(CB())
Z.add_state(CA())
Z.add_state(C7())
Z.add_state(C6())
Z.add_state(C8())
Z.add_state(C9())
AB.value=L
def B9():
	C('/sd/feller_menu/animator_available_on_network.wav');C('/sd/feller_menu/to_access_type.wav')
	if A[r]=='animator-feller':C('/sd/feller_menu/animator_feller_local.wav')
	else:B7(A[r],L)
	C('/sd/feller_menu/in_your_browser.wav')
if AH:
	D.log_item('starting server...')
	try:Y.start(W(z.radio.ipv4_address));D.log_item('Listening on http://%s:80'%z.radio.ipv4_address);B9()
	except OSError:time.sleep(5);D.log_item('restarting...');As()
Z.go_to_state(P)
D.log_item('animator has started...')
H('animations started.')
while L:
	Z.update();E(.1)
	if AH:
		try:Y.poll()
		except BA as Ab:D.log_item(Ab);continue