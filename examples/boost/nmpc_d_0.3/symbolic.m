syms d x t T x1 x2

L = 100e-6;
C = 20e-6;
R = 4;
Vin = 10;
Ts = 1/50e3;


A0 = [0 0; 0 -1/R/C];
b0 = [Vin/L; 0];

A1 = [0 -1/L; 1/C -1/R/C];
b1 = b0;

dd = 0.3;
xx = -(dd*A0 + (1-dd)*A1)^(-1) * (dd*b0 + (1-dd)*b1)
dx = dd*Ts*0.5*(A0 * xx + b0)
xe = xx + dx;

int0 = int(expm(A0*t), t, 0, d*Ts);
int1 = int(expm(A1*t), t, 0, d*Ts);

x = [x1;x2];

exp = expm(A1*(1-d)*Ts)*expm(A0*d*Ts)*x + expm(A1*(1-d)*Ts)*int0*b0 + int1*b1;

derx = jacobian(exp, x);
derx = subs(derx, d, dd);


derd = jacobian(exp, d);
derd = subs(derd, d, dd);
derd = subs(derd, x, xe);

Ad = double(derx)
bd = double(derd)




Q = eye(2);
R = 0.1;
[P,L,G] = dare(Ad,bd,Q,R)
K = -G

alpha = xe'*P*xe
N = 10;
e = min(eig(P^(-0.5)*Q*P^(-0.5)))
real(N*e + alpha)