  $(function() {

    var updateInterval = 5000;
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
    $.ajaxSetup({
        headers: { "X-CSRFToken": csrftoken }
    });


    // we use an inline data source in the example, usually data would
    // be fetched from a server
   // ==============================================================
    // Real Time Visits
    // ==============================================================
    function create_plot(name, value){
        var plot_id = "#real-time" + name + "_" + val;
        var plot = $.plot(plot_id, [[]], {
        series: {
            shadowSize: 1, // Drawing is faster without shadows
            lines: { fill: true, fillColor: 'transparent' },
        },
        yaxis: {
            min: 0,
            max: 100,
            show: true
        },
        xaxis: {
            show: false
        },
        colors: ["#488c13"],
        grid: {
            color: "#AFAFAF",
            hoverable: true,
            borderWidth: 0,
            backgroundColor: 'transparent'
        },
        tooltip: true,
        tooltipOpts: {
            content: "date: %x",
            defaultTheme: false
        }
    });


    function data_handler(data) {

        plot.setData([data]);
        // Since the axes don't change, we don't need to call plot.setupGrid()
        plot.draw();
        setTimeout(update, updateInterval);
    };

    function update(){
        getDataRates(name, val, data_handler)
    };
    window.onresize = function(event) {
        $.plot($(plot_id), [[]]);
        update();
    }
    update();




    };


    function getDataRates(chanelName, rate_name, callback_handler){
               var request = $.ajax({
                   url: "/api/oper/getDataRate/" + Name + "/" + rate_name,
                   method: "GET",
                   dataType: "json"
                });

                request.done(function( msg ) {

                  var res = [];
                    for (var i = 0; i < data.length; ++i) {
                        var item = data[i];
                        var k = item["name"];
                        var val = item["value"];
                        res.push([k, val]);
                    }
                    callback_handler(res);
                });

                request.fail(function( jqXHR, textStatus ) {
                  alert("не могу получить данные по курсу " + rate_name +" на " + chanelName );
                });


    }
    //setup plots from different stocks
     var plots = [{"name":"bitstamp", "val":"btc_usd"},
                  {"name":"bitstamp", "val":"eth_usd"},
                  {"name":"kuna", "val":"btc_uah"},
                  {"name":"btctradeua", "val": "btc_uah"}];

    for(k in plots){
            var item = plots[k]
            create_plot(item["name"], item["val"])
    }

    function getRandomData() {
        if (data.length > 0) data = data.slice(1);
        // Do a random walk
        while (data.length < totalPoints) {
            var prev = data.length > 0 ? data[data.length - 1] : 10,
                y = prev + Math.random() * 10 - 5;
            if (y < 0) {
                y = 0;
            } else if (y > 100) {
                y = 100;
            }
            data.push(y);
        }
        // Zip the generated y values with the x values
        var res = [];
        for (var i = 0; i < data.length; ++i) {
            res.push([i, data[i]])
        }
        return res;
    }
    // Set up the control widget
    $("#updateInterval").val(updateInterval).change(function() {
        var v = $(this).val();
        if (v && !isNaN(+v)) {
            updateInterval = +v;
            if (updateInterval < 1) {
                updateInterval = 1;
            } else if (updateInterval > 1000) {
                updateInterval = 1000;
            }
            $(this).val("" + updateInterval);
        }
    });
    var plot = $.plot("#real-time", [getRandomData()], {
        series: {
            shadowSize: 1, // Drawing is faster without shadows
            lines: { fill: true, fillColor: 'transparent' },
        },
        yaxis: {
            min: 0,
            max: 100,
            show: true
        },
        xaxis: {
            show: false
        },
        colors: ["#488c13"],
        grid: {
            color: "#AFAFAF",
            hoverable: true,
            borderWidth: 0,
            backgroundColor: 'transparent'
        },
        tooltip: true,
        tooltipOpts: {
            content: "Visits: %x",
            defaultTheme: false
        }
    });
    window.onresize = function(event) {
        $.plot($("#real-time"), [getRandomData()]);
    }

    function update() {

        plot.setData([getRandomData()]);
        // Since the axes don't change, we don't need to call plot.setupGrid()
        plot.draw();
        setTimeout(update, updateInterval);
    }
    update();

        console.log("document ready");
        var offset = 0;
        plot1();

        function plot1() {
            var sin = []
                , cos = [];
            for (var i = 0; i < 12; i += 0.2) {
                sin.push([i, Math.sin(i + offset)]);
                cos.push([i, Math.cos(i + offset)]);
            }
            var options = {
                series: {
                    lines: {
                        show: true
                    }
                    , points: {
                        show: true
                    }
                }
                , grid: {
                    hoverable: true //IMPORTANT! this is needed for tooltip to work
                }
                , yaxis: {
                    min: -1.2
                    , max: 1.2
                }
                , colors: ["#ee7951", "#4fb9f0"]
                , grid: {
                    color: "#AFAFAF"
                    , hoverable: true
                    , borderWidth: 0
                    , backgroundColor: '#FFF'
                }
                , tooltip: true
                , tooltipOpts: {
                    content: "'%s' of %x.1 is %y.4"
                    , shifts: {
                        x: -60
                        , y: 25
                    }
                }
            };
            var plotObj = $.plot($("#flot-line-chart"), [{
                data: sin
                , label: "sin(x)"
            , }, {
                data: cos
                , label: "cos(x)"
                }], options);
        }

});