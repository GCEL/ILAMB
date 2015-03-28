import pylab as plt
import numpy as np

def UseLatexPltOptions(fsize=18):
    params = {'axes.titlesize':fsize,
              'axes.labelsize':fsize,
              'font.size':fsize,
              'legend.fontsize':fsize,
              'xtick.labelsize':fsize,
              'ytick.labelsize':fsize}
    plt.rcParams.update(params)
    #plt.rc('text', usetex=True)
    #plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})

def ConfrontationTableASCII(c,M):
    
    # determine header info
    head = None
    for m in M:
        if c.name in m.confrontations.keys():
            head = m.confrontations[c.name]["metric"].keys()
            break
    if head is None: return ""

    # we need to sort the header, I will use a score based on words I
    # find the in header text
    def _columnval(name):
        val = 1
        if "Score"       in name: val *= 2**4
        if "Interannual" in name: val *= 2**3
        if "RMSE"        in name: val *= 2**2
        if "Bias"        in name: val *= 2**1
        return val
    head   = sorted(head,key=_columnval)
    metric = m.confrontations[c.name]["metric"]

    # what is the longest model name?
    lenM = 0
    for m in M: lenM = max(lenM,len(m.name))
    lenM += 1

    # how long is a line?
    lineL = lenM
    for h in head: lineL += len(h)+2

    s  = "".join(["-"]*lineL) + "\n"
    s += ("{0:^%d}" % lineL).format(c.name) + "\n"
    s += "".join(["-"]*lineL) + "\n"
    s += ("{0:>%d}" % lenM).format("ModelName")
    for h in head: s += ("{0:>%d}" % (len(h)+2)).format(h)
    s += "\n" + ("{0:>%d}" % lenM).format("")
    for h in head: s += ("{0:>%d}" % (len(h)+2)).format(metric[h]["unit"])
    s += "\n" + "".join(["-"]*lineL)

    # print the table
    s += ("\n{0:>%d}" % lenM).format("Benchmark")
    for h in head:
        if h in c.metric.keys():
            s += ("{0:>%d,.3f}" % (len(h)+2)).format(c.metric[h]["var"])
        else:
            s += ("{0:>%d}" % (len(h)+2)).format("~")

    for m in M:
        s += ("\n{0:>%d}" % lenM).format(m.name)
        if c.name in m.confrontations.keys():
            for h in head: s += ("{0:>%d,.3f}" % (len(h)+2)).format(m.confrontations[c.name]["metric"][h]["var"])
        else:
            for h in head: s += ("{0:>%d}" % (len(h)+2)).format("~")
    return s

def ConfrontationTableGoogle(c,M,regions=["global"]):
    
    # determine header info
    head = None
    for m in M:
        if c.name in m.confrontations.keys():
            head = m.confrontations[c.name]["metric"].keys()
            break
    if head is None: return ""

    # we need to sort the header, I will use a score based on words I
    # find the in header text
    def _columnval(name):
        val = 1
        if "Score"       in name: val *= 2**4
        if "Interannual" in name: val *= 2**3
        if "RMSE"        in name: val *= 2**2
        if "Bias"        in name: val *= 2**1
        return val
    head   = sorted(head,key=_columnval)
    metric = m.confrontations[c.name]["metric"]

    s  = """
<html>
  <head>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["table"]});
      google.setOnLoadCallback(draw%sTable);
""" % c.name
    s += "      function draw%sTable() {\n" % c.name
    s += "        var data = new google.visualization.DataTable();\n"
    s += "        data.addColumn('string','ModelName');\n"
    for h in head: s += "        data.addColumn('number','%s');\n" % h
    s += "        data.addRows(%d);\n" % (len(M)+1)   
 
    row = 0
    s   += "        data.setCell(%d,0,'Benchmark');" % (row)
    col = 0
    for h in head:
        col += 1
        if h in c.metric.keys():
            s += "data.setCell(%d,%d,%.3f); " % (row,col,c.metric[h]["var"])
        else:
            s += "data.setCell(%d,%d,null); " % (row,col)
    s += "\n"
    for m in M:
        row += 1
        col  = 0
        s   += "        data.setCell(%d,0,'%s'); " % (row,m.name)
        if c.name in m.confrontations.keys():
            for h in head: 
                col += 1
                s   += "data.setCell(%d,%d,%.3f); " % (row,col,m.confrontations[c.name]["metric"][h]["var"])
        else:
            for h in head:
                col += 1
                s   += "data.setCell(%d,%d,null); " % (row,col)
        s += "\n"
    s += """  
        var table = new google.visualization.Table(document.getElementById('table_div'));
        table.draw(data, {showRowNumber: false});

        function updateImages() {
          try {
            var row = table.getSelection()[0].row;
          }
          catch(err) {
            var row = 0;
          }
          var reg = document.getElementById("region").options[document.getElementById("region").selectedIndex].value
          var mod = data.getValue(row, 0)
          document.getElementById("img"  ).src = mod + "_"      + reg + ".png"
          document.getElementById("bias" ).src = mod + "_Bias_" + reg + ".png"
          document.getElementById("mean" ).src = mod + "_Mean.png"
          document.getElementById("cycle").src = mod + "_Cycle.png"
        }

        google.visualization.events.addListener(table, 'select', updateImages);

        table.setSelection([{'row': 0}]);
        updateImages();
      }
    </script>
  </head>
  <body>
    <select id="region" onchange="drawGPPFluxnetGlobalMTETable()">
"""
    for region in regions:
        s += '      <option value="%s">%s</option>\n' % (region,region)
    s += """
    </select>
    <div id="table_div" align="center"></div>
    <div id="img_div" align="center">
      <img src="Benchmark_global.png" id="img"></img>
      <img src="" id="bias"></img><br>
      <img src="" id="mean"></img>
      <img src="" id="cycle"></img>
    </div>
  </body>
</html>"""
    return s

def GlobalPlot(lat,lon,var,region="global.large",shift=False,ax=None,**keywords):
    """

    """
    from mpl_toolkits.basemap import Basemap
    from constants import regions
    lats,lons = regions[region]
    bmap = Basemap(projection='cyl',
                   llcrnrlon=lons[ 0],llcrnrlat=lats[ 0],
                   urcrnrlon=lons[-1],urcrnrlat=lats[-1],
                   resolution='c',ax=ax)
    if shift:
        nroll = np.argmin(np.abs(lon-180))
        alon  = np.roll(lon,nroll); alon[:nroll] -= 360
        tmp   = np.roll(var,nroll,axis=1)
    else:
        alon = lon
        tmp  = var
    vmin = keywords.get("vmin",None)
    vmax = keywords.get("vmax",None)
    cmap = keywords.get("cmap","jet")
    x,y = bmap(alon,lat)
    ax  = bmap.pcolormesh(x,y,tmp,zorder=2,vmin=vmin,vmax=vmax,cmap=cmap)
    bmap.colorbar(ax)
    #bmap.drawmeridians(np.arange(-150,151,30),labels=[0,0,0,1],zorder=1,dashes=[1000000,1],linewidth=0.5)
    #bmap.drawparallels(np.arange( -60, 61,30),labels=[1,0,0,0],zorder=1,dashes=[1000000,1],linewidth=0.5)
    bmap.drawcoastlines(linewidth=0.1)

    
    