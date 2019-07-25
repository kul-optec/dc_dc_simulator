function printpdf(outfilename, h)

    if nargin == 1
        h = gcf;
    end

    set(h, 'PaperUnits','centimeters');
    set(h, 'Units','centimeters');
    pos=get(h,'Position');
    set(h, 'PaperSize', [pos(3) pos(4)]);
    set(h, 'PaperPositionMode', 'manual');
    set(h, 'PaperPosition',[0 0 pos(3) pos(4)]);
    set(h,'Renderer','opengl')
    print('-dpdf', '-r600', outfilename);
%     set(h,'renderer','opengl')
%     print('-dpdf', '-r300', outfilename);
end