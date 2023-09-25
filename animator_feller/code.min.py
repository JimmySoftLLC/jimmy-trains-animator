BU='move_tree_to_fallen_position'
BT='move_tree_to_upright_position'
BS='move_feller_to_chop_position'
BR='move_feller_to_rest_position'
BQ='/sd/menu_voice_commands/to_exit_press_and_hold_button_down.wav'
BP='animator-feller'
BO='Dialog option cal saved.'
BN='opening_dialog_off'
BM='opening_dialog_on'
BL=' cal saved.'
BK='Redirected to home page.'
BJ='/sd/menu_voice_commands/continuous_mode_deactivated.wav'
BI='/sd/menu_voice_commands/continuous_mode_activated.wav'
BH='feller_girlfriend'
BG='feller_buddy'
BF='feller_poem'
BE='feller_wife'
BD='wav/micro_sd_card_not_inserted.mp3'
BC=Exception
Aq='web_options'
Ap='set_dialog_options'
Ao='/sd/config_lightning.json'
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
u='/sd/config_feller.json'
l='HOST_NAME'
k=property
j=len
i=range
f='/sd/menu_voice_commands/all_changes_complete.wav'
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
import sdcardio as Ar,storage as AI,audiomp3 as AQ,audiocore as b,audiomixer as BV,audiobusio as As,time,board as U,microcontroller as AR,busio,pwmio as At,digitalio as m,random as v
from analogio import AnalogIn as BW
from adafruit_motor import servo as Au
from adafruit_debouncer import Debouncer as Av
def Aw():AR.on_next_reset(AR.RunMode.NORMAL);AR.reset()
H('imports')
BX=BW(U.A0)
def BY(pin,wait_for):
	B=wait_for/10;A=0
	for C in i(10):time.sleep(B);A+=1;A=A/10
	return pin.value/65536
AB=m.DigitalInOut(U.GP28)
AB.direction=m.Direction.OUTPUT
AB.value=E
BZ=At.PWMOut(U.GP10,duty_cycle=2**15,frequency=50)
Ba=At.PWMOut(U.GP11,duty_cycle=2**15,frequency=50)
w=Au.Servo(BZ)
x=Au.Servo(Ba)
Bb=U.GP6
Bc=U.GP7
AS=m.DigitalInOut(Bb)
AS.direction=m.Direction.INPUT
AS.pull=m.Pull.UP
G=Av(AS)
AT=m.DigitalInOut(Bc)
AT.direction=m.Direction.INPUT
AT.pull=m.Pull.UP
J=Av(AT)
Ax=U.GP18
Ay=U.GP19
Az=U.GP20
g=As.I2SOut(bit_clock=Ax,word_select=Ay,data=Az)
AB.value=K
Bd=U.GP2
Be=U.GP3
Bf=U.GP4
A_=U.GP5
B0=busio.SPI(Bd,Be,Bf)
try:AU=Ar.SDCard(B0,A_);AV=AI.VfsFat(AU);AI.mount(AV,'/sd')
except:
	n=AQ.MP3Decoder(W(BD,Y));g.play(n)
	while g.playing:0
	n.deinit();H(AE);B1=E
	while not B1:
		G.update()
		if G.fell:
			try:
				AU=Ar.SDCard(B0,A_);AV=AI.VfsFat(AU);AI.mount(AV,'/sd');B1=K;n=AQ.MP3Decoder(W('wav/micro_sd_card_success.mp3',Y));g.play(n)
				while g.playing:0
				n.deinit();H(AE)
			except:
				n=AQ.MP3Decoder(W(BD,Y));g.play(n)
				while g.playing:0
				n.deinit();H(AE)
g.deinit()
AB.value=E
H('deinit audio')
g=As.I2SOut(bit_clock=Ax,word_select=Ay,data=Az)
Bg=2
B=BV.Mixer(voice_count=Bg,sample_rate=22050,channel_count=2,bits_per_sample=16,samples_signed=K,buffer_size=8192)
g.play(B)
H('audio setup')
import utilities as y
H('animator_feller, utilities')
A=D.read_json_file(u)
z=A[L]
o=60
p=180
if A[a]<o or A[a]>p:A[a]=o
if A[L]<o or A[L]>p:A[L]=p
A0=A[N]
q=0
r=170
if A[N]<q or A[N]>r:A[N]=q
if A[S]>r or A[S]<q:A[S]=r
Bh=D.read_json_file('/sd/menu_voice_commands/main_menu.json')
AW=Bh[Ai]
Bi=D.read_json_file('/sd/menu_voice_commands/choose_sounds.json')
A5=Bi[AN]
Bj=D.read_json_file('/sd/feller_dialog/feller_dialog.json')
B2=Bj['feller_dialog']
Bk=D.read_json_file('/sd/feller_wife/feller_wife.json')
Bl=Bk[BE]
Bm=D.read_json_file('/sd/feller_poem/feller_poem.json')
Bn=Bm[BF]
Bo=D.read_json_file('/sd/feller_buddy/feller_buddy.json')
Bp=Bo[BG]
Bq=D.read_json_file('/sd/feller_girlfriend/feller_girlfriend.json')
Br=Bq[BH]
Bs=D.read_json_file('/sd/menu_voice_commands/adjust_feller_and_tree.json')
AX=Bs[AO]
Bt=D.read_json_file('/sd/menu_voice_commands/move_feller_and_tree.json')
AY=Bt[AP]
Bu=D.read_json_file('/sd/menu_voice_commands/dialog_selection_menu.json')
AZ=Bu['dialog_selection_menu']
Bv=D.read_json_file('/sd/menu_voice_commands/web_menu.json')
Aa=Bv['web_menu']
AJ=A[Aj]
c=N
d=L
s=E
H('config setup')
if AJ:
	import socketpool as Bw,mdns;H(Ak);import wifi as A1;H(Ak);from adafruit_httpserver import Server,Request,FileResponse as Ab,Response as M,POST as h;H(Ak);D.log_item('Connecting to WiFi');B3='jimmytrainsguest';B4=''
	try:B5=D.read_json_file('/sd/env.json');B3=B5['WIFI_SSID'];B4=B5['WIFI_PASSWORD'];H('wifi env');A7('Using env ssid and password')
	except:A7('Using default ssid and password')
	try:
		A1.radio.connect(B3,B4);H('wifi connect');Ac=mdns.Server(A1.radio);Ac.hostname=A[l];Ac.advertise_service(service_type='_http',protocol='_tcp',port=80);Bx=[hex(A)for A in A1.radio.mac_address];D.log_item('My MAC addr:'+X(Bx));By=X(A1.radio.ipv4_address);D.log_item('My IP address is'+By);D.log_item('Connected to WiFi');Bz=Bw.SocketPool(A1.radio);Q=Server(Bz,'/static',debug=K);H('wifi server')
		@Q.route('/')
		def B6(request):H('Home page.');return Ab(request,'index.html','/')
		@Q.route('/mui.min.css')
		def B6(request):return Ab(request,'mui.min.css','/')
		@Q.route('/mui.min.js')
		def B6(request):return Ab(request,'mui.min.js','/')
		@Q.route('/animation',[h])
		def t(request):
			S='owl';Q='no_sounds';P='machines';N='just_birds';L='birds_dogs';J='birds_dogs_short_version';I='train';H='halloween';G='christmas';F='forth_of_july';D=request;global A;global s;B=D.raw_request.decode(AF)
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
			elif'cont_mode_on'in B:s=K;C(BI)
			elif'cont_mode_off'in B:s=E;C(BJ)
			return M(D,'Animation '+A[O]+' started.')
		@Q.route('/feller',[h])
		def t(request):
			B=request;global A;global c;C=B.raw_request.decode(AF)
			if N in C:c=N;e(A[c],.01);return M(B,'Moved feller to rest position.')
			elif S in C:c=S;e(A[c],.01);return M(B,'Moved feller to chop position.')
			elif'feller_adjust'in C:c=N;e(A[c],.01);return M(B,'Redirected to feller-adjust page.')
			elif'feller_home'in C:return M(B,BK)
			elif'feller_clockwise'in C:Af(w,c,1,q,r);return M(B,'Moved feller clockwise.')
			elif'feller_counter_clockwise'in C:Ag(w,c,1,q,r);return M(B,'Moved feller counter clockwise.')
			elif'feller_cal_saved'in C:Ah();Z.go_to_state(P);return M(B,'Feller '+c+BL)
		@Q.route('/tree',[h])
		def t(request):
			B=request;global A;global d;C=B.raw_request.decode(AF)
			if L in C:d=L;V(A[d],.01);return M(B,'Moved tree to up position.')
			elif a in C:d=a;V(A[d],.01);return M(B,'Moved tree to fallen position.')
			elif'tree_adjust'in C:d=L;V(A[d],.01);return M(B,'Redirected to tree-adjust page.')
			elif'tree_home'in C:return M(B,BK)
			elif'tree_up'in C:Af(x,d,-1,o,p);return M(B,'Moved tree up.')
			elif'tree_down'in C:Ag(x,d,-1,o,p);return M(B,'Moved tree down.')
			elif'tree_cal_saved'in C:Ah();Z.go_to_state(P);return M(B,'Tree '+d+BL)
		@Q.route('/dialog',[h])
		def t(request):
			F=request;global A;B=F.raw_request.decode(AF)
			if BM in B:A[A8]=K
			elif BN in B:A[A8]=E
			elif'feller_advice_on'in B:A[A9]=K
			elif'feller_advice_off'in B:A[A9]=E
			D.write_json_file(u,A);C(f);return M(F,BO)
		@Q.route('/utilities',[h])
		def t(request):
			F=request;global A;B=F.raw_request.decode(AF)
			if'speaker_test'in B:C('/sd/menu_voice_commands/left_speaker_right_speaker.wav')
			elif'volume_pot_off'in B:A[AG]=E;D.write_json_file(Ao,A);C(f)
			elif'volume_pot_on'in B:A[AG]=K;D.write_json_file(Ao,A);C(f)
			elif'reset_to_defaults'in B:B_();D.write_json_file(u,A);C(f);Z.go_to_state(P)
			return M(F,BO)
		@Q.route('/update-host-name',[h])
		def t(request):B=request;global A;C=B.json();A[l]=C['text'];D.write_json_file(u,A);Ac.hostname=A[l];BB();return M(B,A[l])
		@Q.route('/get-host-name',[h])
		def t(request):return M(request,A[l])
		@Q.route('/update-volume',[h])
		def t(request):B=request;global A;F=B.json();A[AH]=F['text'];A[AG]=E;D.write_json_file(Ao,A);C('/sd/menu_voice_commands/volume.wav');Ae(A[AH],E);return M(B,A[AH])
		@Q.route('/get-volume',[h])
		def t(request):return M(request,A[AH])
	except BC as Ad:AJ=E;D.log_item(Ad)
H('web server')
def B_():global A;A[L]=165;A[a]=100;A[N]=0;A[S]=150;A[A8]=E;A[A9]=K;A[l]=BP;A[AG]=K
def F(seconds):
	if A[AG]:C=BY(BX,seconds);B.voice[0].level=C
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
	A=b.WaveFile(W(file_name,Y));B.voice[0].play(A,loop=E)
	while B.voice[0].playing:C0()
def CF():
	B.voice[0].stop()
	while B.voice[0].playing:0
def C0():
	F(.02);G.update()
	if G.fell:B.voice[0].stop()
def A6():C('/sd/menu_voice_commands/press_left_button_right_button.wav')
def A2():C('/sd/menu_voice_commands/option_selected.wav')
def B7():C('/sd/menu_voice_commands/now_we_can_adjust_the_feller_position.wav');C(BQ)
def B8():C('/sd/menu_voice_commands/now_we_can_adjust_the_tree_position.wav');C(BQ)
def C1():C('/sd/menu_voice_commands/main_menu.wav');A6()
def C2():C('/sd/menu_voice_commands/sound_selection_menu.wav');A6()
def C3():C('/sd/menu_voice_commands/adjust_feller_and_tree_menu.wav');A6()
def C4():C('/sd/menu_voice_commands/move_feller_and_tree_menu.wav');A6()
def AC():C('/sd/menu_voice_commands/dialog_selection_menu.wav');A6()
def AD():C('/sd/menu_voice_commands/web_menu.wav');A6()
def B9(min_servo_pos,max_servo_pos,servo_pos):
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
	if B9(min_servo_pos,max_servo_pos,A[B]):servo.angle=A[B]
	else:A[B]+=1*sign
def Ag(servo,movement_type,sign,min_servo_pos,max_servo_pos):
	B=movement_type;global A;A[B]+=1*sign
	if B9(min_servo_pos,max_servo_pos,A[B]):servo.angle=A[B]
	else:A[B]-=1*sign
def Ah():C(f);global A;D.write_json_file(u,A)
def AK(servo,movement_type):
	C=servo;B=movement_type
	if B==N or B==S:D=q;H=r;I=1
	else:D=o;H=p;I=-1
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
def e(new_position,speed):
	A=new_position;global A0;B=1
	if A0>A:B=-1
	for C in i(A0,A,B):AL(C);F(speed)
	AL(A)
def V(new_position,speed):
	A=new_position;global z;B=1
	if z>A:B=-1
	for C in i(z,A,B):A3(C);F(speed)
	A3(A)
def AL(servo_pos):
	A=servo_pos
	if A<q:A=q
	if A>r:A=r
	w.angle=A;global A0;A0=A
def A3(servo_pos):
	A=servo_pos
	if A<o:A=o
	if A>p:A=p
	x.angle=A;global z;z=A
def R():C6()
H('servo helpers')
def BA():
	D=7;C=.2
	while B.voice[0].playing:
		E=y.switch_state(G,J,F,5)
		if E==A4:
			B.voice[0].stop()
			while B.voice[0].playing:0
			return
		w.angle=D+A[N];F(C);w.angle=A[N];F(C)
def C5():
	D=2;C=.2
	while B.voice[0].playing:
		E=y.switch_state(G,J,F,5)
		if E==A4:
			B.voice[0].stop()
			while B.voice[0].playing:0
			return
		x.angle=A[L];F(C);x.angle=A[L]-D;F(C)
def AM(sound_files,folder):
	C=folder;A=sound_files;L=j(A)-1;I=v.randint(0,L);D.log_item(C+': '+X(I));K=b.WaveFile(W('/sd/'+C+'/'+A[I]+T,Y));B.voice[0].play(K,loop=E)
	while B.voice[0].playing:
		F(.1);M=y.switch_state(G,J,F,5)
		if M==A4:
			B.voice[0].stop()
			while B.voice[0].playing:0
	K.deinit();H(AE)
def C6():
	p='Sound file: ';o='/sd/feller_sounds/sounds_';g='/sd/menu_voice_commands/animation_canceled.wav';F(.05)
	if A[A8]:
		U=v.randint(0,3)
		if U==0:AM(Bl,BE)
		if U==1:AM(Bp,BG)
		if U==2:AM(Bn,BF)
		if U==3:AM(Br,BH)
	P=1;Z=v.randint(2,7);d=j(B2)-1;h=v.randint(0,d);k=v.randint(2,Z);D.log_item('Chop total: '+X(Z)+' what to speak: '+X(h)+' when to speak: '+X(k));l=E;q=A[L]-3;M=A[O]
	if M==Al:d=j(A5)-2;Q=v.randint(0,d);M=A5[Q];A7('Random sound file: '+A5[Q])
	if M==An:Q=v.randint(0,6);I=o+M+X(Q)+T;A7(p+M+X(Q))
	else:I=o+M+T;A7(p+M)
	m=b.WaveFile(W(I,Y))
	while P<=Z:
		if k==P and not l and A[A9]:l=K;I='/sd/feller_dialog/'+B2[h]+T;C=b.WaveFile(W(I,Y));B.voice[0].play(C,loop=E);BA();C.deinit();H(AE)
		C=b.WaveFile(W('/sd/feller_chops/chop'+X(P)+T,Y));P+=1
		for c in i(A[N],A[S]+5,10):
			AL(c)
			if c>=A[S]-10:
				B.voice[0].play(C,loop=E);f=2;F(.2)
				for r in i(f):A3(q);F(.1);A3(A[L]);F(.1)
				break
		if P<=Z:
			for c in i(A[S],A[N],-5):AL(c);F(.02)
	while B.voice[0].playing:F(.1)
	B.voice[0].play(m,loop=E)
	for s in i(A[L],A[a],-5):A3(s);F(.06)
	f=8
	for r in i(f):A3(A[a]);F(.1);A3(7+A[a]);F(.1)
	if M==Am:
		A7('Alien sequence starting....');F(2);e(A[N],.01);V(A[L],.01);t=A[L];u=A[L]-8
		while B.voice[0].playing:
			R=y.switch_state(G,J,F,5)
			if R==A4:
				B.voice[0].stop()
				while B.voice[0].playing:0
				I=g;C=b.WaveFile(W(I,Y));B.voice[0].play(C,loop=E)
				while B.voice[0].playing:0
				break
			V(t,.1);V(u,.1)
		V(A[L],.04)
		for n in i(7):
			I='/sd/feller_alien/human_'+X(n+1)+T;C=b.WaveFile(W(I,Y));B.voice[0].play(C,loop=E);BA();I='/sd/feller_alien/alien_'+X(n+1)+T;C=b.WaveFile(W(I,Y));B.voice[0].play(C,loop=E);C5();R=y.switch_state(G,J,F,5)
			if R==A4:
				B.voice[0].stop()
				while B.voice[0].playing:0
				I=g;C=b.WaveFile(W(I,Y));B.voice[0].play(C,loop=E)
				while B.voice[0].playing:0
				break
	else:
		while B.voice[0].playing:
			R=y.switch_state(G,J,F,5)
			if R==A4:
				B.voice[0].stop()
				while B.voice[0].playing:0
				I=g;C=b.WaveFile(W(I,Y));B.voice[0].play(C,loop=E)
				while B.voice[0].playing:0
				break
	C.deinit();m.deinit();H('deinit wave0 wave1');e(A[N],.01);F(.02);V(A[L],.01)
class C7:
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
	def reset(A):Aw()
class I:
	def __init__(A):0
	@k
	def name(self):return''
	def enter(A,machine):0
	def exit(A,machine):0
	def update(B,machine):
		A=machine
		if G.fell:A.paused_state=A.state.name;A.pause();return E
		return K
class C8(I):
	def __init__(A):0
	@k
	def name(self):return P
	def enter(E,machine):
		F(.1)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:e(A[N],.01);V(A[L],.01);C('/sd/menu_voice_commands/animations_are_now_active.wav')
		D.log_item('Entered base state');I.enter(E,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(B,machine):
		global s;A=y.switch_state(G,J,F,30)
		if A==A4:
			if s:s=E;C(BJ)
			else:s=K;C(BI)
		elif A=='left'or s:R()
		elif A=='right':machine.go_to_state(Ai)
class C9(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return AP
	def enter(A,machine):D.log_item('Move feller and tree menu');C4();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(B,machine):
		G.update();J.update()
		if G.fell:
			C(AA+AY[B.menuIndex]+T);B.selectedMenuIndex=B.menuIndex;B.menuIndex+=1
			if B.menuIndex>j(AY)-1:B.menuIndex=0
		if J.fell:
			D=AY[B.selectedMenuIndex]
			if D==BR:e(A[N],.01)
			elif D==BS:e(A[S],.01)
			elif D==BT:V(A[L],.01)
			elif D==BU:V(A[a],.01)
			else:C(f);machine.go_to_state(P)
class CA(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return AO
	def enter(A,machine):D.log_item('Adjust feller and tree menu');C3();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(D,machine):
		E=machine;G.update();J.update()
		if G.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(AA+AX[D.menuIndex]+T);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>j(AX)-1:D.menuIndex=0
		if J.fell:
			F=AX[D.selectedMenuIndex]
			if F==BR:e(A[N],.01);B7();AK(w,N);E.go_to_state(P)
			elif F==BS:e(A[S],.01);B7();AK(w,S);E.go_to_state(P)
			elif F==BT:V(A[L],.01);B8();AK(x,L);E.go_to_state(P)
			elif F==BU:V(A[a],.01);B8();AK(x,a);E.go_to_state(P)
			else:C(f);E.go_to_state(P)
class CB(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Ap
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
				if F.menuIndex>j(AZ)-1:F.menuIndex=0
		if J.fell:
			H=AZ[F.selectedMenuIndex]
			if H==BM:A[A8]=K;A2();AC()
			elif H==BN:A[A8]=E;A2();AC()
			elif H=='lumberjack_advice_on':A[A9]=K;A2();AC()
			elif H=='lumberjack_advice_off':A[A9]=E;A2();AC()
			else:D.write_json_file(u,A);C(f);machine.go_to_state(P)
class CC(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Aq
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
				if F.menuIndex>j(Aa)-1:F.menuIndex=0
		if J.fell:
			H=Aa[F.selectedMenuIndex]
			if H=='web_on':A[Aj]=K;A2();AD()
			elif H=='web_off':A[Aj]=E;A2();AD()
			elif H=='hear_url':Ae(A[l],K);AD()
			elif H=='hear_instr_web':C('/sd/menu_voice_commands/web_instruct.wav');AD()
			else:D.write_json_file(u,A);C(f);machine.go_to_state(P)
class CD(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return AN
	def enter(A,machine):D.log_item('Choose sounds menu');C2();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(E,machine):
		G.update();J.update()
		if G.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C('/sd/menu_voice_commands/option_'+A5[E.menuIndex]+T);E.selectedMenuIndex=E.menuIndex;E.menuIndex+=1
				if E.menuIndex>j(A5)-1:E.menuIndex=0
		if J.fell:A[O]=A5[E.selectedMenuIndex];D.log_item('Selected index: '+X(E.selectedMenuIndex)+' Saved option: '+A[O]);D.write_json_file(u,A);A2();machine.go_to_state(P)
class CE(I):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Ai
	def enter(A,machine):D.log_item('Main menu');C1();I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(A,machine):
		D=machine;G.update();J.update()
		if G.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(AA+AW[A.menuIndex]+T);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>j(AW)-1:A.menuIndex=0
		if J.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				E=AW[A.selectedMenuIndex]
				if E==AN:D.go_to_state(AN)
				elif E==AO:D.go_to_state(AO)
				elif E==AP:D.go_to_state(AP)
				elif E==Ap:D.go_to_state(Ap)
				elif E==Aq:D.go_to_state(Aq)
				else:C(f);D.go_to_state(P)
class CG(I):
	def __init__(A):super().__init__()
	@k
	def name(self):return'example'
	def enter(A,machine):I.enter(A,machine)
	def exit(A,machine):I.exit(A,machine)
	def update(A,machine):I.update(A,machine)
H('state machine')
Z=C7()
Z.add_state(C8())
Z.add_state(CE())
Z.add_state(CD())
Z.add_state(CA())
Z.add_state(C9())
Z.add_state(CB())
Z.add_state(CC())
AB.value=K
def BB():
	C('/sd/menu_voice_commands/animator_available_on_network.wav');C('/sd/menu_voice_commands/to_access_type.wav')
	if A[l]==BP:C('/sd/menu_voice_commands/animator_feller_local.wav')
	else:Ae(A[l],K)
	C('/sd/menu_voice_commands/in_your_browser.wav')
if AJ:
	D.log_item('starting server...')
	try:Q.start(X(A1.radio.ipv4_address));D.log_item('Listening on http://%s:80'%A1.radio.ipv4_address);BB()
	except OSError:time.sleep(5);D.log_item('restarting...');Aw()
Z.go_to_state(P)
D.log_item('animator has started...')
H('animations started.')
while K:
	Z.update();F(.1)
	if AJ:
		try:Q.poll()
		except BC as Ad:D.log_item(Ad);continue