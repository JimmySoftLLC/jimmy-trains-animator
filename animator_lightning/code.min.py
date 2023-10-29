Ba='right_held'
BZ='Set Web Options'
BY='left_held'
BX='/sd/mvc/animations_are_now_active.wav'
BW=' Dif: '
BV=' Timestamp: '
BU='Time elapsed: '
BT='fireworks'
BS='/sd/mvc/create_sound_track_files.wav'
BR='/sd/mvc/option_selected.wav'
BQ='/sd/mvc/local.wav'
BP='/sd/mvc/dot.wav'
BO='animator-lightning'
BN='timestamp_mode_off'
BM='/sd/mvc/timestamp_mode_on.wav'
BL='timestamp_mode_on'
BK='/sd/mvc/continuous_mode_deactivated.wav'
BJ='/sd/mvc/continuous_mode_activated.wav'
BI='wav/no_card.wav'
BH=Exception
Ay='web_options'
Ax='light_string_setup_menu'
Aw='choose_sounds'
Av='right'
Au='left'
At='can_cancel'
As='volume_pot_on'
Ar='volume_pot_off'
Aq='/sd/mvc/timestamp_mode_off.wav'
Ap='/sd/mvc/timestamp_instructions.wav'
Ao='Utility: '
An='config wifi imports'
Am='main_menu'
Al='serve_webpage'
Ak='random my'
Aj='random built in'
Ai='random all'
AQ='/sd/customers_owned_music/'
AP='text'
AO='add_sounds_animate'
AN='volume_settings'
AM=enumerate
AE='flashTime'
AD='utf8'
A8='action'
A5='volume_pot'
A4='/sd/lightning_sounds/'
A3='customers_owned_music_'
z='option_selected'
y='.json'
x=property
t='HOST_NAME'
r='/sd/mvc/'
q='volume'
p='rb'
o=open
l='b'
k='g'
j='r'
i='bolts'
h='bars'
g=''
f=str
c=range
Z='base_state'
Y='/sd/mvc/all_changes_complete.wav'
T='light_string'
S='/sd/config_lightning.json'
R=print
P='.wav'
N=len
H=True
G=False
import gc,files as D
def V(collection_point):gc.collect();A=gc.mem_free();D.log_item('Point '+collection_point+' Available memory: {} bytes'.format(A))
V('Imports gc, files')
import time as J,audiocore as m,audiomixer as Bb,audiobusio as Bc,sdcardio as Az,storage as AF,busio,digitalio as u,board as a,neopixel as A_,random as F,rtc,microcontroller as AR
from analogio import AnalogIn as Bd
from adafruit_debouncer import Debouncer as B0
def B1():AR.on_next_reset(AR.RunMode.NORMAL);AR.reset()
V('imports')
Be=Bd(a.A0)
def Bf(pin,wait_for):
	B=wait_for/10;A=0
	for C in c(10):J.sleep(B);A+=1;A=A/10
	return pin.value/65536
A9=u.DigitalInOut(a.GP28)
A9.direction=u.Direction.OUTPUT
A9.value=G
Bg=a.GP6
Bh=a.GP7
AS=u.DigitalInOut(Bg)
AS.direction=u.Direction.INPUT
AS.pull=u.Pull.UP
I=B0(AS)
AT=u.DigitalInOut(Bh)
AT.direction=u.Direction.INPUT
AT.pull=u.Pull.UP
K=B0(AT)
Bi=a.GP18
Bj=a.GP19
Bk=a.GP20
Bl=Bc.I2SOut(bit_clock=Bi,word_select=Bj,data=Bk)
A9.value=H
Bm=a.GP2
Bn=a.GP3
Bo=a.GP4
B2=a.GP5
B3=busio.SPI(Bm,Bn,Bo)
Bp=2
E=Bb.Mixer(voice_count=Bp,sample_rate=22050,channel_count=2,bits_per_sample=16,samples_signed=H,buffer_size=4096)
Bl.play(E)
B4=.2
E.voice[0].level=B4
E.voice[1].level=B4
try:AU=Az.SDCard(B3,B2);AV=AF.VfsFat(AU);AF.mount(AV,'/sd')
except:
	AA=m.WaveFile(o(BI,p));E.voice[0].play(AA,loop=G)
	while E.voice[0].playing:0
	B5=G
	while not B5:
		I.update()
		if I.fell:
			try:
				AU=Az.SDCard(B3,B2);AV=AF.VfsFat(AU);AF.mount(AV,'/sd');B5=H;AA=m.WaveFile(o('/sd/mvc/micro_sd_card_success.wav',p));E.voice[0].play(AA,loop=G)
				while E.voice[0].playing:0
			except:
				AA=m.WaveFile(o(BI,p));E.voice[0].play(AA,loop=G)
				while E.voice[0].playing:0
A9.value=G
Bq=rtc.RTC()
Bq.datetime=J.struct_time((2019,5,29,15,14,15,0,-1,-1))
A=D.read_json_file(S)
A0=D.return_directory(g,'/sd/lightning_sounds',P)
Br=[Ai,Aj,Ak]
A0.extend(Br)
A6=D.return_directory(A3,'/sd/customers_owned_music',P)
v=[]
v.extend(A0)
v.extend(A6)
Bs=D.return_directory(g,'/sd/time_stamp_defaults',y)
AG=A[Al]
Bt=D.read_json_file('/sd/mvc/main_menu.json')
AW=Bt[Am]
Bu=D.read_json_file('/sd/mvc/web_menu.json')
AX=Bu['web_menu']
Bv=D.read_json_file('/sd/mvc/light_string_menu.json')
AY=Bv['light_string_menu']
Bw=D.read_json_file('/sd/mvc/light_options.json')
A1=Bw['light_options']
Bx=D.read_json_file('/sd/mvc/volume_settings.json')
AZ=Bx[AN]
By=D.read_json_file('/sd/mvc/add_sounds_animate.json')
Aa=By[AO]
V('sd card variables')
s=G
b=G
from rainbowio import colorwheel as B6
d=[]
w=[]
AH=[]
AI=[]
O=0
C=A_.NeoPixel(a.GP10,O)
def Bz():
	B=[]
	for C in d:
		for A in C:D=A;break
		for A in c(0,10):B.append(A+D)
	return B
def B_():
	B=[]
	for C in w:
		for A in C:D=A;break
		for A in c(0,4):B.append(A+D)
	return B
def C0():
	global AH,AI;AH=Bz();AI=B_()
	for B in d:
		for A in B:C[A]=50,50,50
		C.show();J.sleep(.3);C.fill((0,0,0));C.show()
	for D in w:
		for A in D:C[A]=50,50,50
		C.show();J.sleep(.3);C.fill((0,0,0));C.show()
def AB():
	global d,w,O,C,O;d=[];w=[];O=0;F=A[T].split(',')
	for H in F:
		D=H.split('-')
		if N(D)==2:
			E,B=D;B=int(B)
			if E=='bar':I=list(c(O,O+B));d.append(I);O+=B
			elif E=='bolt':J=list(c(O,O+B));w.append(J);O+=B
	R('Number of pixels total: ',O);C.deinit();V('Deinit ledStrip');C=A_.NeoPixel(a.GP10,O);C.auto_write=G;C.brightness=1.;C0()
AB()
V('Neopixels setup')
if AG:
	import socketpool as C1,mdns;V(An);import wifi as A2;V(An);from adafruit_httpserver import Server,Request,FileResponse as Ab,Response as Q,POST as W;V(An);D.log_item('Connecting to WiFi');B7='jimmytrainsguest';B8=g
	try:B9=D.read_json_file('/sd/env.json');B7=B9['WIFI_SSID'];B8=B9['WIFI_PASSWORD'];V('wifi env');R('Using env ssid and password')
	except:R('Using default ssid and password')
	try:
		A2.radio.connect(B7,B8);V('wifi connect');Ac=mdns.Server(A2.radio);Ac.hostname=A[t];Ac.advertise_service(service_type='_http',protocol='_tcp',port=80);C2=[hex(A)for A in A2.radio.mac_address];D.log_item('My MAC addr:'+f(C2));C3=f(A2.radio.ipv4_address);D.log_item('My IP address is'+C3);D.log_item('Connected to WiFi');C4=C1.SocketPool(A2.radio);L=Server(C4,'/static',debug=H);V('wifi server')
		@L.route('/')
		def BA(request):V('Home page.');return Ab(request,'index.html','/')
		@L.route('/mui.min.css')
		def BA(request):return Ab(request,'mui.min.css','/')
		@L.route('/mui.min.js')
		def BA(request):return Ab(request,'mui.min.js','/')
		@L.route('/animation',[W])
		def X(request):
			E=request;global A,s,b;C=E.raw_request.decode(AD)
			if A3 in C:
				for B in A6:
					if B in C:A[z]=B;Ag(A[z]);break
			else:
				for B in A0:
					if B in C:A[z]=B;Ag(A[z]);break
			D.write_json_file(S,A);return Q(E,'Animation '+A[z]+' started.')
		@L.route('/defaults',[W])
		def X(request):
			I='reset_default_colors';H='reset_to_defaults';C=request;global A;E=g;F=C.raw_request.decode(AD)
			if'reset_animation_timing_to_defaults'in F:
				for G in Bs:J=D.read_json_file('/sd/time_stamp_defaults/'+G+y);D.write_json_file(A4+G+y,J)
				B(Y)
			elif H in F:E=H;C5();D.write_json_file(S,A);B(Y);n.go_to_state(Z)
			elif I in F:E=I;BC();D.write_json_file(S,A);B(Y);K=D.json_stringify({h:A[h],i:A[i]});n.go_to_state(Z);return Q(C,K)
			return Q(C,Ao+E)
		@L.route('/mode',[W])
		def X(request):
			D=request;global A,s,b;E=g;C=D.raw_request.decode(AD)
			if'cont_mode_on'in C:s=H;B(BJ)
			elif'cont_mode_off'in C:s=G;B(BK)
			elif BL in C:b=H;B(BM);B(Ap)
			elif BN in C:b=G;B(Aq)
			return Q(D,Ao+E)
		@L.route('/speaker',[W])
		def X(request):
			I='speaker_test';F=request;global A;C=g;E=F.raw_request.decode(AD)
			if I in E:C=I;B('/sd/mvc/left_speaker_right_speaker.wav')
			elif Ar in E:C=Ar;A[A5]=G;D.write_json_file(S,A);B(Y)
			elif As in E:C=As;A[A5]=H;D.write_json_file(S,A);B(Y)
			return Q(F,Ao+C)
		@L.route('/lights',[W])
		def X(request):
			B=request;A=B.raw_request.decode(AD)
			if'set_to_red'in A:C.fill((255,0,0));C.show()
			elif'set_to_green'in A:C.fill((0,255,0));C.show()
			elif'set_to_blue'in A:C.fill((0,0,255));C.show()
			elif'set_to_white'in A:C.fill((255,255,255));C.show()
			elif'set_to_0'in A:C.brightness=.0;C.show()
			elif'set_to_20'in A:C.brightness=.2;C.show()
			elif'set_to_40'in A:C.brightness=.4;C.show()
			elif'set_to_60'in A:C.brightness=.6;C.show()
			elif'set_to_80'in A:C.brightness=.8;C.show()
			elif'set_to_100'in A:C.brightness=1.;C.show()
			return Q(B,'Utility: set lights')
		@L.route('/update-host-name',[W])
		def X(request):B=request;global A;C=B.json();A[t]=C[AP];D.write_json_file(S,A);Ac.hostname=A[t];BF();return Q(B,A[t])
		@L.route('/get-host-name',[W])
		def X(request):return Q(request,A[t])
		@L.route('/update-volume',[W])
		def X(request):B=request;global A;C=B.json();Af(C[A8]);return Q(B,A[q])
		@L.route('/get-volume',[W])
		def X(request):return Q(request,A[q])
		@L.route('/update-light-string',[W])
		def X(request):
			G=' data: ';F='action: ';E=request;global A;C=E.json()
			if C[A8]=='save'or C[A8]=='clear'or C[A8]=='defaults':A[T]=C[AP];R(F+C[A8]+G+A[T]);D.write_json_file(S,A);AB();B(Y);return Q(E,A[T])
			if A[T]==g:A[T]=C[AP]
			else:A[T]=A[T]+','+C[AP]
			R(F+C[A8]+G+A[T]);D.write_json_file(S,A);AB();B(Y);return Q(E,A[T])
		@L.route('/get-light-string',[W])
		def X(request):return Q(request,A[T])
		@L.route('/get-customers-sound-tracks',[W])
		def X(request):A=D.json_stringify(A6);return Q(request,A)
		@L.route('/get-built-in-sound-tracks',[W])
		def X(request):A=[];A.extend(A0);A.remove(Ai);A.remove(Aj);A.remove(Ak);B=D.json_stringify(A);return Q(request,B)
		@L.route('/get-bar-colors',[W])
		def X(request):B=D.json_stringify(A[h]);return Q(request,B)
		@L.route('/get-bolt-colors',[W])
		def X(request):B=D.json_stringify(A[i]);return Q(request,B)
		@L.route('/set-lights',[W])
		def X(request):
			I='item';F=request;global A;B=F.json();J='set-lights'
			if B[I]==h:
				A[h]={j:B[j],k:B[k],l:B[l]};G=[];G.extend(AH)
				for E in G:C[E]=B[j],B[k],B[l];C.show()
			elif B[I]==i:
				A[i]={j:B[j],k:B[k],l:B[l]};H=[];H.extend(AI)
				for E in H:C[E]=B[j],B[k],B[l];C.show()
			R(A);D.write_json_file(S,A);return Q(F,J)
	except BH as Ad:AG=G;D.log_item(Ad)
V('web server')
import utilities as Ae
V('utilities')
def U(seconds):
	C=seconds
	if A[A5]:B=Bf(Be,C);E.voice[0].level=B
	else:
		try:B=int(A[q])/100
		except:B=.5
		if B<0 or B>1:B=.5
		E.voice[0].level=B;E.voice[1].level=B;J.sleep(C)
def BB():global A;A[T]='bar-10,bolt-4,bar-10,bolt-4,bar-10,bolt-4'
def BC():global A;A[h]={j:60,k:18,l:5};A[i]={j:60,k:18,l:5}
def C5():global A;A[A5]=H;A[t]=BO;A[z]='thunder birds rain';A[q]='20';A[At]=H;BB();BC()
def Af(action):
	E=action;C=int(A[q])
	if q in E:F=E.split(q);C=int(F[1])
	if E=='lower1':C-=1
	elif E=='raise1':C+=1
	elif E=='lower':
		if C<=10:C-=1
		else:C-=10
	elif E=='raise':
		if C<10:C+=1
		else:C+=10
	if C>100:C=100
	if C<1:C=1
	A[q]=f(C);A[A5]=G;D.write_json_file(S,A);B('/sd/mvc/volume.wav');AJ(A[q],G)
def B(file_name):
	if E.voice[0].playing:
		E.voice[0].stop()
		while E.voice[0].playing:U(.02)
	A=m.WaveFile(o(file_name,p));E.voice[0].play(A,loop=G)
	while E.voice[0].playing:C6()
def CO():
	E.voice[0].stop()
	while E.voice[0].playing:0
def C6():
	U(.02);I.update()
	if I.fell:E.voice[0].stop()
def AJ(str_to_speak,addLocal):
	for A in str_to_speak:
		if A==' ':A='space'
		if A=='-':A='dash'
		if A=='.':A='dot'
		B(r+A+P)
	if addLocal:B(BP);B(BQ)
def A7():B('/sd/mvc/press_left_button_right_button.wav')
def AC():B('/sd/mvc/web_menu.wav');A7()
def BD():B(BR)
def C7(song_number):B('/sd/mvc/song.wav');AJ(song_number,G)
def BE(play_intro):
	if play_intro:B('/sd/mvc/current_light_settings_are.wav')
	C=A[T].split(',')
	for(D,E)in AM(C):B('/sd/mvc/position.wav');B(r+f(D+1)+P);B('/sd/mvc/is.wav');B(r+E+P)
def CP():
	B('/sd/mvc/no_user_soundtrack_found.wav')
	while H:
		I.update();K.update()
		if I.fell:break
		if K.fell:B(BS);break
def BF():
	B('/sd/mvc/animator_available_on_network.wav');B('/sd/mvc/to_access_type.wav')
	if A[t]==BO:B('/sd/mvc/animator_dash_lightning.wav');B(BP);B(BQ)
	else:AJ(A[t],H)
	B('/sd/mvc/in_your_browser.wav')
def Ag(file_name):
	G='Sound file: ';E='Random sound file: ';C=file_name;R(C);A=C
	if C==Aj:D=N(A0)-4;B=F.randint(0,D);A=A0[B];R(E+A0[B]);R(G+A)
	elif C==Ak:D=N(A6)-1;B=F.randint(0,D);A=A6[B];R(E+A6[B]);R(G+A)
	elif C==Ai:D=N(v)-4;B=F.randint(0,D);A=v[B];R(E+v[B]);R(G+A)
	if b:C8(A)
	elif A3 in A:AK(A)
	elif A=='alien lightshow':AK(A)
	elif A=='inspiring cinematic ambient lightshow':AK(A)
	elif A==BT:AK(A)
	else:C9(A)
	V('Animation complete.')
def AK(file_name):
	M=file_name;global b;T=1;V=3
	if M==BT:T=4;V=4
	X=A3 in M
	if X:
		M=M.replace(A3,g)
		try:Y=D.read_json_file(AQ+M+y)
		except:
			B('/sd/mvc/no_timestamp_file_found.wav')
			while H:
				I.update();K.update()
				if I.fell:b=G;return
				if K.fell:b=H;B(Ap);return
	else:Y=D.read_json_file(A4+M+y)
	Q=Y[AE];c=N(Q);L=0
	if X:Z=m.WaveFile(o(AQ+M+P,p))
	else:Z=m.WaveFile(o(A4+M+P,p))
	E.voice[0].play(Z,loop=G);d=J.monotonic();O=0
	while H:
		a=0;W=J.monotonic()-d
		if L<N(Q)-2:S=Q[L+1]-Q[L]-.25
		else:S=.25
		if S<0:S=0
		if W>Q[L]-.25:
			R(BU+f(W)+BV+f(Q[L])+BW+f(W-Q[L]));L+=1;O=F.randint(T,V)
			while O==a:O=F.randint(T,V)
			if O==1:CA(.005,S)
			elif O==2:CE(.01);U(S)
			elif O==3:CB(S)
			elif O==4:CD(S)
			a=O
		if c==L:L=0
		I.update()
		if I.fell and A[At]:E.voice[0].stop()
		if not E.voice[0].playing:C.fill((0,0,0));C.show();break
		U(.001)
def C8(file_name):
	A=file_name;R('Time stamp mode:');global b;I=A3 in A;F=D.read_json_file('/sd/time_stamp_defaults/timestamp mode.json');F[AE]=[];A=A.replace(A3,g)
	if I:L=m.WaveFile(o(AQ+A+P,p))
	else:L=m.WaveFile(o(A4+A+P,p))
	E.voice[0].play(L,loop=G);N=J.monotonic();U(.1)
	while H:
		M=J.monotonic()-N;K.update()
		if K.fell:F[AE].append(M);R(M)
		if not E.voice[0].playing:
			C.fill((0,0,0));C.show();F[AE].append(5000)
			if I:D.write_json_file(AQ+A+y,F)
			else:D.write_json_file(A4+A+y,F)
			break
	b=G;B('/sd/mvc/timestamp_saved.wav');B(Aq);B(BX)
def C9(file_name):
	L=file_name;O=D.read_json_file(A4+L+y);M=O[AE];Q=N(M);B=0;S=m.WaveFile(o(A4+L+P,p));E.voice[0].play(S,loop=G);T=J.monotonic()
	while H:
		U(.1);C=J.monotonic()-T;K=M[B]-F.uniform(.5,1)
		if C>K:R(BU+f(C)+BV+f(K)+BW+f(C-K));B+=1;CF()
		if Q==B:B=0
		I.update()
		if I.fell and A[At]:E.voice[0].stop()
		if not E.voice[0].playing:break
def CA(speed,duration):
	G=duration;F=speed;H=J.monotonic()
	for B in c(0,255,1):
		for A in c(O):D=A*256//O+B;C[A]=B6(D&255)
		C.show();U(F);E=J.monotonic()-H
		if E>G:return
	for B in reversed(c(0,255,1)):
		for A in c(O):D=A*256//O+B;C[A]=B6(D&255)
		C.show();U(F);E=J.monotonic()-H
		if E>G:return
def CB(duration):
	L=J.monotonic();C.brightness=1.;I=[];I.extend(AH);K=[];K.extend(AI);A=F.randint(0,255);B=F.randint(0,255);D=F.randint(0,255)
	for E in K:C[E]=A,B,D
	A=F.randint(0,255);B=F.randint(0,255);D=F.randint(0,255)
	while H:
		for E in I:G=F.randint(0,110);M=Ah(A-G,0,255);N=Ah(B-G,0,255);O=Ah(D-G,0,255);C[E]=M,N,O;C.show()
		U(F.uniform(.05,.1));P=J.monotonic()-L
		if P>duration:return
def CC(arr):
	A=arr;B=N(A)//2
	for C in c(B):D=B-1-C;E=B+C;yield(A[D],A[E])
def AL():
	for A in d:
		for B in A:C[B]=0,0,0
def BG():
	A=F.randint(0,2)
	if A==0:B=255;C=255;D=255
	if A==1:B=255;C=0;D=0
	if A==2:B=0;C=0;D=255
	return B,C,D
def CD(duration):
	K=duration;L=J.monotonic();C.brightness=1.;B=[]
	for(D,V)in AM(d):
		if D==F.randint(0,N(d)-1):B.append(D)
	if N(B)==0:D==F.randint(0,N(d)-1);B.append(D)
	for M in w:
		E,H,I=BG()
		for O in M:C[O]=E,H,I
	P=G
	while not P:
		for Q in B:
			E,H,I=BG();R=CC(d[Q])
			for(S,T)in R:
				AL();C[S]=E,H,I;C[T]=E,H,I;C.show();U(.1);A=J.monotonic()-L
				if A>K:AL();C.show();break
			C.show();A=J.monotonic()-L
			if A>K:AL();C.show();break
		A=J.monotonic()-L
		if A>K:AL();C.show();return
def CE(duration):
	G=J.monotonic();C.brightness=1.
	while H:
		for I in c(0,O):
			K=F.randint(128,255);L=F.randint(128,255);M=F.randint(128,255);A=F.randint(0,2)
			if A==0:B=K;D=0;E=0
			elif A==1:B=0;D=L;E=0
			elif A==2:B=0;D=0;E=M
			C[I]=B,D,E;C.show()
		U(F.uniform(.2,.3));N=J.monotonic()-G
		if N>duration:return
def e(item,colorKey,addSub):return A[item][colorKey]+addSub
def CF():
	H=[];I=F.randint(-1,N(w)-1)
	if I!=-1:
		for(D,E)in AM(w):
			if D==I:H.extend(E)
	K=[]
	for(D,E)in AM(d):
		if D==F.randint(0,N(d)-1):K.extend(E)
	L=F.randint(e(i,j,-20),e(i,j,+20));M=F.randint(e(i,k,-8),e(i,k,+8));O=F.randint(e(i,l,-5),e(i,l,+5));P=F.randint(e(h,j,-20),e(h,j,+20));Q=F.randint(e(h,k,-8),e(h,k,+8));R=F.randint(e(h,l,-5),e(h,l,+5));S=F.randint(5,10);C.brightness=F.randint(150,255)/255
	for T in c(0,S):
		A=F.randint(0,50)
		if A<0:A=0
		for U in c(4):
			for G in H:C[G]=L+A,M+A,O+A
			for G in K:C[G]=P+A,Q+A,R+A
			C.show();B=F.randint(0,75);B=B/1000;J.sleep(B);C.fill((0,0,0));C.show()
		B=F.randint(1,50);B=B/1000;J.sleep(B);C.fill((0,0,0));C.show()
def Ah(my_color,lower,upper):
	C=upper;B=lower;A=my_color
	if A<B:A=B
	if A>C:A=C
	return A
class CG:
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
	def reset(A):B1()
class M:
	def __init__(A):0
	@x
	def name(self):return g
	def enter(A,machine):0
	def exit(A,machine):0
	def update(A,machine):0
class CH(M):
	def __init__(A):0
	@x
	def name(self):return Z
	def enter(A,machine):B(BX);D.log_item('Entered base state');M.enter(A,machine)
	def exit(A,machine):M.exit(A,machine)
	def update(D,machine):
		global s;C=Ae.switch_state(I,K,U,3.)
		if C==BY:
			if s:s=G;B(BK)
			else:s=H;B(BJ)
		elif C==Au or s:Ag(A[z])
		elif C==Av:machine.go_to_state(Am)
class CI(M):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@x
	def name(self):return Am
	def enter(A,machine):B('/sd/mvc/main_menu.wav');A7();M.enter(A,machine)
	def exit(A,machine):M.exit(A,machine)
	def update(A,machine):
		C=machine;I.update();K.update()
		if I.fell:
			B(r+AW[A.menuIndex]+P);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
			if A.menuIndex>N(AW)-1:A.menuIndex=0
		if K.fell:
			D=AW[A.selectedMenuIndex]
			if D==Aw:C.go_to_state(Aw)
			elif D==AO:C.go_to_state(AO)
			elif D==Ax:C.go_to_state(Ax)
			elif D==Ay:C.go_to_state(Ay)
			elif D==AN:C.go_to_state(AN)
			else:B(Y);C.go_to_state(Z)
class CJ(M):
	def __init__(A):A.optionIndex=0;A.currentOption=0
	@x
	def name(self):return Aw
	def enter(A,machine):
		R('Choose sounds')
		if E.voice[0].playing:
			E.voice[0].stop()
			while E.voice[0].playing:0
		else:B('/sd/mvc/sound_selection_menu.wav');A7()
		M.enter(A,machine)
	def exit(A,machine):M.exit(A,machine)
	def update(B,machine):
		I.update();K.update()
		if I.fell:
			if E.voice[0].playing:
				E.voice[0].stop()
				while E.voice[0].playing:0
			else:
				try:C=m.WaveFile(o('/sd/lightning_options_voice_commands/option_'+v[B.optionIndex]+P,p));E.voice[0].play(C,loop=G)
				except:C7(f(B.optionIndex+1))
				B.currentOption=B.optionIndex;B.optionIndex+=1
				if B.optionIndex>N(v)-1:B.optionIndex=0
				while E.voice[0].playing:0
		if K.fell:
			if E.voice[0].playing:
				E.voice[0].stop()
				while E.voice[0].playing:0
			else:
				A[z]=v[B.currentOption];D.write_json_file(S,A);C=m.WaveFile(o(BR,p));E.voice[0].play(C,loop=G)
				while E.voice[0].playing:0
			machine.go_to_state(Z)
class CK(M):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@x
	def name(self):return AO
	def enter(A,machine):B('/sd/mvc/add_sounds_animate.wav');A7();M.enter(A,machine)
	def exit(A,machine):M.exit(A,machine)
	def update(A,machine):
		D=machine;global b;I.update();K.update()
		if I.fell:
			B(r+Aa[A.menuIndex]+P);A.selectedMenuIndex=A.menuIndex;A.menuIndex+=1
			if A.menuIndex>N(Aa)-1:A.menuIndex=0
		if K.fell:
			if E.voice[0].playing:
				E.voice[0].stop()
				while E.voice[0].playing:0
			else:
				C=Aa[A.selectedMenuIndex]
				if C=='hear_instructions':B(BS)
				elif C==BL:b=H;B(BM);B(Ap);D.go_to_state(Z)
				elif C==BN:b=G;B(Aq)
				else:B(Y);D.go_to_state(Z)
class CL(M):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@x
	def name(self):return AN
	def enter(A,machine):D.log_item(BZ);B('/sd/mvc/volume_settings_menu.wav');A7();M.enter(A,machine)
	def exit(A,machine):M.exit(A,machine)
	def update(C,machine):
		E=machine;I.update();K.update()
		if I.fell:
			B(r+AZ[C.menuIndex]+P);C.selectedMenuIndex=C.menuIndex;C.menuIndex+=1
			if C.menuIndex>N(AZ)-1:C.menuIndex=0
		if K.fell:
			F=AZ[C.selectedMenuIndex]
			if F=='volume_level_adjustment':
				B('/sd/mvc/volume_adjustment_menu.wav');L=G
				while not L:
					J=Ae.switch_state(I,K,U,3.)
					if J==Au:Af('lower')
					elif J==Av:Af('raise')
					elif J==Ba:D.write_json_file(S,A);B(Y);L=H;E.go_to_state(Z)
					U(.1)
			elif F==Ar:
				A[A5]=G
				if A[q]==0:A[q]=10
				D.write_json_file(S,A);B(Y);E.go_to_state(Z)
			elif F==As:A[A5]=H;D.write_json_file(S,A);B(Y);E.go_to_state(Z)
class CM(M):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@x
	def name(self):return Ay
	def enter(A,machine):D.log_item(BZ);AC();M.enter(A,machine)
	def exit(A,machine):M.exit(A,machine)
	def update(C,machine):
		I.update();K.update()
		if I.fell:
			B(r+AX[C.menuIndex]+P);C.selectedMenuIndex=C.menuIndex;C.menuIndex+=1
			if C.menuIndex>N(AX)-1:C.menuIndex=0
		if K.fell:
			E=AX[C.selectedMenuIndex]
			if E=='web_on':A[Al]=H;BD();AC()
			elif E=='web_off':A[Al]=G;BD();AC()
			elif E=='hear_url':AJ(A[t],H);AC()
			elif E=='hear_instr_web':B('/sd/mvc/web_instruct.wav');AC()
			else:D.write_json_file(S,A);B(Y);machine.go_to_state(Z)
class CN(M):
	def __init__(A):A.menuIndex=0;A.selectedMenuIndex=0
	@x
	def name(self):return Ax
	def enter(A,machine):B('/sd/mvc/light_string_setup_menu.wav');A7();M.enter(A,machine)
	def exit(A,machine):M.exit(A,machine)
	def update(C,machine):
		J=machine;I.update();K.update()
		if I.fell:
			B(r+AY[C.menuIndex]+P);C.selectedMenuIndex=C.menuIndex;C.menuIndex+=1
			if C.menuIndex>N(AY)-1:C.menuIndex=0
		if K.fell:
			E=AY[C.selectedMenuIndex]
			if E=='hear_light_setup_instructions':B('/sd/mvc/string_instructions.wav')
			elif E=='reset_lights_defaults':BB();B('/sd/mvc/lights_reset_to.wav');BE(G)
			elif E=='hear_current_light_settings':BE(H)
			elif E=='clear_light_string':A[T]=g;B('/sd/mvc/lights_cleared.wav')
			elif E=='add_lights':
				B('/sd/mvc/add_light_menu.wav');L=H
				while L:
					F=Ae.switch_state(I,K,U,3.)
					if F==Au:
						C.menuIndex-=1
						if C.menuIndex<0:C.menuIndex=N(A1)-1
						C.selectedMenuIndex=C.menuIndex;B(r+A1[C.menuIndex]+P)
					elif F==Av:
						C.menuIndex+=1
						if C.menuIndex>N(A1)-1:C.menuIndex=0
						C.selectedMenuIndex=C.menuIndex;B(r+A1[C.menuIndex]+P)
					elif F==Ba:
						if A[T]==g:A[T]=A1[C.selectedMenuIndex]
						else:A[T]=A[T]+','+A1[C.selectedMenuIndex]
						B(r+A1[C.selectedMenuIndex]+P);B('/sd/mvc/added.wav')
					elif F==BY:D.write_json_file(S,A);AB();B(Y);L=G;J.go_to_state(Z)
					U(.1)
			else:D.write_json_file(S,A);B(Y);AB();J.go_to_state(Z)
n=CG()
n.add_state(CH())
n.add_state(CI())
n.add_state(CJ())
n.add_state(CK())
n.add_state(CL())
n.add_state(CM())
n.add_state(CN())
A9.value=H
if AG:
	D.log_item('starting server...')
	try:L.start(f(A2.radio.ipv4_address));D.log_item('Listening on http://%s:80'%A2.radio.ipv4_address);BF()
	except OSError:J.sleep(5);D.log_item('restarting...');B1()
n.go_to_state(Z)
D.log_item('animator has started...')
V('animations started.')
while H:
	n.update();U(.02)
	if AG:
		try:L.poll()
		except BH as Ad:D.log_item(Ad);continue