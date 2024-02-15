Bg='right_held'
Bf='Set Web Options'
Be='left_held'
Bd='/sd/mvc/animations_are_now_active.wav'
Bc=' Dif: '
Bb=' Timestamp: '
Ba='Time elapsed: '
BZ='fireworks'
BY='/sd/mvc/option_selected.wav'
BX='/sd/mvc/local.wav'
BW='/sd/mvc/dot.wav'
BV='animator-lightning'
BU='/sd/mvc/timestamp_mode_off.wav'
BT='/sd/mvc/timestamp_instructions.wav'
BS='/sd/mvc/continuous_mode_deactivated.wav'
BR='/sd/mvc/continuous_mode_activated.wav'
BQ='random my'
BP='random all'
BO='wav/no_card.wav'
BN=Exception
B3='web_options'
B2='light_string_setup_menu'
B1='choose_sounds'
B0='right'
A_='left'
Az='can_cancel'
Ay='volume_pot_on'
Ax='volume_pot_off'
Aw='Utility: '
Av='config wifi imports'
Au='add_sounds_animate'
At='main_menu'
As='serve_webpage'
Ar='random built in'
Aa='/sd/customers_owned_music/'
AZ='b2'
AY='g2'
AX='b1'
AW='g1'
AV='text'
AU='volume_settings'
AM='flashTime'
AL='utf8'
AK=enumerate
AE='action'
AD='bars'
AA='r2'
A9='r1'
A8='volume_pot'
A7='/sd/lightning_sounds/'
A6='customers_owned_music_'
A5=property
z='.json'
v='option_selected'
u='HOST_NAME'
s='/sd/mvc/'
r=int
o='volume'
n='rb'
m=open
k='base_state'
j=str
g=''
e='b'
d='g'
c='r'
b='/sd/mvc/all_changes_complete.wav'
a=range
V='variation'
U='bolts'
T='light_string'
S='.wav'
R='/sd/config_lightning.json'
Q=print
I=True
H=len
G=False
import gc,files as D
def Y(collection_point):gc.collect();A=gc.mem_free();D.log_item('Point '+collection_point+' Available memory: {} bytes'.format(A))
Y('Imports gc, files')
import time as J,audiocore as l,audiomixer as Bh,audiobusio as Bi,sdcardio as B4,storage as AN,busio,digitalio as w,board as f,random as E,rtc,microcontroller as Ab
from analogio import AnalogIn as Bj
import neopixel as B5
from rainbowio import colorwheel as B6
from adafruit_debouncer import Debouncer as B7
def B8():Ab.on_next_reset(Ab.RunMode.NORMAL);Ab.reset()
Y('imports')
Bk=Bj(f.A0)
def Bl(pin,wait_for):
	B=wait_for/10;A=0
	for C in a(10):J.sleep(B);A+=1;A=A/10
	return pin.value/65536
AF=w.DigitalInOut(f.GP28)
AF.direction=w.Direction.OUTPUT
AF.value=G
Bm=f.GP6
Bn=f.GP7
Ac=w.DigitalInOut(Bm)
Ac.direction=w.Direction.INPUT
Ac.pull=w.Pull.UP
K=B7(Ac)
Ad=w.DigitalInOut(Bn)
Ad.direction=w.Direction.INPUT
Ad.pull=w.Pull.UP
N=B7(Ad)
Bo=f.GP18
Bp=f.GP19
Bq=f.GP20
Br=Bi.I2SOut(bit_clock=Bo,word_select=Bp,data=Bq)
AF.value=I
Bs=f.GP2
Bt=f.GP3
Bu=f.GP4
B9=f.GP5
BA=busio.SPI(Bs,Bt,Bu)
Bv=1
F=Bh.Mixer(voice_count=Bv,sample_rate=22050,channel_count=2,bits_per_sample=16,samples_signed=I,buffer_size=4096)
Br.play(F)
Bw=.2
F.voice[0].level=Bw
try:Ae=B4.SDCard(BA,B9);Af=AN.VfsFat(Ae);AN.mount(Af,'/sd')
except:
	AG=l.WaveFile(m(BO,n));F.voice[0].play(AG,loop=G)
	while F.voice[0].playing:0
	BB=G
	while not BB:
		K.update()
		if K.fell:
			try:
				Ae=B4.SDCard(BA,B9);Af=AN.VfsFat(Ae);AN.mount(Af,'/sd');BB=I;AG=l.WaveFile(m('/sd/mvc/micro_sd_card_success.wav',n));F.voice[0].play(AG,loop=G)
				while F.voice[0].playing:0
			except:
				AG=l.WaveFile(m(BO,n));F.voice[0].play(AG,loop=G)
				while F.voice[0].playing:0
AF.value=G
Bx=rtc.RTC()
Bx.datetime=J.struct_time((2019,5,29,15,14,15,0,-1,-1))
A=D.read_json_file(R)
A0=D.return_directory(g,'/sd/lightning_sounds',S)
x=D.return_directory(A6,'/sd/customers_owned_music',S)
AB=[]
AB.extend(A0)
AB.extend(x)
A1=[]
A1.extend(A0)
By=[BP,Ar,BQ]
A1.extend(By)
A1.extend(x)
Bz=D.return_directory(g,'/sd/time_stamp_defaults',z)
AO=A[As]
B_=D.read_json_file('/sd/mvc/main_menu.json')
Ag=B_[At]
C0=D.read_json_file('/sd/mvc/web_menu.json')
Ah=C0['web_menu']
C1=D.read_json_file('/sd/mvc/light_string_menu.json')
Ai=C1['light_string_menu']
C2=D.read_json_file('/sd/mvc/light_options.json')
A2=C2['light_options']
C3=D.read_json_file('/sd/mvc/volume_settings.json')
Aj=C3[AU]
C4=D.read_json_file('/sd/mvc/add_sounds_animate.json')
CU=C4[Au]
Y('sd card variables')
t=G
p=G
h=[]
y=[]
AC=[]
AP=[]
AQ=[]
M=0
B=B5.NeoPixel(f.GP10,M)
def C5():
	B=[]
	for C in h:
		for A in C:D=A;break
		for A in a(0,10):B.append(A+D)
	return B
def C6():
	B=[]
	for C in y:
		for A in C:D=A;break
		if H(C)==4:
			for A in a(0,4):B.append(A+D)
		if H(C)==1:
			for A in a(0,1):B.append(A+D)
	return B
def C7():
	global AP,AQ;AP=C5();AQ=C6()
	for C in h:
		for A in C:B[A]=50,50,50
		B.show();J.sleep(.3);B.fill((0,0,0));B.show()
	for D in y:
		for A in D:B[A]=50,50,50
		B.show();J.sleep(.3);B.fill((0,0,0));B.show()
	for E in AC:B[E[0]]=50,50,50;B.show();J.sleep(.3);B.fill((0,0,0));B.show()
def AH():
	I='bolt';global h,y,AC,M,B,M;h=[];y=[];AC=[];M=0;J=A[T].split(',')
	for K in J:
		F=K.split('-')
		if H(F)==2:
			E,C=F;C=r(C)
			if E=='bar':D=list(a(M,M+C));h.append(D);M+=C
			elif E==I and C<4:D=[M,C];AC.append(D);M+=1
			elif E==I and C==4:D=list(a(M,M+C));y.append(D);M+=C
	Q('Number of pixels total: ',M);B.deinit();Y('Deinit ledStrip');B=B5.NeoPixel(f.GP10,M);B.auto_write=G;B.brightness=1.;C7()
AH()
Y('Neopixels setup')
if AO:
	import socketpool as C8,mdns;Y(Av);import wifi as A3;Y(Av);from adafruit_httpserver import Server,Request,FileResponse as Ak,Response as O,POST as W;Y(Av);D.log_item('Connecting to WiFi');BC='jimmytrainsguest';BD=g
	try:BE=D.read_json_file('/sd/env.json');BC=BE['WIFI_SSID'];BD=BE['WIFI_PASSWORD'];Y('wifi env');Q('Using env ssid and password')
	except:Q('Using default ssid and password')
	try:
		A3.radio.connect(BC,BD);Y('wifi connect');Al=mdns.Server(A3.radio);Al.hostname=A[u];Al.advertise_service(service_type='_http',protocol='_tcp',port=80);C9=[hex(A)for A in A3.radio.mac_address];D.log_item('My MAC addr:'+j(C9));CA=j(A3.radio.ipv4_address);D.log_item('My IP address is'+CA);D.log_item('Connected to WiFi');CB=C8.SocketPool(A3.radio);L=Server(CB,'/static',debug=I);Y('wifi server')
		@L.route('/')
		def BF(request):Y('Home page.');return Ak(request,'index.html','/')
		@L.route('/mui.min.css')
		def BF(request):return Ak(request,'mui.min.css','/')
		@L.route('/mui.min.js')
		def BF(request):return Ak(request,'mui.min.js','/')
		@L.route('/animation',[W])
		def Z(request):
			E=request;global A,t,p;C=E.raw_request.decode(AL)
			if A6 in C:
				for B in x:
					if B in C:A[v]=B;Ap(A[v]);break
			else:
				for B in A1:
					if B in C:A[v]=B;Ap(A[v]);break
			D.write_json_file(R,A);return O(E,'Animation '+A[v]+' started.')
		@L.route('/defaults',[W])
		def Z(request):
			I='reset_default_colors';H='reset_to_defaults';B=request;global A;E=g;F=B.raw_request.decode(AL)
			if'reset_animation_timing_to_defaults'in F:
				for G in Bz:J=D.read_json_file('/sd/time_stamp_defaults/'+G+z);D.write_json_file(A7+G+z,J)
				C(b)
			elif H in F:E=H;CC();D.write_json_file(R,A);C(b);q.go_to_state(k)
			elif I in F:E=I;BH();D.write_json_file(R,A);C(b);K=D.json_stringify({AD:A[AD],U:A[U],V:A[V]});q.go_to_state(k);return O(B,K)
			return O(B,Aw+E)
		@L.route('/mode',[W])
		def Z(request):
			D=request;global A,t,p;E=g;B=D.raw_request.decode(AL)
			if'cont_mode_on'in B:t=I;C(BR)
			elif'cont_mode_off'in B:t=G;C(BS)
			elif'timestamp_mode_on'in B:p=I;C('/sd/mvc/timestamp_mode_on.wav');C(BT)
			elif'timestamp_mode_off'in B:p=G;C(BU)
			return O(D,Aw+E)
		@L.route('/speaker',[W])
		def Z(request):
			H='speaker_test';F=request;global A;B=g;E=F.raw_request.decode(AL)
			if H in E:B=H;C('/sd/mvc/left_speaker_right_speaker.wav')
			elif Ax in E:B=Ax;A[A8]=G;D.write_json_file(R,A);C(b)
			elif Ay in E:B=Ay;A[A8]=I;D.write_json_file(R,A);C(b)
			return O(F,Aw+B)
		@L.route('/lights',[W])
		def Z(request):
			C=request;A=C.raw_request.decode(AL)
			if'set_to_red'in A:B.fill((255,0,0));B.show()
			elif'set_to_green'in A:B.fill((0,255,0));B.show()
			elif'set_to_blue'in A:B.fill((0,0,255));B.show()
			elif'set_to_white'in A:B.fill((255,255,255));B.show()
			elif'set_to_0'in A:B.brightness=.0;B.show()
			elif'set_to_20'in A:B.brightness=.2;B.show()
			elif'set_to_40'in A:B.brightness=.4;B.show()
			elif'set_to_60'in A:B.brightness=.6;B.show()
			elif'set_to_80'in A:B.brightness=.8;B.show()
			elif'set_to_100'in A:B.brightness=1.;B.show()
			return O(C,'Utility: set lights')
		@L.route('/update-host-name',[W])
		def Z(request):B=request;global A;C=B.json();A[u]=C[AV];D.write_json_file(R,A);Al.hostname=A[u];BK();return O(B,A[u])
		@L.route('/get-host-name',[W])
		def Z(request):return O(request,A[u])
		@L.route('/update-volume',[W])
		def Z(request):B=request;global A;C=B.json();Ao(C[AE]);return O(B,A[o])
		@L.route('/get-volume',[W])
		def Z(request):return O(request,A[o])
		@L.route('/update-light-string',[W])
		def Z(request):
			G=' data: ';F='action: ';E=request;global A;B=E.json()
			if B[AE]=='save'or B[AE]=='clear'or B[AE]=='defaults':A[T]=B[AV];Q(F+B[AE]+G+A[T]);D.write_json_file(R,A);AH();C(b);return O(E,A[T])
			if A[T]==g:A[T]=B[AV]
			else:A[T]=A[T]+','+B[AV]
			Q(F+B[AE]+G+A[T]);D.write_json_file(R,A);AH();C(b);return O(E,A[T])
		@L.route('/get-light-string',[W])
		def Z(request):return O(request,A[T])
		@L.route('/get-customers-sound-tracks',[W])
		def Z(request):A=D.json_stringify(x);return O(request,A)
		@L.route('/get-built-in-sound-tracks',[W])
		def Z(request):A=[];A.extend(A0);B=D.json_stringify(A);return O(request,B)
		@L.route('/get-bar-colors',[W])
		def Z(request):B=D.json_stringify(A[AD]);return O(request,B)
		@L.route('/get-bolt-colors',[W])
		def Z(request):B=D.json_stringify(A[U]);return O(request,B)
		@L.route('/get-color-variation',[W])
		def Z(request):B=D.json_stringify(A[V]);return O(request,B)
		@L.route('/set-lights',[W])
		def Z(request):
			G=request;E='item';global A;C=G.json();J='set-lights'
			if C[E]==AD:
				A[AD]={c:C[c],d:C[d],e:C[e]};H=[];H.extend(AP)
				for F in H:B[F]=C[c],C[d],C[e];B.show()
			elif C[E]==U:
				A[U]={c:C[c],d:C[d],e:C[e]};I=[];I.extend(AQ)
				for F in I:B[F]=C[c],C[d],C[e];B.show()
			elif C[E]=='variationBolt':Q(C);A[V]={A9:C[c],AW:C[d],AX:C[e],AA:A[V][AA],AY:A[V][AY],AZ:A[V][AZ]}
			elif C[E]=='variationBar':A[V]={A9:A[V][A9],AW:A[V][AW],AX:A[V][AX],AA:C[c],AY:C[d],AZ:C[e]}
			D.write_json_file(R,A);return O(G,J)
	except BN as Am:AO=G;D.log_item(Am)
Y('web server')
import utilities as An
Y('utilities')
def X(seconds):
	C=seconds
	if A[A8]:B=Bl(Bk,C);F.voice[0].level=B
	else:
		try:B=r(A[o])/100
		except:B=.5
		if B<0 or B>1:B=.5
		F.voice[0].level=B;J.sleep(C)
def BG():global A;A[T]='bar-10,bolt-4,bar-10,bolt-4,bar-10,bolt-4'
def BH():global A;A[AD]={c:60,d:18,e:5};A[U]={c:60,d:18,e:5};A[V]={A9:20,AW:8,AX:5,AA:20,AY:8,AZ:5}
def CC():global A;A[A8]=I;A[u]=BV;A[v]='thunder birds rain';A[o]='20';A[Az]=I;BG();BH()
def Ao(action):
	E=action;B=r(A[o])
	if o in E:F=E.split(o);B=r(F[1])
	if E=='lower1':B-=1
	elif E=='raise1':B+=1
	elif E=='lower':
		if B<=10:B-=1
		else:B-=10
	elif E=='raise':
		if B<10:B+=1
		else:B+=10
	if B>100:B=100
	if B<1:B=1
	A[o]=j(B);A[A8]=G;D.write_json_file(R,A);C('/sd/mvc/volume.wav');AR(A[o],G)
def C(file_name):
	if F.voice[0].playing:
		F.voice[0].stop()
		while F.voice[0].playing:X(.02)
	A=l.WaveFile(m(file_name,n));F.voice[0].play(A,loop=G)
	while F.voice[0].playing:CD()
def CV():
	F.voice[0].stop()
	while F.voice[0].playing:0
def CD():
	X(.02);K.update()
	if K.fell:F.voice[0].stop()
def AR(str_to_speak,addLocal):
	for A in str_to_speak:
		try:
			if A==' ':A='space'
			if A=='-':A='dash'
			if A=='.':A='dot'
			C(s+A+S)
		except:Q('Invalid character in string to speak')
	if addLocal:C(BW);C(BX)
def AI():C('/sd/mvc/press_left_button_right_button.wav')
def AJ():C('/sd/mvc/web_menu.wav');AI()
def BI():C(BY)
def CE(song_number):C('/sd/mvc/song.wav');AR(song_number,G)
def BJ(play_intro):
	try:
		B=A[T].split(',')
		if play_intro:C('/sd/mvc/current_light_settings_are.wav')
		for(D,E)in AK(B):C('/sd/mvc/position.wav');C(s+j(D+1)+S);C('/sd/mvc/is.wav');C(s+E+S)
	except:C('/sd/mvc/no_lights_in_light_string.wav');return
def CF():
	C('/sd/mvc/no_user_soundtrack_found.wav')
	while I:
		K.update();N.update()
		if K.fell:break
		if N.fell:C('/sd/mvc/create_sound_track_files.wav');break
def BK():
	C('/sd/mvc/animator_available_on_network.wav');C('/sd/mvc/to_access_type.wav')
	if A[u]==BV:C('/sd/mvc/animator_dash_lightning.wav');C(BW);C(BX)
	else:AR(A[u],I)
	C('/sd/mvc/in_your_browser.wav')
A4=g
def Ap(file_name):
	G='Sound file: ';F='Random sound option: ';C=file_name;global A,A4;Q('Filename: '+C);B=C
	try:
		if C==Ar:
			D=H(A0)-1;B=A0[E.randint(0,D)]
			while A4==B and H(A0)>1:B=A0[E.randint(0,D)]
			A4=B;Q(F+C);Q(G+B)
		elif C==BQ:
			D=H(x)-1;B=x[E.randint(0,D)]
			while A4==B and H(x)>1:B=x[E.randint(0,D)]
			A4=B;Q(F+C);Q(G+B)
		elif C==BP:
			D=H(AB)-1;B=AB[E.randint(0,D)]
			while A4==B and H(AB)>1:B=AB[E.randint(0,D)]
			A4=B;Q(F+C);Q(G+B)
		if p:CG(B)
		elif A6 in B:AS(B)
		elif B=='alien lightshow':AS(B)
		elif B=='inspiring cinematic ambient lightshow':AS(B)
		elif B==BZ:AS(B)
		else:CH(B)
	except:CF();A[v]=Ar;return
	Y('Animation complete.')
def AS(file_name):
	M=file_name;global p;T=1;U=3
	if M==BZ:T=4;U=4
	W=A6 in M
	if W:
		M=M.replace(A6,g)
		try:Y=D.read_json_file(Aa+M+z)
		except:
			C('/sd/mvc/no_timestamp_file_found.wav')
			while I:
				K.update();N.update()
				if K.fell:p=G;return
				if N.fell:p=I;C(BT);return
	else:Y=D.read_json_file(A7+M+z)
	P=Y[AM];b=H(P);L=0
	if W:Z=l.WaveFile(m(Aa+M+S,n))
	else:Z=l.WaveFile(m(A7+M+S,n))
	F.voice[0].play(Z,loop=G);c=J.monotonic();O=0;BM(.01)
	while I:
		a=0;V=J.monotonic()-c
		if L<H(P)-2:R=P[L+1]-P[L]-.25
		else:R=.25
		if R<0:R=0
		if V>P[L]-.25:
			Q(Ba+j(V)+Bb+j(P[L])+Bc+j(V-P[L]));L+=1;O=E.randint(T,U)
			while O==a:O=E.randint(T,U)
			if O==1:CI(.005,R)
			elif O==2:BM(.01);X(R)
			elif O==3:CJ(R)
			elif O==4:CL(R)
			a=O
		if b==L:L=0
		K.update()
		if K.fell and A[Az]:F.voice[0].stop()
		if not F.voice[0].playing:B.fill((0,0,0));B.show();break
		X(.001)
def CG(file_name):
	A=file_name;Q('Time stamp mode:');global p;H=A6 in A;E=D.read_json_file('/sd/time_stamp_defaults/timestamp mode.json');E[AM]=[];A=A.replace(A6,g)
	if H:K=l.WaveFile(m(Aa+A+S,n))
	else:K=l.WaveFile(m(A7+A+S,n))
	F.voice[0].play(K,loop=G);M=J.monotonic();X(.1)
	while I:
		L=J.monotonic()-M;N.update()
		if N.fell:E[AM].append(L);Q(L)
		if not F.voice[0].playing:
			B.fill((0,0,0));B.show();E[AM].append(5000)
			if H:D.write_json_file(Aa+A+z,E)
			else:D.write_json_file(A7+A+z,E)
			break
	p=G;C('/sd/mvc/timestamp_saved.wav');C(BU);C(Bd)
def CH(file_name):
	M=file_name;O=D.read_json_file(A7+M+z);N=O[AM];P=H(N);B=0;R=l.WaveFile(m(A7+M+S,n));F.voice[0].play(R,loop=G);T=J.monotonic()
	while I:
		X(.1);C=J.monotonic()-T;L=N[B]-E.uniform(.5,1)
		if C>L:Q(Ba+j(C)+Bb+j(L)+Bc+j(C-L));B+=1;CM()
		if P==B:B=0
		K.update()
		if K.fell and A[Az]:F.voice[0].stop()
		if not F.voice[0].playing:break
def CI(speed,duration):
	G=duration;F=speed;H=J.monotonic()
	for C in a(0,255,1):
		for A in a(M):D=A*256//M+C;B[A]=B6(D&255)
		B.show();X(F);E=J.monotonic()-H
		if E>G:return
	for C in reversed(a(0,255,1)):
		for A in a(M):D=A*256//M+C;B[A]=B6(D&255)
		B.show();X(F);E=J.monotonic()-H
		if E>G:return
def CJ(duration):
	L=J.monotonic();B.brightness=1.;H=[];H.extend(AP);K=[];K.extend(AQ);A=E.randint(0,255);C=E.randint(0,255);D=E.randint(0,255)
	for F in K:B[F]=A,C,D
	A=E.randint(0,255);C=E.randint(0,255);D=E.randint(0,255)
	while I:
		for F in H:G=E.randint(0,110);M=Aq(A-G,0,255);N=Aq(C-G,0,255);O=Aq(D-G,0,255);B[F]=M,N,O;B.show()
		X(E.uniform(.05,.1));P=J.monotonic()-L
		if P>duration:return
def CK(arr):
	A=arr;B=H(A)//2
	for C in a(B):D=B-1-C;E=B+C;yield(A[D],A[E])
def AT():
	for A in h:
		for C in A:B[C]=0,0,0
def BL():
	A=E.randint(0,2)
	if A==0:B=255;C=255;D=255
	if A==1:B=255;C=0;D=0
	if A==2:B=0;C=0;D=255
	return B,C,D
def CL(duration):
	L=duration;M=J.monotonic();B.brightness=1.;C=[]
	for(D,U)in AK(h):
		if D==E.randint(0,H(h)-1):C.append(D)
	if H(C)==0:D==E.randint(0,H(h)-1);C.append(D)
	for N in y:
		F,I,K=BL()
		for O in N:B[O]=F,I,K
	P=G
	while not P:
		for Q in C:
			F,I,K=BL();R=CK(h[Q])
			for(S,T)in R:
				AT();B[S]=F,I,K;B[T]=F,I,K;B.show();X(.1);A=J.monotonic()-M
				if A>L:AT();B.show();break
			B.show();A=J.monotonic()-M
			if A>L:AT();B.show();break
		A=J.monotonic()-M
		if A>L:AT();B.show();return
def BM(duration):
	G=J.monotonic();B.brightness=1.
	while I:
		for H in a(0,M):
			K=E.randint(128,255);L=E.randint(128,255);N=E.randint(128,255);A=E.randint(0,2)
			if A==0:C=K;D=0;F=0
			elif A==1:C=0;D=L;F=0
			elif A==2:C=0;D=0;F=N
			B[H]=C,D,F;B.show()
		X(E.uniform(.2,.3));O=J.monotonic()-G
		if O>duration:return
def i(item,colorKey,addSub):return A[item][colorKey]+addSub
def CM():
	N=[];O=E.randint(-1,H(y)-1)
	if O!=-1:
		for(G,I)in AK(y):
			if G==O:N.extend(I)
	T=[]
	for(G,I)in AK(h):
		if G==E.randint(0,H(h)-1):T.extend(I)
	D=[];W=E.randint(-1,H(AC)-1)
	if W!=-1:
		for(G,I)in AK(AC):
			if G==W:D.extend(I)
	if H(D)>0 and H(N)>0:
		O=E.randint(0,1)
		if O==0:N=[]
		else:D=[]
	K=r(A[V][A9]);L=r(A[V][A9]);M=r(A[V][A9]);X=E.randint(i(U,c,-K),i(U,c,K));Y=E.randint(i(U,d,-L),i(U,d,L));Z=E.randint(i(U,e,-M),i(U,e,M));K=r(A[V][AA]);L=r(A[V][AA]);M=r(A[V][AA]);b=E.randint(i(U,c,-K),i(U,c,K));f=E.randint(i(U,d,-L),i(U,d,L));g=E.randint(i(U,e,-M),i(U,e,M));j=E.randint(5,10);B.brightness=E.randint(255,255)/255
	if H(D)>0:
		if D[1]==1:P=1;Q=0;R=0
		if D[1]==2:P=E.randint(0,1);Q=0;R=E.randint(0,1)
		if D[1]==3:P=E.randint(0,1);Q=E.randint(0,1);R=E.randint(0,1)
	for k in a(0,j):
		C=E.randint(0,100)
		if C<0:C=0
		for l in a(4):
			if H(D)>0:B[D[0]]=(155+C)*Q,(155+C)*P,(155+C)*R
			for S in N:B[S]=X+C,Y+C,Z+C
			for S in T:B[S]=b+C,f+C,g+C
			B.show();F=E.randint(0,75);F=F/1000;J.sleep(F);B.fill((0,0,0));B.show()
		F=E.randint(1,50);F=F/1000;J.sleep(F);B.fill((0,0,0));B.show()
def Aq(my_color,lower,upper):
	C=upper;B=lower;A=my_color
	if A<B:A=B
	if A>C:A=C
	return A
class CN:
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
	def reset(A):B8()
class P:
	def __init__(A):0
	@A5
	def name(self):return g
	def enter(A,machine):0
	def exit(A,machine):0
	def update(A,machine):0
class CO(P):
	def __init__(A):0
	@A5
	def name(self):return k
	def enter(A,machine):C(Bd);D.log_item('Entered base state');P.enter(A,machine)
	def exit(A,machine):P.exit(A,machine)
	def update(D,machine):
		global t;B=An.switch_state(K,N,X,3.)
		if B==Be:
			if t:t=G;C(BS)
			else:t=I;C(BR)
		elif B==A_ or t:Ap(A[v])
		elif B==B0:machine.go_to_state(At)
class CP(P):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@A5
	def name(self):return At
	def enter(A,machine):C('/sd/mvc/main_menu.wav');AI();P.enter(A,machine)
	def exit(A,machine):P.exit(A,machine)
	def update(A,machine):
		B=machine;K.update();N.update()
		if K.fell:
			C(s+Ag[A.menuIndex]+S);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
			if A.menuIndex>H(Ag)-1:A.menuIndex=0
		if N.fell:
			D=Ag[A.selectedMenuIndex]
			if D==B1:B.go_to_state(B1)
			elif D==Au:B.go_to_state(Au)
			elif D==B2:B.go_to_state(B2)
			elif D==B3:B.go_to_state(B3)
			elif D==AU:B.go_to_state(AU)
			else:C(b);B.go_to_state(k)
class CQ(P):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@A5
	def name(self):return B1
	def enter(A,machine):D.log_item('Choose sounds menu');C('/sd/mvc/sound_selection_menu.wav');AI();P.enter(A,machine)
	def exit(A,machine):P.exit(A,machine)
	def update(B,machine):
		K.update();N.update()
		if K.fell:
			if F.voice[0].playing:
				F.voice[0].stop()
				while F.voice[0].playing:0
			else:
				try:C=l.WaveFile(m('/sd/lightning_options_voice_commands/option_'+A1[B.optionIndex]+S,n));F.voice[0].play(C,loop=G)
				except:CE(j(B.optionIndex+1))
				B.currentOption=B.optionIndex;B.optionIndex+=1
				if B.optionIndex>H(A1)-1:B.optionIndex=0
				while F.voice[0].playing:0
		if N.fell:
			if F.voice[0].playing:
				F.voice[0].stop()
				while F.voice[0].playing:0
			else:
				A[v]=A1[B.currentOption];D.write_json_file(R,A);C=l.WaveFile(m(BY,n));F.voice[0].play(C,loop=G)
				while F.voice[0].playing:0
			machine.go_to_state(k)
class CR(P):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@A5
	def name(self):return AU
	def enter(A,machine):D.log_item(Bf);C('/sd/mvc/volume_settings_menu.wav');AI();P.enter(A,machine)
	def exit(A,machine):P.exit(A,machine)
	def update(B,machine):
		E=machine;K.update();N.update()
		if K.fell:
			C(s+Aj[B.menuIndex]+S);B.selectedMenuIndex=B.menuIndex;B.menuIndex+=1
			if B.menuIndex>H(Aj)-1:B.menuIndex=0
		if N.fell:
			F=Aj[B.selectedMenuIndex]
			if F=='volume_level_adjustment':
				C('/sd/mvc/volume_adjustment_menu.wav');L=G
				while not L:
					J=An.switch_state(K,N,X,3.)
					if J==A_:Ao('lower')
					elif J==B0:Ao('raise')
					elif J==Bg:D.write_json_file(R,A);C(b);L=I;E.go_to_state(k)
					X(.1)
			elif F==Ax:
				A[A8]=G
				if A[o]==0:A[o]=10
				D.write_json_file(R,A);C(b);E.go_to_state(k)
			elif F==Ay:A[A8]=I;D.write_json_file(R,A);C(b);E.go_to_state(k)
class CS(P):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@A5
	def name(self):return B3
	def enter(A,machine):D.log_item(Bf);AJ();P.enter(A,machine)
	def exit(A,machine):P.exit(A,machine)
	def update(B,machine):
		K.update();N.update()
		if K.fell:
			C(s+Ah[B.menuIndex]+S);B.selectedMenuIndex=B.menuIndex;B.menuIndex+=1
			if B.menuIndex>H(Ah)-1:B.menuIndex=0
		if N.fell:
			E=Ah[B.selectedMenuIndex]
			if E=='web_on':A[As]=I;BI();AJ()
			elif E=='web_off':A[As]=G;BI();AJ()
			elif E=='hear_url':AR(A[u],I);AJ()
			elif E=='hear_instr_web':C('/sd/mvc/web_instruct.wav');AJ()
			else:D.write_json_file(R,A);C(b);machine.go_to_state(k)
class CT(P):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@A5
	def name(self):return B2
	def enter(A,machine):D.log_item('Light string menu');C('/sd/mvc/light_string_setup_menu.wav');AI();P.enter(A,machine)
	def exit(A,machine):P.exit(A,machine)
	def update(B,machine):
		J=machine;K.update();N.update()
		if K.fell:
			C(s+Ai[B.menuIndex]+S);B.selectedMenuIndex=B.menuIndex;B.menuIndex+=1
			if B.menuIndex>H(Ai)-1:B.menuIndex=0
		if N.fell:
			E=Ai[B.selectedMenuIndex]
			if E=='hear_light_setup_instructions':C('/sd/mvc/string_instructions.wav')
			elif E=='reset_lights_defaults':BG();C('/sd/mvc/lights_reset_to.wav');BJ(G)
			elif E=='hear_current_light_settings':BJ(I)
			elif E=='clear_light_string':A[T]=g;C('/sd/mvc/lights_cleared.wav')
			elif E=='add_lights':
				C('/sd/mvc/add_light_menu.wav');L=I
				while L:
					F=An.switch_state(K,N,X,3.)
					if F==A_:
						B.menuIndex-=1
						if B.menuIndex<0:B.menuIndex=H(A2)-1
						B.selectedMenuIndex=B.menuIndex;C(s+A2[B.menuIndex]+S)
					elif F==B0:
						B.menuIndex+=1
						if B.menuIndex>H(A2)-1:B.menuIndex=0
						B.selectedMenuIndex=B.menuIndex;C(s+A2[B.menuIndex]+S)
					elif F==Bg:
						if A[T]==g:A[T]=A2[B.selectedMenuIndex]
						else:A[T]=A[T]+','+A2[B.selectedMenuIndex]
						C(s+A2[B.selectedMenuIndex]+S);C('/sd/mvc/added.wav')
					elif F==Be:D.write_json_file(R,A);AH();C(b);L=G;J.go_to_state(k)
					X(.1)
			else:D.write_json_file(R,A);C(b);AH();J.go_to_state(k)
q=CN()
q.add_state(CO())
q.add_state(CP())
q.add_state(CQ())
q.add_state(CR())
q.add_state(CS())
q.add_state(CT())
AF.value=I
if AO:
	D.log_item('starting server...')
	try:L.start(j(A3.radio.ipv4_address));D.log_item('Listening on http://%s:80'%A3.radio.ipv4_address);BK()
	except OSError:J.sleep(5);D.log_item('restarting...');B8()
q.go_to_state(k)
D.log_item('animator has started...')
Y('animations started.')
while I:
	q.update();X(.02)
	if AO:
		try:L.poll()
		except BN as Am:D.log_item(Am);continue
