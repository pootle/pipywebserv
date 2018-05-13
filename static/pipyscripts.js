
window.onload=pipyinit

function pipyinit() {
    if (!!window.EventSource) {
        var tempdataset = new TimeSeries()
        var templine = new SmoothieChart({ fps: 30, millisPerPixel: 200, tooltip: false, minValue:20, maxValue:70,
                grid: { strokeStyle: '#555555', lineWidth: 1, millisPerLine: 5000, verticalSections: 4}});
        templine.addTimeSeries(tempdataset,
                { strokeStyle:'rgb(128, 250, 128)', fillStyle:'rgba(128, 250, 128, 0.4)', lineWidth:2 });
        templine.streamTo(document.getElementById("pitempchart"), 1000);
        var cpudataset = new TimeSeries();
        var cpudatasetavg = new TimeSeries();
        var cpudataavg = 0;
        var cpuchart = new SmoothieChart({ fps: 30, millisPerPixel: 200, tooltip: false, minValue:0, maxValue:100, 
                grid: { strokeStyle: '#555555', lineWidth: 1, millisPerLine: 5000, verticalSections: 4} });
        cpuchart.addTimeSeries(cpudataset,
                { strokeStyle:'rgb(128, 250, 128)', fillStyle:'rgba(128, 250, 128, 0.4)', lineWidth:2 });
        cpuchart.addTimeSeries(cpudatasetavg, 
                { strokeStyle:'rgb(250, 100, 128)', fillStyle:'rgba(250, 100, 128, 0.4)', lineWidth:2 });
        cpuchart.streamTo(document.getElementById("picputime"), 1000);
        var esource = new EventSource("dostream?s=pistatus");
        esource.addEventListener("message", function(e) {
            var newinfo=JSON.parse(e.data);
            tempdataset.append(Date.now(),newinfo.cputemp);
            cpudataset.append(Date.now(), newinfo.busy*100);
            cpudataavg=(cpudataavg*3+newinfo.busy*100)/4;
            cpudatasetavg.append(Date.now(),cpudataavg);
            var cel = document.getElementById("picpuavg");
            cel.innerHTML=cpudataavg.toFixed(2)+"%";
        }, false);
        esource.addEventListener("open", function(e) {
            var tempel = document.getElementById("appmessage");
            tempel.innerHTML="update Connection established";
        }, false);
        esource.addEventListener("error", function(e) {
            var tempel = document.getElementById("appmessage");
            if (e.readyState == EventSource.CLOSED) {
                tempel.innerHTML="update connection lost";
            } else {
                tempel.innerHTML="update connection had an error";
            }
        }, false);
    } else {
        var tempel = document.getElementById("note");
        tempel.innerHTML="I'm sorry Dave, live updates not supported by this browser";
    }
}
