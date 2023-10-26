BZ='right_held'
BY='Choose sounds menu'
BX='Select a program option'
BW='left_held'
BV='/sd/menu_voice_commands/animations_are_now_active.wav'
BU='/sd/menu_voice_commands/create_sound_track_files.wav'
BT='/sd/menu_voice_commands/local.wav'
BS='/sd/menu_voice_commands/dot.wav'
BR='animator-lightning'
BQ='Utility: '
BP='timestamp_mode_off'
BO='/sd/menu_voice_commands/timestamp_mode_on.wav'
BN='timestamp_mode_on'
BM='/sd/menu_voice_commands/continuous_mode_deactivated.wav'
BL='/sd/menu_voice_commands/continuous_mode_activated.wav'
BK='wav/no_card.wav'
BJ=Exception
A_='Set Web Options'
Az='web_options'
Ay='light_string_setup_menu'
Ax='choose_my_sounds'
Aw='choose_sounds'
Av='right'
Au='left'
At='/sd/menu_voice_commands/option_selected.wav'
As='volume_pot_on'
Ar='volume_pot_off'
Aq='/sd/menu_voice_commands/timestamp_mode_off.wav'
Ap='/sd/menu_voice_commands/timestamp_instructions.wav'
Ao='alien_lightshow'
An='inspiring_cinematic_ambient_lightshow'
Am='thunder_birds_rain'
Al='random_all'
Ak='random_my'
Aj='random_built_in'
Ai='utf8'
Ah='config wifi imports'
Ag='main_menu'
Af='serve_webpage'
Ae=enumerate
AJ='/sd/customers_owned_music/'
AI='text'
AH='end'
AG='start'
AF='volume_settings'
AB='flashTime'
AA='add_sounds_animate'
A4='action'
A2='volume_pot'
A1='/sd/lightning_sounds/'
A0=1.
t='.json'
s='customers_owned_music_'
r=str
o='HOST_NAME'
k=property
i='/sd/menu_voice_commands/'
h='volume'
g=''
d='rb'
c=open
Z='/sd/menu_voice_commands/all_changes_complete.wav'
V='base_state'
U=range
T='light_string'
S='.wav'
R='/sd/config_lightning.json'
Q=len
O=print
J=True
H='option_selected'
G=False
import gc,files as E
def W(collection_point):gc.collect();A=gc.mem_free();E.log_item('Point '+collection_point+' Available memory: {} bytes'.format(A))
W('Imports gc, files')
import time as L,audiocore as b,audiomixer as Ba,audiobusio as Bb,sdcardio as B0,storage as AC,busio,digitalio as p,board as a,neopixel as B1,random as F,rtc,microcontroller as AK
from analogio import AnalogIn as Bc
from rainbowio import colorwheel as B2
from adafruit_debouncer import Debouncer as B3
def Bd():AK.on_next_reset(AK.RunMode.NORMAL);AK.reset()
W('imports')
Be=Bc(a.A0)
def Bf(pin,wait_for):
	B=wait_for/10;A=0
	for C in U(10):L.sleep(B);A+=1;A=A/10
	return pin.value/65536
A5=p.DigitalInOut(a.GP28)
A5.direction=p.Direction.OUTPUT
A5.value=G
Bg=a.GP6
Bh=a.GP7
AL=p.DigitalInOut(Bg)
AL.direction=p.Direction.INPUT
AL.pull=p.Pull.UP
I=B3(AL)
AM=p.DigitalInOut(Bh)
AM.direction=p.Direction.INPUT
AM.pull=p.Pull.UP
M=B3(AM)
Bi=a.GP18
Bj=a.GP19
Bk=a.GP20
Bl=Bb.I2SOut(bit_clock=Bi,word_select=Bj,data=Bk)
A5.value=J
Bm=a.GP2
Bn=a.GP3
Bo=a.GP4
B4=a.GP5
B5=busio.SPI(Bm,Bn,Bo)
Bp=2
B=Ba.Mixer(voice_count=Bp,sample_rate=22050,channel_count=2,bits_per_sample=16,samples_signed=J,buffer_size=4096)
Bl.play(B)
B6=.2
B.voice[0].level=B6
B.voice[1].level=B6
try:AN=B0.SDCard(B5,B4);AO=AC.VfsFat(AN);AC.mount(AO,'/sd')
except:
	A6=b.WaveFile(c(BK,d));B.voice[0].play(A6,loop=G)
	while B.voice[0].playing:0
	B7=G
	while not B7:
		I.update()
		if I.fell:
			try:
				AN=B0.SDCard(B5,B4);AO=AC.VfsFat(AN);AC.mount(AO,'/sd');B7=J;A6=b.WaveFile(c('/sd/menu_voice_commands/micro_sd_card_success.wav',d));B.voice[0].play(A6,loop=G)
				while B.voice[0].playing:0
			except:
				A6=b.WaveFile(c(BK,d));B.voice[0].play(A6,loop=G)
				while B.voice[0].playing:0
A5.value=G
Bq=rtc.RTC()
Bq.datetime=L.struct_time((2019,5,29,15,14,15,0,-1,-1))
A=E.read_json_file(R)
u=A['options']
l=E.return_directory(s,'/sd/customers_owned_music',S)
A7=[]
A7.extend(l)
A7.extend(u)
Br=E.return_directory(g,'/sd/time_stamp_defaults',t)
AD=A[Af]
Bs=E.read_json_file('/sd/menu_voice_commands/main_menu.json')
AP=Bs[Ag]
Bt=E.read_json_file('/sd/menu_voice_commands/web_menu.json')
AQ=Bt['web_menu']
Bu=E.read_json_file('/sd/menu_voice_commands/light_string_menu.json')
AR=Bu['light_string_menu']
Bv=E.read_json_file('/sd/menu_voice_commands/light_options.json')
v=Bv['light_options']
Bw=E.read_json_file('/sd/menu_voice_commands/volume_settings.json')
AS=Bw[AF]
Bx=E.read_json_file('/sd/menu_voice_commands/add_sounds_animate.json')
AT=Bx[AA]
W('config setup')
q=G
m=G
w=[]
x=[]
AU=[]
AV=[]
AW=[]
AX=[]
N=0
D=B1.NeoPixel(a.GP10,N)
def B8(part):
	B=[]
	for D in w:
		for A in D:C=A;break
		if part==AG:
			for A in U(0,5):B.append(A+C)
		if part==AH:
			for A in U(5,10):B.append(A+C)
	return B
def B9(part):
	B=[]
	for D in x:
		for A in D:C=A;break
		if part==AG:
			for A in U(0,2):B.append(A+C)
		if part==AH:
			for A in U(2,4):B.append(A+C)
	return B
def By():
	global AU,AV,AW,AX;AU=B8(AG);AV=B8(AH);AW=B9(AG);AX=B9(AH)
	for B in w:
		for A in B:D[A]=50,50,50
		D.show();L.sleep(.3);D.fill((0,0,0));D.show()
	for C in x:
		for A in C:D[A]=50,50,50
		D.show();L.sleep(.3);D.fill((0,0,0));D.show()
def A8():
	global w,x,N,D,N;w=[];x=[];N=0;F=A[T].split(',')
	for H in F:
		C=H.split('-')
		if Q(C)==2:
			E,B=C;B=int(B)
			if E=='bar':I=list(U(N,N+B));w.append(I);N+=B
			elif E=='bolt':J=list(U(N,N+B));x.append(J);N+=B
	O('Number of pixels total: ',N);D.deinit();W('Deinit ledStrip');D=B1.NeoPixel(a.GP10,N);D.auto_write=G;D.brightness=A0;By()
A8()
W('Neopixels setup')
if AD:
	import socketpool as Bz,mdns;W(Ah);import wifi as y;W(Ah);from adafruit_httpserver import Server,Request,FileResponse as AY,Response as e,POST as j;W(Ah);E.log_item('Connecting to WiFi');BA='jimmytrainsguest';BB=g
	try:BC=E.read_json_file('/sd/env.json');BA=BC['WIFI_SSID'];BB=BC['WIFI_PASSWORD'];W('wifi env');O('Using env ssid and password')
	except:O('Using default ssid and password')
	try:
		y.radio.connect(BA,BB);W('wifi connect');AZ=mdns.Server(y.radio);AZ.hostname=A[o];AZ.advertise_service(service_type='_http',protocol='_tcp',port=80);B_=[hex(A)for A in y.radio.mac_address];E.log_item('My MAC addr:'+r(B_));C0=r(y.radio.ipv4_address);E.log_item('My IP address is'+C0);E.log_item('Connected to WiFi');C1=Bz.SocketPool(y.radio);X=Server(C1,'/static',debug=J);W('wifi server')
		@X.route('/')
		def BD(request):W('Home page.');return AY(request,'index.html','/')
		@X.route('/mui.min.css')
		def BD(request):return AY(request,'mui.min.css','/')
		@X.route('/mui.min.js')
		def BD(request):return AY(request,'mui.min.js','/')
		@X.route('/animation',[j])
		def n(request):
			P='thunder_distant';O='thunder_and_rain';N='halloween_thunder';M='epic_thunder';L='dark_thunder';K='continuous_thunder';D=request;global A;global q;B=D.raw_request.decode(Ai)
			if Aj in B:A[H]=Aj;Y(A[H])
			elif Ak in B:A[H]=Ak;Y(A[H])
			elif Al in B:A[H]=Al;Y(A[H])
			elif Am in B:A[H]=Am;Y(A[H])
			elif K in B:A[H]=K;Y(A[H])
			elif L in B:A[H]=L;Y(A[H])
			elif M in B:A[H]=M;Y(A[H])
			elif N in B:A[H]=N;Y(A[H])
			elif O in B:A[H]=O;Y(A[H])
			elif P in B:A[H]=P;Y(A[H])
			elif An in B:A[H]=An;Y(A[H])
			elif Ao in B:A[H]=Ao;Y(A[H])
			elif s in B:
				for F in l:
					if F in B:A[H]=F;Y(A[H]);break
			elif'cont_mode_on'in B:q=J;C(BL)
			elif'cont_mode_off'in B:q=G;C(BM)
			elif BN in B:Q=J;C(BO);C(Ap)
			elif BP in B:Q=G;C(Aq)
			elif'reset_animation_timing_to_defaults'in B:
				for I in Br:S=E.read_json_file('/sd/time_stamp_defaults/'+I+t);E.write_json_file(A1+I+t,S)
			E.write_json_file(R,A);return e(D,'Animation '+A[H]+' started.')
		@X.route('/utilities',[j])
		def n(request):
			I='reset_to_defaults';H='speaker_test';F=request;global A;B=g;D=F.raw_request.decode(Ai)
			if H in D:B=H;C('/sd/menu_voice_commands/left_speaker_right_speaker.wav')
			elif Ar in D:B=Ar;A[A2]=G;E.write_json_file(R,A);C(Z)
			elif As in D:B=As;A[A2]=J;E.write_json_file(R,A);C(Z)
			elif I in D:B=I;C2();E.write_json_file(R,A);C(Z);f.go_to_state(V)
			return e(F,BQ+B)
		@X.route('/lights',[j])
		def n(request):
			O='set_to_100';N='set_to_80';M='set_to_60';L='set_to_40';K='set_to_20';J='set_to_0';I='set_to_white';H='set_to_blue';G='set_to_green';F='set_to_red';E=request;global A;B=g;C=E.raw_request.decode(Ai)
			if F in C:B=F;D.fill((255,0,0));D.show()
			elif G in C:B=G;D.fill((0,255,0));D.show()
			elif H in C:B=H;D.fill((0,0,255));D.show()
			elif I in C:B=I;D.fill((255,255,255));D.show()
			elif J in C:B=J;D.brightness=.0;D.show()
			elif K in C:B=K;D.brightness=.2;D.show()
			elif L in C:B=L;D.brightness=.4;D.show()
			elif M in C:B=M;D.brightness=.6;D.show()
			elif N in C:B=N;D.brightness=.8;D.show()
			elif O in C:B=O;D.brightness=A0;D.show()
			return e(E,BQ+B)
		@X.route('/update-host-name',[j])
		def n(request):B=request;global A;C=B.json();A[o]=C[AI];E.write_json_file(R,A);AZ.hostname=A[o];BI();return e(B,A[o])
		@X.route('/get-host-name',[j])
		def n(request):return e(request,A[o])
		@X.route('/update-volume',[j])
		def n(request):B=request;global A;C=B.json();Ac(C[A4]);return e(B,A[h])
		@X.route('/get-volume',[j])
		def n(request):return e(request,A[h])
		@X.route('/update-light-string',[j])
		def n(request):
			G=' data: ';F='action: ';D=request;global A;B=D.json()
			if B[A4]=='save'or B[A4]=='clear'or B[A4]=='defaults':A[T]=B[AI];O(F+B[A4]+G+A[T]);E.write_json_file(R,A);A8();C(Z);return e(D,A[T])
			if A[T]==g:A[T]=B[AI]
			else:A[T]=A[T]+','+B[AI]
			O(F+B[A4]+G+A[T]);E.write_json_file(R,A);A8();C(Z);return e(D,A[T])
		@X.route('/get-light-string',[j])
		def n(request):return e(request,A[T])
		@X.route('/get-customers-sound-tracks',[j])
		def n(request):A=E.json_stringify(l);return e(request,A)
	except BJ as Aa:AD=G;E.log_item(Aa)
W('web server')
import utilities as Ab
W('utilities')
def P(seconds):
	D=seconds
	if A[A2]:C=Bf(Be,D);B.voice[0].level=C
	else:
		try:C=int(A[h])/100
		except:C=.5
		if C<0 or C>1:C=.5
		B.voice[0].level=C;B.voice[1].level=C;L.sleep(D)
def BE():global A;A[T]='bar-10,bolt-4,bar-10,bolt-4,bar-10,bolt-4'
def C2():global A;A[A2]=J;A[o]=BR;A[H]=Am;A[h]='30';BE()
def Ac(action):
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
	A[h]=r(B);A[A2]=G;E.write_json_file(R,A);C('/sd/menu_voice_commands/volume.wav');AE(A[h],G)
def C(file_name):
	if B.voice[0].playing:
		B.voice[0].stop()
		while B.voice[0].playing:P(.02)
	A=b.WaveFile(c(file_name,d));B.voice[0].play(A,loop=G)
	while B.voice[0].playing:C3()
def CR():
	B.voice[0].stop()
	while B.voice[0].playing:0
def C3():
	P(.02);I.update()
	if I.fell:B.voice[0].stop()
def AE(str_to_speak,addLocal):
	for A in str_to_speak:
		if A==' ':A='space'
		if A=='-':A='dash'
		if A=='.':A='dot'
		C(i+A+S)
	if addLocal:C(BS);C(BT)
def C4():C('/sd/menu_voice_commands/sound_selection_menu.wav');z()
def C5():C('/sd/menu_voice_commands/choose_my_sounds_menu.wav');z()
def z():C('/sd/menu_voice_commands/press_left_button_right_button.wav')
def C6():C('/sd/menu_voice_commands/main_menu.wav');z()
def C7():C('/sd/menu_voice_commands/add_sounds_animate.wav');z()
def A9():C('/sd/menu_voice_commands/web_menu.wav');z()
def C8():C('/sd/menu_voice_commands/volume_settings_menu.wav');z()
def C9():C('/sd/menu_voice_commands/light_string_setup_menu.wav');z()
def CA():C('/sd/menu_voice_commands/string_instructions.wav')
def BF():C(At)
def BG(play_intro):
	if play_intro:C('/sd/menu_voice_commands/current_light_settings_are.wav')
	B=A[T].split(',')
	for(D,E)in Ae(B):C('/sd/menu_voice_commands/position.wav');C(i+r(D+1)+S);C('/sd/menu_voice_commands/is.wav');C(i+E+S)
def CB():
	C('/sd/menu_voice_commands/no_user_soundtrack_found.wav')
	while J:
		I.update();M.update()
		if I.fell:break
		if M.fell:C(BU);break
def Y(file_name):
	G='Sound file: ';E='Random sound file: ';C=file_name;O(C);A=C
	if C==Aj:D=Q(u)-4;B=F.randint(0,D);A=u[B];O(E+u[B]);O(G+A)
	elif C==Ak:D=Q(l)-1;B=F.randint(0,D);A=l[B];O(E+l[B]);O(G+A)
	elif C==Al:D=Q(A7)-4;B=F.randint(0,D);A=A7[B];O(E+A7[B]);O(G+A)
	if m:CC(A)
	elif s in A:Ad(A)
	elif A==Ao:Ad(A)
	elif A==An:Ad(A)
	else:CD(A)
def Ad(file_name):
	K=file_name;global m;R=1;T=3;U=s in K
	if U:
		K=K.replace(s,g)
		try:V=E.read_json_file(AJ+K+t)
		except:
			C('/sd/menu_voice_commands/no_timestamp_file_found.wav')
			while J:
				I.update();M.update()
				if I.fell:m=G;return
				if M.fell:m=J;C(Ap);return
	else:V=E.read_json_file(A1+K+t)
	N=V[AB];Z=Q(N);D=0
	if U:W=b.WaveFile(c(AJ+K+S,d))
	else:W=b.WaveFile(c(A1+K+S,d))
	B.voice[0].play(W,loop=G);a=L.monotonic();A=0
	while J:
		X=0;Y=L.monotonic()-a
		if D<Q(N)-2:H=N[D+1]-N[D]-.25
		else:H=.25
		if H<0:H=0
		if Y>N[D]-.25:
			O('time elasped: '+r(Y)+' Timestamp: '+r(N[D]));D+=1;A=F.randint(R,T)
			while A==X:O('regenerating random selection');A=F.randint(R,T)
			if A==1:CE(.005,H)
			elif A==2:BH(.01);P(H)
			elif A==3:CF(H)
			elif A==4:CG(H)
			elif A==5:BH(H)
			X=A
		if Z==D:D=0
		I.update()
		if I.fell:B.voice[0].stop()
		if not B.voice[0].playing:break
		P(.001)
def CC(file_name):
	A=file_name;O('time stamp mode');global m;H=s in A;F=E.read_json_file('/sd/time_stamp_defaults/timestamp_mode.json');F[AB]=[];A=A.replace(s,g)
	if H:I=b.WaveFile(c(AJ+A+S,d))
	else:I=b.WaveFile(c(A1+A+S,d))
	B.voice[0].play(I,loop=G);N=L.monotonic();P(.1)
	while J:
		K=L.monotonic()-N;M.update()
		if M.fell:F[AB].append(K);O(K)
		if not B.voice[0].playing:
			D.fill((0,0,0));D.show();F[AB].append(5000)
			if H:E.write_json_file(AJ+A+t,F)
			else:E.write_json_file(A1+A+t,F)
			break
	m=G;C('/sd/menu_voice_commands/timestamp_saved.wav');C(Aq);C(BV)
def CD(file_name):
	C=file_name;K=E.read_json_file(A1+C+t);D=K[AB];N=Q(D);A=0;R=b.WaveFile(c(A1+C+S,d));B.voice[0].play(R,loop=G);T=L.monotonic()
	while J:
		P(.1);H=L.monotonic()-T;M.update()
		if M.fell:O(H)
		if H>D[A]-F.uniform(.5,1):A+=1;CH()
		if N==A:A=0
		I.update()
		if I.fell:B.voice[0].stop()
		if not B.voice[0].playing:break
def CS(ledStrip):A=ledStrip;A.brightness=A0;B=F.randint(0,255);C=F.randint(0,255);D=F.randint(0,255);A.fill((B,C,D));A.show()
def CE(speed,duration):
	G=duration;F=speed;H=L.monotonic()
	for B in U(0,255,1):
		for A in U(N):C=A*256//N+B;D[A]=B2(C&255)
		D.show();P(F);E=L.monotonic()-H
		if E>G:return
	for B in reversed(U(0,255,1)):
		for A in U(N):C=A*256//N+B;D[A]=B2(C&255)
		D.show();P(F);E=L.monotonic()-H
		if E>G:return
def CF(duration):
	K=L.monotonic();D.brightness=A0;A=[];A.extend(AU);A.extend(AV);B=[];B.extend(AW);B.extend(AX);C=F.randint(0,255);E=F.randint(0,255);G=F.randint(0,255)
	for H in B:D[H]=C,E,G
	C=F.randint(0,255);E=F.randint(0,255);G=F.randint(0,255)
	while J:
		for H in A:I=F.randint(0,110);M=A3(C-I,0,255);N=A3(E-I,0,255);O=A3(G-I,0,255);D[H]=M,N,O;D.show()
		P(F.uniform(.05,.1));Q=L.monotonic()-K
		if Q>duration:return
def CG(duration):
	G=L.monotonic();D.brightness=A0
	while J:
		for H in U(0,N):
			I=F.randint(0,255);K=F.randint(0,255);M=F.randint(0,255);A=F.randint(0,1)
			if A==0:B=I;C=0;E=0
			elif A==1:B=0;C=K;E=0
			elif A==2:B=0;C=0;E=M
			D[H]=B,C,E;D.show()
		P(F.uniform(.2,.3));O=L.monotonic()-G
		if O>duration:return
def BH(duration):
	G=L.monotonic();D.brightness=A0
	while J:
		for H in U(0,N):
			I=F.randint(128,255);K=F.randint(128,255);M=F.randint(128,255);A=F.randint(0,2)
			if A==0:B=I;C=0;E=0
			elif A==1:B=0;C=K;E=0
			elif A==2:B=0;C=0;E=M
			D[H]=B,C,E;D.show()
		P(F.uniform(.2,.3));O=L.monotonic()-G
		if O>duration:return
def CH():
	E=[];O=F.randint(-1,Q(x)-1)
	if O!=-1:
		for(M,N)in Ae(x):
			if M==O:E.extend(N)
	for(M,N)in Ae(w):
		if M==F.randint(0,Q(w)-1):E.extend(N)
	G=F.randint(40,80);H=F.randint(10,25);I=F.randint(0,10);P=F.randint(5,10);R=150;S=255;T=F.randint(R,S)/255;D.brightness=T;J=0;K=75;V=1;W=50
	for X in U(0,P):
		B=F.randint(0,50)
		if B<0:B=0
		for C in E:D[C]=G+B,H+B,I+B
		D.show();A=F.randint(J,K);A=A/1000;L.sleep(A);D.fill((0,0,0));D.show()
		for C in E:D[C]=G+B,H+B,I+B
		D.show();A=F.randint(J,K);A=A/1000;L.sleep(A);D.fill((0,0,0));D.show()
		for C in E:D[C]=G+B,H+B,I+B
		D.show();A=F.randint(J,K);A=A/1000;L.sleep(A);D.fill((0,0,0));D.show()
		for C in E:D[C]=G+B,H+B,I+B
		D.show();A=F.randint(J,K);A=A/1000;L.sleep(A);D.fill((0,0,0));D.show();A=F.randint(V,W);A=A/1000;L.sleep(A);D.fill((0,0,0));D.show()
def CT(num_times):
	D.brightness=A0;B=226;C=121;E=35
	for K in U(num_times):
		for G in U(0,N):A=F.randint(0,110);H=A3(B-A,0,255);I=A3(C-A,0,255);J=A3(E-A,0,255);D[G]=H,I,J;D.show()
		P(F.uniform(.05,.1))
def A3(my_color,lower,upper):
	C=upper;B=lower;A=my_color
	if A<B:A=B
	if A>C:A=C
	return A
class CI:
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
class K:
	def __init__(A):0
	@k
	def name(self):return g
	def enter(A,machine):0
	def exit(A,machine):0
	def update(B,machine):
		A=machine
		if I.fell:A.paused_state=A.state.name;A.pause();return G
		return J
class CJ(K):
	def __init__(A):0
	@k
	def name(self):return V
	def enter(A,machine):C(BV);E.log_item('Entered base state');K.enter(A,machine)
	def exit(A,machine):K.exit(A,machine)
	def update(D,machine):
		global q;B=Ab.switch_state(I,M,P,3.)
		if B==BW:
			if q:q=G;C(BM)
			else:q=J;C(BL)
		elif B==Au or q:Y(A[H])
		elif B==Av:machine.go_to_state(Ag)
class CK(K):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Ag
	def enter(A,machine):E.log_item('Main menu');C6();K.enter(A,machine)
	def exit(A,machine):K.exit(A,machine)
	def update(A,machine):
		D=machine;I.update();M.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AP[A.menuIndex]+S);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>Q(AP)-1:A.menuIndex=0
		if M.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				E=AP[A.selectedMenuIndex]
				if E==Aw:D.go_to_state(Aw)
				elif E==Ax:D.go_to_state(Ax)
				elif E==AA:D.go_to_state(AA)
				elif E==Ay:D.go_to_state(Ay)
				elif E==Az:D.go_to_state(Az)
				elif E==AF:D.go_to_state(AF)
				else:C(Z);D.go_to_state(V)
class CL(K):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@k
	def name(self):return Aw
	def enter(A,machine):
		O(BX)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:E.log_item(BY);C4()
		K.enter(A,machine)
	def exit(A,machine):K.exit(A,machine)
	def update(C,machine):
		I.update();M.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				D=b.WaveFile(c('/sd/lightning_options_voice_commands/option_'+u[C.optionIndex]+S,d));B.voice[0].play(D,loop=G);C.currentOption=C.optionIndex;C.optionIndex+=1
				if C.optionIndex>Q(u)-1:C.optionIndex=0
				while B.voice[0].playing:0
		if M.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				A[H]=u[C.currentOption];E.write_json_file(R,A);D=b.WaveFile(c(At,d));B.voice[0].play(D,loop=G)
				while B.voice[0].playing:0
			machine.go_to_state(V)
class CM(K):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@k
	def name(self):return Ax
	def enter(A,machine):
		O(BX)
		if B.voice[0].playing:
			B.voice[0].stop()
			while B.voice[0].playing:0
		else:E.log_item(BY);C5()
		K.enter(A,machine)
	def exit(A,machine):K.exit(A,machine)
	def update(D,machine):
		F=machine;I.update();M.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				try:
					L=l[D.optionIndex].replace(s,g);J=r(D.optionIndex+1);C('/sd/menu_voice_commands/song.wav');AE(J,G);D.currentOption=D.optionIndex;D.optionIndex+=1
					if D.optionIndex>Q(l)-1:D.optionIndex=0
					while B.voice[0].playing:0
				except:CB();F.go_to_state(V);return
		if M.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				try:
					A[H]=l[D.currentOption];E.write_json_file(R,A);K=b.WaveFile(c(At,d));B.voice[0].play(K,loop=G)
					while B.voice[0].playing:0
				except:O('no sound track')
			F.go_to_state(V)
class CN(K):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return AA
	def enter(A,machine):E.log_item(AA);C7();K.enter(A,machine)
	def exit(A,machine):K.exit(A,machine)
	def update(A,machine):
		E=machine;global m;I.update();M.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AT[A.menuIndex]+S);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
				if A.menuIndex>Q(AT)-1:A.menuIndex=0
		if M.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				D=AT[A.selectedMenuIndex]
				if D=='hear_instructions':C(BU)
				elif D==BN:m=J;C(BO);C(Ap);E.go_to_state(V)
				elif D==BP:m=G;C(Aq)
				else:C(Z);E.go_to_state(V)
class CO(K):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return AF
	def enter(A,machine):E.log_item(A_);C8();K.enter(A,machine)
	def exit(A,machine):K.exit(A,machine)
	def update(D,machine):
		F=machine;I.update();M.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AS[D.menuIndex]+S);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>Q(AS)-1:D.menuIndex=0
		if M.fell:
			H=AS[D.selectedMenuIndex]
			if H=='volume_level_adjustment':
				C('/sd/menu_voice_commands/volume_adjustment_menu.wav')
				while J:
					K=Ab.switch_state(I,M,P,3.)
					if K==Au:Ac('lower')
					elif K==Av:Ac('raise')
					elif K==BZ:
						E.write_json_file(R,A);C(Z);F.go_to_state(V);break
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:E.write_json_file(R,A);C(Z);F.go_to_state(V)
					P(.1)
			elif H==Ar:
				A[A2]=G
				if A[h]==0:A[h]=10
				E.write_json_file(R,A);C(Z);F.go_to_state(V)
			elif H==As:A[A2]=J;E.write_json_file(R,A);C(Z);F.go_to_state(V)
class CP(K):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Az
	def enter(A,machine):E.log_item(A_);A9();K.enter(A,machine)
	def exit(A,machine):K.exit(A,machine)
	def update(D,machine):
		I.update();M.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AQ[D.menuIndex]+S);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>Q(AQ)-1:D.menuIndex=0
		if M.fell:
			F=AQ[D.selectedMenuIndex]
			if F=='web_on':A[Af]=J;BF();A9()
			elif F=='web_off':A[Af]=G;BF();A9()
			elif F=='hear_url':AE(A[o],J);A9()
			elif F=='hear_instr_web':C('/sd/menu_voice_commands/web_instruct.wav');A9()
			else:E.write_json_file(R,A);C(Z);machine.go_to_state(V)
class CQ(K):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@k
	def name(self):return Ay
	def enter(A,machine):E.log_item(A_);C9();K.enter(A,machine)
	def exit(A,machine):K.exit(A,machine)
	def update(D,machine):
		K=machine;I.update();M.update()
		if I.fell:
			if B.voice[0].playing:
				B.voice[0].stop()
				while B.voice[0].playing:0
			else:
				C(i+AR[D.menuIndex]+S);D.selectedMenuIndex=D.menuIndex;D.menuIndex+=1
				if D.menuIndex>Q(AR)-1:D.menuIndex=0
		if M.fell:
			F=AR[D.selectedMenuIndex]
			if F=='hear_light_setup_instructions':CA()
			elif F=='reset_lights_defaults':BE();C('/sd/menu_voice_commands/lights_reset_to.wav');BG(G)
			elif F=='hear_current_light_settings':BG(J)
			elif F=='clear_light_string':A[T]=g;C('/sd/menu_voice_commands/lights_cleared.wav')
			elif F=='add_lights':
				C('/sd/menu_voice_commands/add_light_menu.wav')
				while J:
					H=Ab.switch_state(I,M,P,3.)
					if H==Au:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							D.menuIndex-=1
							if D.menuIndex<0:D.menuIndex=Q(v)-1
							D.selectedMenuIndex=D.menuIndex;C(i+v[D.menuIndex]+S)
					elif H==Av:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							D.menuIndex+=1
							if D.menuIndex>Q(v)-1:D.menuIndex=0
							D.selectedMenuIndex=D.menuIndex;C(i+v[D.menuIndex]+S)
					elif H==BZ:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:
							if A[T]==g:A[T]=v[D.selectedMenuIndex]
							else:A[T]=A[T]+','+v[D.selectedMenuIndex]
							C(i+v[D.selectedMenuIndex]+S);C('/sd/menu_voice_commands/added.wav')
					elif H==BW:
						if B.voice[0].playing:
							B.voice[0].stop()
							while B.voice[0].playing:0
						else:E.write_json_file(R,A);C(Z);A8();K.go_to_state(V)
					P(.1)
			else:E.write_json_file(R,A);C(Z);A8();K.go_to_state(V)
class CU(K):
	def __init__(A):super().__init__()
	@k
	def name(self):return'example'
	def enter(A,machine):K.enter(A,machine)
	def exit(A,machine):K.exit(A,machine)
	def update(A,machine):K.update(A,machine)
f=CI()
f.add_state(CJ())
f.add_state(CK())
f.add_state(CL())
f.add_state(CM())
f.add_state(CN())
f.add_state(CO())
f.add_state(CP())
f.add_state(CQ())
A5.value=J
def BI():
	C('/sd/menu_voice_commands/animator_available_on_network.wav');C('/sd/menu_voice_commands/to_access_type.wav')
	if A[o]==BR:C('/sd/menu_voice_commands/animator_dash_lightning.wav');C(BS);C(BT)
	else:AE(A[o],J)
	C('/sd/menu_voice_commands/in_your_browser.wav')
if AD:
	E.log_item('starting server...')
	try:X.start(r(y.radio.ipv4_address));E.log_item('Listening on http://%s:80'%y.radio.ipv4_address);BI()
	except OSError:L.sleep(5);E.log_item('restarting...');Bd()
f.go_to_state(V)
E.log_item('animator has started...')
W('animations started.')
while J:
	f.update();P(.02)
	if AD:
		try:X.poll()
		except BJ as Aa:E.log_item(Aa);continue