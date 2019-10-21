n = 0:length(log.d)-1;
fs = 50e3;
n = n/fs * 1e3;

figure(1)
clf
set(1,'defaultaxesfontname','courier')
set(1, 'Units','centimeters', 'Position',[0 0 30 15])
subplot_tight(2,2,1, [0.1 0.1]), stairs(n,log.d);
grid on
ylabel('$d$', 'interpreter', 'latex','fontsize',14)
%xlabel('$t \; [\mbox{ms}]$', 'interpreter', 'latex') 
set(gca,'FontSize',12)
set(gca,'ActivePositionProperty','outerposition');

subplot_tight(2,2,3, [0.1 0.1]), stairs(n,log.cost);
grid on
ylabel('cost', 'interpreter', 'latex','fontsize',14)
xlabel('$nT_S \; [\mbox{ms}]$', 'interpreter', 'latex')
set(gca,'FontSize',12)
set(gca,'ActivePositionProperty','outerposition');

subplot_tight(2,2,2, [0.1 0.1]), stairs(n,log.time);
grid on
ylabel('CPU time $[\mu\mbox{s}]$', 'interpreter', 'latex','fontsize',14)
%xlabel('$t \; [\mbox{ms}]$', 'interpreter', 'latex')
set(gca,'FontSize',12)
set(gca,'ActivePositionProperty','outerposition');

subplot_tight(2,2,4, [0.1 0.1]), stairs(n,log.steps);
grid on
ylabel('iterations', 'interpreter', 'latex','fontsize',14)
xlabel('$nT_S \; [\mbox{ms}]$', 'interpreter', 'latex')
set(gca,'FontSize',12)
set(gca,'ActivePositionProperty','outerposition');