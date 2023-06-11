  "use strict";
  let Calculator = {"current":null};

  $(function() {

    $("#calc_rate").val("");
    //TODO update crf token
    let csrftoken = $("[name=csrfmiddlewaretoken]").val();
    $.ajaxSetup({
        headers: { "X-CSRFToken": csrftoken }
    });
    $( document ).ajaxComplete(function( event, xhr, settings ) {
         let cookies = xhr.getResponseHeader('Set-Cookie');
         //csrftoken = xhr
    });


    Calculator.exchange_change = function(event, from, to){
        //save the state of current
        $(".calc_buttons").removeClass("btn-primary");
        $(event.target).addClass("btn-primary");
        Calculator.current = [from, to];
        var request = $.ajax({
                   url: "/oper/api/get_direction/" + from + "/" + to+"/",
                   method: "GET",
                   dataType: "json"
                });

                request.done(function( msg ) {
                  var data  = msg["raw_data"];
                  $("#calc_rate").val(data);
                });

                request.fail(function( jqXHR, textStatus ) {
                  alert("не могу получить данные по курсу " + from +" на " + to );
                });




    };
    Calculator.test_change = function(){
               var from  = Calculator.current[0];
               var to  = Calculator.current[1];
               var code = $("#calc_rate").val();

               var request = $.ajax({
                   'url': "/oper/api/test_rate/",
                   'data': code, //{action:'x',params:['a','b','c']}
                   'type': 'POST',
                   'processData': false,
                   'contentType': 'application/json'
                });
                request.done(function( msg ) {
                  var data  = msg["result"];
                  alert("результат выполнения  " + from +" на " + to + ": " + data  );
                });

                request.fail(function( jqXHR, textStatus ) {
                  alert("не могу получить данные по курсу " + from +" на " + to );
                });


    };
    Calculator.save_change = function(){
               var from  = Calculator.current[0];
               var to  = Calculator.current[1];
               var code = $("#calc_rate").val();
               var request = $.ajax({
                   'url': "/oper/api/save_rate/"+from+"/" + to +"/",
                   'data': code,
                   'type': 'POST',
                   'processData': false,
                   'contentType': 'application/json'
                });
                request.done(function( msg ) {
                  var data  = msg["result"];
                  alert("Сохраненны данные по направлению  " + from +" на " + to  );
                });

                request.fail(function( jqXHR, textStatus ) {
                  alert("не могу сохранить данные по курсу " + from +" на " + to );
                });

    };

    var updateInterval = 15000;
    function find_max(list, key_func){
        var max_val = -100000000000000000;
        var min_val = 1000000000000000;

        for(var i=0; i<list.length; i++){
            var current = key_func(list[i]);
            if(current>max_val)
                max_val=current
            if(current<min_val)
                min_val = current
        }
        return max_val, min_val;
    }


    // we use an inline data source in the example, usually data would
    // be fetched from a server
   // ==============================================================
    // Real Time Visits
    // ==============================================================
    function create_plot(plot, name, value, init_vals){
        console.log("drawing plot", name, value);

        var plot_id = "#real-time" + name + "_" + value;
        var max_val, min_val = find_max(init_vals, function(x){ return  x[1]});
        plot["name"] = name;
        plot["value"] = value;

        plot["plot_obj"] = $.plot(plot_id, [init_vals], {
            series: {
                shadowSize: 1, // Drawing is faster without shadows
                lines: { fill: true, fillColor: 'transparent' },
            },
            yaxis: {
                min: min_val,
                max: max_val,
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
                content: "%y.10",
                defaultTheme: false
            }
        });

        plot["data_handler"] = function data_handler(data) {
            plot["plot_obj"].setData([data]);
            // Since the axes don't change, we don't need to call plot.setupGrid()
            plot["plot_obj"].draw();
            setTimeout(plot["update"], updateInterval);
        };

        plot["update"] = function update(){
                                getDataRates(plot["name"], plot["value"],  plot["data_handler"])
                          };




    };


    function getDataRates(chanelName, rate_name, callback_handler){
               var request = $.ajax({
                   url: "/api/oper/getDataRate/" + chanelName + "/" + rate_name+"/",
                   method: "GET",
                   dataType: "json",
                  success: function( msg ) {
                          var data  = msg["result"]
                          var res = [];
                          var last="";
                            for (var i = 0; i < data.length; ++i) {
                                var item = data[i];
                                var k = item["name"];
                                var val = item["value"];
                                if(val>0){
                                    res.push([i, val]);
                                    last = val;
                                }

                            }

                            $("#context_"+chanelName+"_"+rate_name).html(last);
                            callback_handler(res);
                 },
                fail: function( jqXHR, textStatus ) {
                  alert("не могу получить данные по курсу " + rate_name +" на " + chanelName );
                 }
                });


    }
    //setup plots from different stocks
    let plots = [{"name":"bitstamp", "val":"btc_usd", "plot":{}},
                 {"name":"bitstamp", "val":"eth_usd", "plot": {}},
                 {"name":"kuna", "val":"btc_uah", "plot": {}},
                 {"name":"btctradeua", "val": "btc_uah", "plot": {}},

                 {"name":"whitebit", "val": "btc_uah", "plot": {}},
                 {"name":"whitebit", "val": "usdt_uah", "plot": {}},
                 {"name":"whitebit", "val": "eth_uah", "plot": {}},

                 {"name":"whitebit", "val": "uah_btc", "plot": {}},
                 {"name":"whitebit", "val": "uah_usdt", "plot": {}},
                 {"name":"whitebit", "val": "uah_eth", "plot": {}},


                 {"name":"whitebit", "val": "btc_usd", "plot": {}},
                 {"name":"whitebit", "val": "usd_btc", "plot": {}},

                 {"name":"whitebit", "val": "eth_usd", "plot": {}},
                 {"name":"whitebit", "val": "usd_eth", "plot": {}},

                 {"name":"etherscan21000", "val": "eth_eth", "plot": {}},


                ];

    if(true){
            //looks strange but do not work with cycle
            //        for(var k in plots){


                getDataRates(plots[0]["name"],
                             plots[0]["val"],
                             function(result){
                                    create_plot(plots[0]["plot"],
                                                plots[0]["name"],
                                                plots[0]["val"], result)
                             }
                             );



            //        for(var k in plots){
                let plot = null;
                getDataRates(plots[1]["name"],
                             plots[1]["val"],
                             function(result){
                                    create_plot(plots[1]["plot"],
                                                plots[1]["name"],
                                                plots[1]["val"], result)
                             }
                             );
                getDataRates(plots[2]["name"],
                             plots[2]["val"],
                             function(result){
                                    create_plot(plots[2]["plot"],
                                                plots[2]["name"],
                                                plots[2]["val"], result)
                             }
                             );
                getDataRates(plots[3]["name"],
                             plots[3]["val"],
                             function(result){
                                    create_plot(plots[3]["plot"],
                                                plots[3]["name"],
                                                plots[3]["val"], result)
                             }
                             );
                getDataRates(plots[4]["name"],
                             plots[4]["val"],
                             function(result){
                                    create_plot(plots[4]["plot"],
                                                plots[4]["name"],
                                                plots[4]["val"], result)
                             }
                             );
                getDataRates(plots[5]["name"],
                             plots[5]["val"],
                             function(result){
                                    create_plot(plots[5]["plot"],
                                                plots[5]["name"],
                                                plots[5]["val"], result)
                             }
                );
                getDataRates(plots[6]["name"],
                             plots[6]["val"],
                             function(result){
                                    create_plot(plots[6]["plot"],
                                                plots[6]["name"],
                                                plots[6]["val"], result)
                             }
                );

                 getDataRates(plots[7]["name"],
                             plots[7]["val"],
                             function(result){
                                    create_plot(plots[7]["plot"],
                                                plots[7]["name"],
                                                plots[7]["val"], result)
                             }
                );
                plot = plots[8];
                getDataRates(plot["name"],
                             plot["val"],
                             function(result){
                                    create_plot(plot["plot"],
                                                plot["name"],
                                                plot["val"], result)
                             }
                );
                 plot = plots[9];
                getDataRates(plot["name"],
                             plot["val"],
                             function(result){
                                    create_plot(plot["plot"],
                                                plot["name"],
                                                plot["val"], result)
                             }
                );
                 plot = plots[10];
                getDataRates(plot["name"],
                             plot["val"],
                             function(result){
                                    create_plot(plot["plot"],
                                                plot["name"],
                                                plot["val"], result)
                             }
                );
                plot = plots[11];
                getDataRates(plot["name"],
                             plot["val"],
                             function(result){
                                    create_plot(plot["plot"],
                                                plot["name"],
                                                plot["val"], result)
                             }
                );
                plot = plots[12];
                getDataRates(plot["name"],
                             plot["val"],
                             function(result){
                                    create_plot(plot["plot"],
                                                plot["name"],
                                                plot["val"], result)
                             }
                );
                plot = plots[13];
                getDataRates(plot["name"],
                             plot["val"],
                             function(result){
                                    create_plot(plot["plot"],
                                                plot["name"],
                                                plot["val"], result)
                             }
                );
                plot = plots[14];
                getDataRates(plot["name"],
                             plot["val"],
                             function(result){
                                    create_plot(plot["plot"],
                                                plot["name"],
                                                plot["val"], result)
                             }
                );


        //}
    }else{
        create_plot("bitstamp", "btc_usd");

    }

    // Set up the control widget
    /*
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
    });*/

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