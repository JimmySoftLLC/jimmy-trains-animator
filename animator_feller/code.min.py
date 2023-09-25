BT='move_tree_to_fallen_position'
BS='move_tree_to_upright_position'
BR='move_feller_to_chop_position'
BQ='move_feller_to_rest_position'
BP='/sd/menu_voice_commands/to_exit_press_and_hold_button_down.wav'
BO='animator-feller'
BN='Dialog option cal saved.'
BM='opening_dialog_off'
BL='opening_dialog_on'
BK=' cal saved.'
BJ='Redirected to home page.'
BI='/sd/menu_voice_commands/continuous_mode_deactivated.wav'
BH='/sd/menu_voice_commands/continuous_mode_activated.wav'
BG='feller_girlfriend'
BF='feller_buddy'
BE='feller_poem'
BD='feller_wife'
BC='wav/micro_sd_card_not_inserted.mp3'
BB=Exception
Ap='web_options'
Ao='set_dialog_options'
An='happy_birthday'
Am='alien'
Al='random'
Ak='config wifi imports'
Aj='serve_webpage'
Ai='main_menu'
AP='move_feller_and_tree'
AO='adjust_feller_and_tree'
AN='choose_sounds'
AH='volume'
AG='volume_pot'
AF='utf8'
AE='deinit wave0'
AA='/sd/menu_voice_commands/'
A9='feller_advice'
A8='opening_dialog'
A7=print
A4='left_held'
m='HOST_NAME'
l=property
k=len
j=range
g='/sd/menu_voice_commands/all_changes_complete.wav'
b='/sd/config_feller.json'
a='tree_down_pos'
Y='rb'
X=str
W=open
T='.wav'
S='feller_chop_pos'
P='base_state'
O='option_selected'
N='feller_rest_pos'
L='tree_up_pos'
K=True
E=False
import gc,files as D
def H(collection_point):gc.collect();A=gc.mem_free();D.log_item('Point '+collection_point+' Available memory: {} bytes'.format(A))
H('Imports gc, files')
import sdcardio as Aq,storage as AI,audiomp3 as AQ,audiocore as c,audiomixer as BU,audiobusio as Ar,time,board as U,microcontroller as AR,busio,pwmio as As,digitalio as n,random as v
from analogio import AnalogIn as BV
from adafruit_motor import servo as At
from adafruit_debouncer import Debouncer as Au
def Av():AR.on_next_reset(AR.RunMode.NORMAL);AR.reset()
H('imports')
BW=BV(U.A0)
def BX(pin,wait_for):
	B=wait_for/10;A=0
	for C in j(10):time.sleep(B);A+=1;A=A/10
	return pin.value/65536
AB=n.DigitalInOut(U.GP28)
AB.direction=n.Direction.OUTPUT
AB.value=E
BY=As.PWMOut(U.GP10,duty_cycle=2**15,frequency=50)
BZ=As.PWMOut(U.GP11,duty_cycle=2**15,frequency=50)
w=At.Servo(BY)
x=At.Servo(BZ)
Ba=U.GP6
Bb=U.GP7
AS=n.DigitalInOut(Ba)
AS.direction=n.Direction.INPUT
AS.pull=n.Pull.UP
G=Au(AS)
AT=n.DigitalInOut(Bb)
AT.direction=n.Direction.INPUT
AT.pull=n.Pull.UP
J=Au(AT)
Aw=U.GP18
Ax=U.GP19
Ay=U.GP20
h=Ar.I2SOut(bit_clock=Aw,word_select=Ax,data=Ay)
AB.value=K
Bc=U.GP2
Bd=U.GP3
Be=U.GP4
Az=U.GP5
A_=busio.SPI(Bc,Bd,Be)
try:AU=Aq.SDCard(A_,Az);AV=AI.VfsFat(AU);AI.mount(AV,'/sd')
except:
	o=AQ.MP3Decoder(W(BC,Y));h.play(o)
	while h.playing:0
	o.deinit();H(AE);B0=E
	while not B0:
		G.update()
		if G.fell:
			try:
				AU=Aq.SDCard(A_,Az);AV=AI.VfsFat(AU);AI.mount(AV,'/sd');B0=K;o=AQ.MP3Decoder(W('wav/micro_sd_card_success.mp3',Y));h.play(o)
				while h.playing:0
				o.deinit();H(AE)
			except:
				o=AQ.MP3Decoder(W(BC,Y));h.play(o)
				while h.playing:0
				o.deinit();H(AE)
h.deinit()
AB.value=E
H('deinit audio')
h=Ar.I2SOut(bit_clock=Aw,word_select=Ax,data=Ay)
Bf=2
B=BU.Mixer(voice_count=Bf,sample_rate=22050,channel_count=2,bits_per_sample=16,samples_signed=K,buffer_size=8192)
h.play(B)
H('audio setup')
import utilities as y
H('animator_feller, utilities')
A=D.read_json_file(b)
z=A[L]
p=60
q=180
if A[a]<p or A[a]>q:A[a]=p
if A[L]<p or A[L]>q:A[L]=q
A0=A[N]
r=0
s=170
if A[N]<r or A[N]>s:A[N]=r
if A[S]>s or A[S]<r:A[S]=s
Bg=D.read_json_file('/sd/menu_voice_commands/main_menu.json')
AW=Bg[Ai]
Bh=D.read_json_file('/sd/menu_voice_commands/choose_sounds.json')
A5=Bh[AN]
Bi=D.read_json_file('/sd/feller_dialog/feller_dialog.json')
B1=Bi['feller_dialog']
Bj=D.read_json_file('/sd/feller_wife/feller_wife.json')
Bk=Bj[BD]
Bl=D.read_json_file('/sd/feller_poem/feller_poem.json')
Bm=Bl[BE]
Bn=D.read_json_file('/sd/feller_buddy/feller_buddy.json')
Bo=Bn[BF]
Bp=D.read_json_file('/sd/feller_girlfriend/feller_girlfriend.json')
Bq=Bp[BG]
Br=D.read_json_file('/sd/menu_voice_commands/adjust_feller_and_tree.json')
AX=Br[AO]
Bs=D.read_json_file('/sd/menu_voice_commands/move_feller_and_tree.json')
AY=Bs[AP]
Bt=D.read_json_file('/sd/menu_voice_commands/dialog_selection_menu.json')
AZ=Bt['dialog_selection_menu']
Bu=D.read_json_file('/sd/menu_voice_commands/web_menu.json')
Aa=Bu['web_menu']
AJ=A[Aj]
d=N
e=L
t=E
H('config setup')
if AJ:
	import socketpool as Bv,mdns;H(Ak);import wifi as A1;H(Ak);from adafruit_httpserver import Server,Request,FileResponse as Ab,Response as M,POST as i;H(Ak);D.log_item('Connecting to WiFi');B2='jimmytrainsguest';B3=''
	try:B4=D.read_json_file('/sd/env.json');B2=B4['WIFI_SSID'];B3=B4['WIFI_PASSWORD'];H('wifi env');A7('Using env ssid and password')
	except:A7('Using default ssid and password')
	try:
		A1.radio.connect(B2,B3);H('wifi connect');Ac=mdns.Server(A1.radio);Ac.hostname=A[m];Ac.advertise_service(service_type='_http',protocol='_tcp',port=80);Bw=[hex(A)for A in A1.radio.mac_address];D.log_item('My MAC addr:'+X(Bw));Bx=X(A1.radio.ipv4_address);D.log_item('My IP address is'+Bx);D.log_item('Connected to WiFi');By=Bv.SocketPool(A1.radio);Q=Server(By,'/static',debug=K);H('wifi server')
		@Q.route('/')
		def B5(request):H('Home page.');return Ab(request,'index.html','/')
		@Q.route('/mui.min.css')
		def B5(request):return Ab(request,'mui.min.css','/')
		@Q.route('/mui.min.js')
		def B5(request):return Ab(request,'mui.min.js','/')
		@Q.route('/animation',[i])
		def u(request):
			S='owl';Q='no_sounds';P='machines';N='just_birds';L='birds_dogs';J='birds_dogs_short_version';I='train';H='halloween';G='christmas';F='forth_of_july';D=request;global A;global t;B=D.raw_request.decode(AF)
			if Al in B:A[O]=Al;R()
			elif F in B:A[O]=F;R()
			elif G in B:A[O]=G;R()
			elif H in B:A[O]=H;R()
			elif I in B:A[O]=I;R()
			elif Am in B:A[O]=Am;R()
			elif J in B:A[O]=J;R()
			elif L in B:A[O]=L;R()
			elif N in B:A[O]=N;R()
			elif P in B:A[O]=P;R()
			elif Q in B:A[O]=Q;R()
			elif S in B:A[O]=S;R()
			elif An in B:A[O]=An;R()
			elif'cont_mode_on'in B:t=K;C(BH)
			elif'cont_mode_off'in B:t=E;C(BI)
			return M(D,'Animation '+A[O]+' started.')
		@Q.route('/feller',[i])
		def u(request):
			B=request;global A;global d;C=B.raw_request.decode(AF)
			if N in C:d=N;f(A[d],.01);return M(B,'Moved feller to rest position.')
			elif S in C:d=S;f(A[d],.01);return M(B,'Moved feller to chop position.')
			elif'feller_adjust'in C:d=N;f(A[d],.01);return M(B,'Redirected to feller-adjust page.')
			elif'feller_home'in C:return M(B,BJ)
			elif'feller_clockwise'in C:Af(w,d,1,r,s);return M(B,'Moved feller clockwise.')
			elif'feller_counter_clockwise'in C:Ag(w,d,1,r,s);return M(B,'Moved feller counter clockwise.')
			elif'feller_cal_saved'in C:Ah();Z.go_to_state(P);return M(B,'Feller '+d+BK)
		@Q.route('/tree',[i])
		def u(request):
			B=request;global A;global e;C=B.raw_request.decode(AF)
			if L in C:e=L;V(A[e],.01);return M(B,'Moved tree to up position.')
			elif a in C:e=a;V(A[e],.01);return M(B,'Moved tree to fallen position.')
			elif'tree_adjust'in C:e=L;V(A[e],.01);return M(B,'Redirected to tree-adjust page.')
			elif'tree_home'in C:return M(B,BJ)
			elif'tree_up'in C:Af(x,e,-1,p,q);return M(B,'Moved tree up.')
			elif'tree_down'in C:Ag(x,e,-1,p,q);return M(B,'Moved tree down.')
			elif'tree_cal_saved'in C:Ah();Z.go_to_state(P);return M(B,'Tree '+e+BK)
		@Q.route('/dialog',[i])
		def u(request):
			F=request;global A;B=F.raw_request.decode(AF)
			if BL in B:A[A8]=K
			elif BM in B:A[A8]=E
			elif'feller_advice_on'in B:A[A9]=K
			elif'feller_advice_off'in B:A[A9]=E
			D.write_json_file(b,A);C(g);return M(F,BN)
		@Q.route('/utilities',[i])
		def u(request):
			F=request;global A;B=F.raw_request.decode(AF)
			if'speaker_test'in B:C('/sd/menu_voice_commands/left_speaker_right_speaker.wav')
			elif'volume_pot_off'in B:A[AG]=E;D.write_json_file(b,A);C(g)
			elif'volume_pot_on'in B:A[AG]=K;D.write_json_file(b,A);C(g)
			elif'reset_to_defaults'in B:Bz();D.write_json_file(b,A);C(g);Z.go_to_state(P)
			return M(F,BN)
		@Q.route('/update-host-name',[i])
		def u(request):B=request;global A;C=B.json();A[m]=C['text'];D.write_json_file(b,A);Ac.hostname=A[m];BA();return M(B,A[m])
		@Q.route('/get-host-name',[i])
		def u(request):return M(request,A[m])
		@Q.route('/update-volume',[i])
		def u(request):B=request;global A;F=B.json();A[AH]=F['text'];A[AG]=E;D.write_json_file(b,A);C('/sd/menu_voice_commands/volume.wav');Ae(A[AH],E);return M(B,A[AH])
		@Q.route('/get-volume',[i])
		def u(request):return M(request,A[AH])
	except BB as Ad:AJ=E;D.log_item(Ad)
H('web server')
def Bz():global A;A[L]=165;A[a]=100;A[N]=0;A[S]=150;A[A8]=E;A[A9]=K;A[m]=BO;A[AG]=K
def F(seconds):
	if A[AG]:C=BX(BW,seconds);B.voice[0].level=C
	else:
		try:C=int(A[AH])/100
		except:C=.5
		if C<0 or C>1:C=.5
		B.voice[0].level=C;B.voice[1].level=C
H('global variable and methods')
def C(file_name):
	if B.voice[0].playing:
		B.voice[0].stop()
		while B.voice[0].playing:F(.02)
	A=c.WaveFile(W(file_name,Y));B.voice[0].play(A,loop=E)
	while B.voice[0].playing:B_()
def CE():
	B.voice[0].stop()
	while B.voice[0].playing:0
def B_():
	F(.02);G.update()
	if G.fell:B.voice[0].stop()
def A6():C('/sd/menu_voice_commands/press_left_button_right_button.wav')
def A2():C('/sd/menu_voice_commands/option_selected.wav')
def B6():C('/sd/menu_voice_commands/now_we_can_adjust_the_feller_position.wav');C(BP)
def B7():C('/sd/menu_voice_commands/now_we_can_adjust_the_tree_position.wav');C(BP)
def C0():C('/sd/menu_voice_commands/main_menu.wav');A6()
def C1():C('/sd/menu_voice_commands/sound_selection_menu.wav');A6()
def C2():C('/sd/menu_voice_commands/adjust_feller_and_tree_menu.wav');A6()
def C3():C('/sd/menu_voice_commands/move_feller_and_tree_menu.wav');A6()
def AC():C('/sd/menu_voice_commands/dialog_selection_menu.wav');A6()
def AD():C('/sd/menu_voice_commands/web_menu.wav');A6()
def B8(min_servo_pos,max_servo_pos,servo_pos):
	B='/sd/menu_voice_commands/limit_reached.wav';A=servo_pos
	if A<min_servo_pos:C(B);return E
	if A>max_servo_pos:C(B);return E
	return K
def Ae(str_to_speak,addLocal):
	for A in str_to_speak:
		if A=='-':A='dash'
		if A=='.':A='dot'
		C(AA+A+T)
	if addLocal:C('/sd/menu_voice_commands/dot.wav');C('/sd/menu_voice_commands/local.wav')
H('dialog methods')
def Af(servo,movement_type,sign,min_servo_pos,max_servo_pos):
	B=movement_type;global A;A[B]-=1*sign
	if B8(min_servo_pos,max_servo_pos,A[B]):servo.angle=A[B]
	else:A[B]+=1*sign
def Ag(servo,movement_type,sign,min_servo_pos,max_servo_pos):
	B=movement_type;global A;A[B]+=1*sign
	if B8(min_servo_pos,max_servo_pos,A[B]):servo.angle=A[B]
	else:A[B]-=1*sign
def Ah():C(g);global A;D.write_json_file(b,A)
def AK(servo,movement_type):
	C=servo;B=movement_type
	if B==N or B==S:D=r;H=s;I=1
	else:D=p;H=q;I=-1
	L=E
	while not L:
		C.angle=A[B];G.update();J.update()
		if G.fell:Af(C,B,I,D,H)
		if J.fell:
			M=K;O=0
			while M:
				F(.1);J.update();O+=1
				if O>30:Ah();M=E;L=K
				if J.rose:M=E
			if not L:Ag(C,B,I,D,H)
	if B==N or B==S:global A0;A0=A[B]
	else:global z;z=A[B]
def f(new_position,speed):
	A=new_position;global A0;B=1
	if A0>A:B=-1
	for C in j(A0,A,B):AL(C);F(speed)
	AL(A)
def V(new_position,speed):
	A=new_position;global z;B=1
	if z>A:B=-1
	for C in j(z,A,B):A3(C);F(speed)
	A3(A)
def AL(servo_pos):
	A=servo_pos
	if A<r:A=r
	if A>s:A=s
	w.angle=A;global A0;A0=A
def A3(servo_pos):
	A=servo_pos
	if A<p:A=p
	if A>q:A=q
	x.angle=A;global z;z=A
def R():C5()
H('servo helpers')
def B9():
	D=7;C=.2
	while B.voice[0].playing:
		E=y.switch_state(G,J,F,5)
		if E==A4:
			B.voice[0].stop()
			while B.voice[0].playing:0
			return
		w.angle=D+A[N];F(C);w.angle=A[N];F(C)
def C4():
	D=2;C=.2
	while B.voice[0].playing:
		E=y.switch_state(G,J,F,5)
		if E==A4:
			B.voice[0].stop()
			while B.voice[0].playing:0
			return
		x.angle=A[L];F(C);x.angle=A[L]-D;F(C)
def AM(sound_files,folder):
	C=folder;A=sound_files;L=k(A)-1;I=v.randint(0,L);D.log_item(C+': '+X(I));K=c.WaveFile(W('/sd/'+C+'/'+A[I]+T,Y));B.voice[0].play(K,loop=E)
	while B.voice[0].playing:
		F(.1);M=y.switch_state(G,J,F,5)
		if M==A4:
			B.voice[0].stop()
			while B.voice[0].playing:0
	K.deinit();H(AE)
def C5():
	p='Sound file: ';o='/sd/feller_sounds/sounds_';g='/sd/menu_voice_commands/animation_canceled.wav';F(.05)
	if A[A8]:
		U=v.randint(0,3)
		if U==0:AM(Bk,BD)
		if U==1:AM(Bo,BF)
		if U==2:AM(Bm,BE)
		if U==3:AM(Bq,BG)
	P=1;Z=v.randint(2,7);d=k(B1)-1;h=v.randint(0,d);i=v.randint(2,Z);D.log_item('Chop total: '+X(Z)+' what to speak: '+X(h)+' when to speak: '+X(i));l=E;q=A[L]-3;M=A[O]
	if M==Al:d=k(A5)-2;Q=v.randint(0,d);M=A5[Q];A7('Random sound file: '+A5[Q])
	if M==An:Q=v.randint(0,6);I=o+M+X(Q)+T;A7(p+M+X(Q))
	else:I=o+M+T;A7(p+M)
	m=c.WaveFile(W(I,Y))
	while P<=Z:
		if i==P and not l and A[A9]:l=K;I='/sd/feller_dialog/'+B1[h]+T;C=c.WaveFile(W(I,Y));B.voice[0].play(C,loop=E);B9();C.deinit();H(AE)
		C=c.WaveFile(W('/sd/feller_chops/chop'+X(P)+T,Y));P+=1
		for b in j(A[N],A[S]+5,10):
			AL(b)
			if b>=A[S]-10:
				B.voice[0].play(C,loop=E);e=2;F(.2)
				for r in j(e):A3(q);F(.1);A3(A[L]);F(.1)
				break
		if P<=Z:
			for b in j(A[S],A[N],-5):AL(b);F(.02)
	while B.voice[0].playing:F(.1)
	B.voice[0].play(m,loop=E)
	for s in j(A[L],A[a],-5):A3(s);F(.06)
	e=8
	for r in j(e):A3(A[a]);F(.1);A3(7+A[a]);F(.1)
	if M==Am:
		A7('Alien sequence starting....');F(2);f(A[N],.01);V(A[L],.01);t=A[L];u=A[L]-8
		while B.voice[0].playing:
			R=y.switch_state(G,J,F,5)
			if R==A4:
				B.voice[0].stop()
				while B.voice[0].playing:0
				I=g;C=c.WaveFile(W(I,Y));B.voice[0].play(C,loop=E)
				while B.voice[0].playing:0
				break
			V(t,.1);V(u,.1)
		V(A[L],.04)
		for n in j(7):
			I='/sd/feller_alien/human_'+X(n+1)+T;C=c.WaveFile(W(I,Y));B.voice[0].play(C,loop=E);B9();I='/sd/feller_alien/alien_'+X(n+1)+T;C=c.WaveFile(W(I,Y));B.voice[0].play(C,loop=E);C4();R=y.switch_state(G,J,F,5)
			if R==A4:
				B.voice[0].stop()
				while B.voice[0].playing:0
				I=g;C=c.WaveFile(W(I,Y));B.voice[0].play(C,loop=E)
				while B.voice[0].playing:0
				break
	else:
		while B.voice[0].playing:
			R=y.switch_state(G,J,F,5)
			if R==A4:
				B.voice[0].stop()
				while B.voice[0].playing:0
				I=g;C=c.WaveFile(W(I,Y));B.voice[0].play(C,loop=E)
				while B.voice[0].playing:0
				break
	C.deinit();m.deinit();H('deinit wave0 wave1');f(A[N],.01);F(.02);V(A[L],.01)
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
	def reset(A):Av()
class I:
	def __init__(A):0
	@l
	def name(self):return''
	def enter(A,machine):0
	def exit(A,machine):0
	def update(B,machine):
		A=machine
		if G.fell:A.paused_state=A.state.name;A.pause();return E
		return K
class C7(I):
	def __init__(A):0
	@l
	def name(self):return P
	def enter(E,machine):
		F(.1)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:f(A[N],.01);V(A[L],.01);C('/sd/menu_voice_commands/animations_are_now_active.wav')
		D.log_item('Entered base state');I.enter(E,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(B,machine):
		global t;A=y.switch_state(G,J,F,30)
		if A==A4:
			if t:t=E;C(BI)
			else:t=K;C(BH)
		elif A=='left'or t:R()
		elif A=='right':machine.go_to_state(Ai)
class C8(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@l
	def name(self):return AP
	def enter(A,machine):D.log_item('Move feller and tree menu');C3();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(B,machine):
		G.update();J.update()
		if G.fell:
			C(AA+AY[B.menuIndex]+T);B.selectedMenuIndex=B.menuIndex;B.menuIndex+=1
			if B.menuIndex>k(AY)-1:B.menuIndex=0
		if J.fell:
			D=AY[B.selectedMenuIndex]
			if D==BQ:f(A[N],.01)
			elif D==BR:f(A[S],.01)
			elif D==BS:V(A[L],.01)
			elif D==BT:V(A[a],.01)
			else:C(g);machine.go_to_state(P)
class C9(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@l
	def name(self):return AO
	def enter(A,machine):D.log_item('Adjust feller and tree menu');C2();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		E=machine;G.update();J.update()
		if G.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(AA+AX[D.menuIndex]+T);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>k(AX)-1:D.menuIndex=0
		if J.fell:
			F=AX[D.selectedMenuIndex]
			if F==BQ:f(A[N],.01);B6();AK(w,N);E.go_to_state(P)
			elif F==BR:f(A[S],.01);B6();AK(w,S);E.go_to_state(P)
			elif F==BS:V(A[L],.01);B7();AK(x,L);E.go_to_state(P)
			elif F==BT:V(A[a],.01);B7();AK(x,a);E.go_to_state(P)
			else:C(g);E.go_to_state(P)
class CA(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@l
	def name(self):return Ao
	def enter(A,machine):D.log_item('Set Dialog Options');AC();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(F,machine):
		G.update();J.update()
		if G.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(AA+AZ[F.menuIndex]+T);F.selectedMenuIndex=F.menuIndex;F.menuIndex+=1
				if F.menuIndex>k(AZ)-1:F.menuIndex=0
		if J.fell:
			H=AZ[F.selectedMenuIndex]
			if H==BL:A[A8]=K;A2();AC()
			elif H==BM:A[A8]=E;A2();AC()
			elif H=='lumberjack_advice_on':A[A9]=K;A2();AC()
			elif H=='lumberjack_advice_off':A[A9]=E;A2();AC()
			else:D.write_json_file(b,A);C(g);machine.go_to_state(P)
class CB(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@l
	def name(self):return Ap
	def enter(A,machine):D.log_item('Set Web Options');AD();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(F,machine):
		G.update();J.update()
		if G.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(AA+Aa[F.menuIndex]+T);F.selectedMenuIndex=F.menuIndex;F.menuIndex+=1
				if F.menuIndex>k(Aa)-1:F.menuIndex=0
		if J.fell:
			H=Aa[F.selectedMenuIndex]
			if H=='web_on':A[Aj]=K;A2();AD()
			elif H=='web_off':A[Aj]=E;A2();AD()
			elif H=='hear_url':Ae(A[m],K);AD()
			elif H=='hear_instr_web':C('/sd/menu_voice_commands/web_instruct.wav');AD()
			else:D.write_json_file(b,A);C(g);machine.go_to_state(P)
class CC(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@l
	def name(self):return AN
	def enter(A,machine):D.log_item('Choose sounds menu');C1();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(E,machine):
		G.update();J.update()
		if G.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C('/sd/menu_voice_commands/option_'+A5[E.menuIndex]+T);E.selectedMenuIndex=E.menuIndex;E.menuIndex+=1
				if E.menuIndex>k(A5)-1:E.menuIndex=0
		if J.fell:A[O]=A5[E.selectedMenuIndex];D.log_item('Selected index: '+X(E.selectedMenuIndex)+' Saved option: '+A[O]);D.write_json_file(b,A);A2();machine.go_to_state(P)
class CD(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@l
	def name(self):return Ai
	def enter(A,machine):D.log_item('Main menu');C0();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(A,machine):
		D=machine;G.update();J.update()
		if G.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(AA+AW[A.menuIndex]+T);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>k(AW)-1:A.menuIndex=0
		if J.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				E=AW[A.selectedMenuIndex]
				if E==AN:D.go_to_state(AN)
				elif E==AO:D.go_to_state(AO)
				elif E==AP:D.go_to_state(AP)
				elif E==Ao:D.go_to_state(Ao)
				elif E==Ap:D.go_to_state(Ap)
				else:C(g);D.go_to_state(P)
class CF(I):
	def __init__(A):super().__init__()
	@l
	def name(self):return'example'
	def enter(A,machine):I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(A,machine):I.update(A,machine)
H('state machine')
Z=C6()
Z.add_state(C7())
Z.add_state(CD())
Z.add_state(CC())
Z.add_state(C9())
Z.add_state(C8())
Z.add_state(CA())
Z.add_state(CB())
AB.value=K
def BA():
	C('/sd/menu_voice_commands/animator_available_on_network.wav');C('/sd/menu_voice_commands/to_access_type.wav')
	if A[m]==BO:C('/sd/menu_voice_commands/animator_feller_local.wav')
	else:Ae(A[m],K)
	C('/sd/menu_voice_commands/in_your_browser.wav')
if AJ:
	D.log_item('starting server...')
	try:Q.start(X(A1.radio.ipv4_address));D.log_item('Listening on http://%s:80'%A1.radio.ipv4_address);BA()
	except OSError:time.sleep(5);D.log_item('restarting...');Av()
Z.go_to_state(P)
D.log_item('animator has started...')
H('animations started.')
while K:
	Z.update();F(.1)
	if AJ:
		try:Q.poll()
		except BB as Ad:D.log_item(Ad);continue