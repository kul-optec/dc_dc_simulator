clear all;
close all;

% M = csvread('C:\VibroSens\14.11.2019_14.42.22.vbr',0,0);%radi nr 2
% start_index = 12500;
% final_index = 12550;

 M = csvread(strcat(pwd, '\14.11.2019_14.7.39.vbr'),0,0);%startup
 start_index = 26125;
 final_index = 26200;



%ova sekcija koriguje snimanje ako je pocelo od silazne ivice pwm-a
siz=size(M(:,1));
s1=siz(1);
if (M(1,4)~=0)
    M=M(2:s1,:);
    M(:,1)=M(:,1)-1;
end

%sensor 0
figure;
subplot(3,1,1);
plot(M(:,1), M(:,2));
subplot(3,1,2);
plot(M(:,1), M(:,3));
subplot(3,1,3);
plot(M(:,1), M(:,4));


%sad ide skaliranje na vreme jer je vreme ili inde/x ili index/2+DC/1000...
start_time = start_index/2;
final_time = final_index/2;

%pravim vreme tako sto svaki drugi odbirak procenjujem na osnovu pwm-a

time=M(:,1);
time=floor(time/2);
time=time+M(:,4)/1000;
time = time - start_time;

start_time = 0;
final_time = 20; %final_time - start_time;

%odabrani opseg prikaza napona i struje
figure(1)
clf
set(1,'defaultaxesfontname','courier')
set(1, 'Units','centimeters', 'Position',[0 0 20 15])
subplot(3,1,2);
plot(time, M(:,2)* 3.3/(4096*0.34));
ylabel('$v_C \; [\mbox{V}]$', 'interpreter', 'latex','fontsize',14)
grid minor;
xlim([start_time final_time]);
ylim([0 5]);set(gca,'FontSize',12)
set(gca,'ActivePositionProperty','outerposition');

subplot(3,1,1);
plot(time, M(:,3)* 3.3/(4096*0.5));
grid minor;
xlim([start_time final_time]);
ylim([0 3]);
ylabel('$i_L \; [\mbox{A}]$', 'interpreter', 'latex','fontsize',14)
set(gca,'FontSize',12)
set(gca,'ActivePositionProperty','outerposition');

subplot(3,1,3);

%pwm:
%pravim vreme i prikaz za pwm, jer plot trazi duplo vise tacaka
s=size(time);
s1=s(1);
pwm_display=zeros(1,s1*2);
pwm_time=zeros(1,s1*2);
for i=1:s1
    if (M(i,4)==0) 
        pwm_display(2*i-1)=0;
        pwm_time(2*i-1)=time(i);
        pwm_display(2*i)=1;
        pwm_time(2*i)=time(i)+0.001;
    else
        pwm_display(2*i-1)=1;
        pwm_time(2*i-1)=time(i);
        pwm_display(2*i)=0;
        pwm_time(2*i)=time(i)+0.001;
    end
end

plot(pwm_time, pwm_display);
grid minor;
xlim([start_time final_time]);
ylim([0 1.2]);
ylabel('S', 'interpreter', 'latex','fontsize',14)
xlabel('$t \; [\mbox{ms}]$', 'interpreter', 'latex')
set(gca,'FontSize',12)
set(gca,'ActivePositionProperty','outerposition');



