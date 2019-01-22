syms L1 C1 R d Vin il1 vc1 s
 
A0 = [0 0; 0 -1/R/C1];
A1 = [0 -1/L1; 1/C1 -1/R/C1];
b0 = [1/L1; 0];
b1 = b0;

C0 = [0; 1];

A = d * A0 + (1-d) * A1;
b = d * b0 + (1-d) * b1;
C = d * C0 + (1-d) * C1;
x = [il1; vc1];
sol = solve(A*x + b * Vin == 0);
xx = [sol.il1; sol.vc1];

E = (A0 - A1) * xx + (b0 - b1) * Vin;
F = 0;
B = [b E];

t = (s*eye(2) - A)^(-1) * B;

t = subs(t, L1, 100e-6);
t = subs(t, C1, 20e-6);
t = subs(t, R, 4);
t = subs(t, Vin, 10);
t = subs(t, d, 0.3);
[num,den] = numden(t(2,2));
nums = sym2poly(num);
dens = sym2poly(den);

H = tf(nums,dens);
figure(1)
subplot(2, 1, 1)
% w = logspace(2, 6, 401);
h = bodeplot(H)
p = getoptions(h); 
p.PhaseMatching = 'on'; 
p.PhaseMatchingFreq = 1; 
p.PhaseMatchingValue = 0;
setoptions(h,p);
title('uncompensated-bode')

f = 50e3;
wc = 2*pi*f / 10;
k = 1 / abs(evalfr(H,j*wc));
Hc = k*H;
wc_check = getGainCrossover(Hc,1);
[Gm,Pm,Wcg,Wcp] = margin(k*H);

subplot(2, 1, 2)
h = bodeplot(Hc)
p = getoptions(h); 
p.PhaseMatching = 'on'; 
p.PhaseMatchingFreq = 1; 
p.PhaseMatchingValue = 0;
setoptions(h,p);
title('wc-bode')

% lead-lag optimal
phi = -145 - (angle(evalfr(Hc,j*wc))*180/pi - 360);
phi = phi * pi / 180;
p = sqrt((1 + sin(phi))/(1-sin(phi)))
wz = wc/p;
wp = wc*p;
Glead = 1/p * tf([1/wz, 1], [1/wp, 1]);
Hlead = Hc * Glead;

figure(2)
h = bodeplot(Hlead)
p = getoptions(h); 
p.PhaseMatching = 'on'; 
p.PhaseMatchingFreq = 1; 
p.PhaseMatchingValue = 0;
setoptions(h,p);
title('wc-bode')

wl = wc/10;
Glag = wl * tf([1/wl, 1], [1, 0]);
Hleadlag = Hc * Glead * Glag;

figure(3)
h = bodeplot(Hleadlag)
p = getoptions(h); 
p.PhaseMatching = 'on'; 
p.PhaseMatchingFreq = 1; 
p.PhaseMatchingValue = 0;
setoptions(h,p);
title('leadlag-bode')

Hclosedloop = Hleadlag/(1+Hleadlag)

figure(4)
step(Hclosedloop)