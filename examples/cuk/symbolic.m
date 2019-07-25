syms d x t T x1 x2 x3 x4

L1 = 645.4e-6;
C1 = 217e-9;
R = 43.0;
L2 = 996.3e-6;
C2 = 14.085e-6;
Vin = 5;
Ts = 1/30e3;

A0 = [0 0 0 0; 0 0 -1/L2 -1/L2; 0 1/C1 0 0; 0 1/C2 0 -1/R/C2];
b0 = [Vin/L1; 0; 0; 0];

A1 = [0 0 -1/L1 0; 0 0 0 -1/L2; 1/C1 0 0 0; 0 1/C2 0 -1/R/C2];
b1 = b0;

dd = 0.5;
xx = -(dd*A0 + (1-dd)*A1)^(-1) * (dd*b0 + (1-dd)*b1)
dx = dd*Ts*0.5*(A0 * xx + b0)
xe = xx + dx;

int0 = int(expm(A0*T), T, 0, d*Ts);
int1 = int(expm(A1*t), t, 0, (1-d)*Ts);

x = [x1;x2;x3;x4];

exp = expm(A1*(1-d)*Ts)*expm(A0*d*Ts)*x + expm(A1*(1-d)*Ts)*int0*b0 + int1*b1;

derx = jacobian(exp, x);
derx = subs(derx, d, dd);


derd = jacobian(exp, d);
derd = subs(derd, [d, x], [dd, xe]);

Ad = double(derx)
bd = double(derd)

Q = eye(4);
R = 0.1*eye(2);
[P,L,G] = dare(Ad,bd,Q,R)
K = -G

alpha = xe'*P*xe
N = 10;
e = min(eig(P^(-0.5)*Q*P^(-0.5)))
real(N*e + alpha)