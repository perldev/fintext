let Main = {};
$(function() {
    "use strict";
   /****************************************
         *       Basic Table                   *
         ****************************************/
       let csrftoken = $("[name=csrfmiddlewaretoken]").val();
        $.ajaxSetup({
            headers: { "X-CSRFToken": csrftoken }
        });
        $( document ).ajaxComplete(function( event, xhr, settings ) {
             let cookies = xhr.getResponseHeader('Set-Cookie');
             //csrftoken = xhr
        });
        Main = {
            "chat_interval": 3000,
            "table":null,
            "plotObj": null,
            "current_wallet": "btc",
            "start_chat": function(chat_id, messages_container,  message){
                Main.id_message = "#" + message;
                Main.id_messages_container = "#" + messages_container;
                Main.chat_id= chat_id;
                Main.last_chat_time = null;
                $(Main.id_message).keyup(function(event) {
                      if(event.key == "Enter" ){
                            Main.post_message();
                      }
                });
                Main.update_chat();
                //start poling chat
                Main.chat_polling_timer = setInterval(Main.update_chat, Main.chat_interval)

            },
            "update_chat": function(){
                       var request = $.ajax({
                           url: "/oper/api/get_history/" + Main.chat_id +"/?last="+Main.last_chat_time,
                           method: "GET",
                       });
                       request.done(function( msg ) {
                            var new_messages = msg["result"];
                            new_messages = new_messages.sort(function(a,b){ return a["time"]>b["time"] });
                            for(var index in new_messages){
                                    var i = new_messages[index];
                                    Main.draw_message(i["text"], i["username"], i["time"]);
                                    Main.last_chat_time = i["time"];
                            }


                       });

                       request.fail(function( jqXHR, textStatus ) {
                            Main.alert("не могу  получить историю " );
                       });
             },
             format_time: function(unix_timestamp){
                // Create a new JavaScript Date object based on the timestamp
                // multiplied by 1000 so that the argument is in milliseconds, not seconds.
                var date = new Date(unix_timestamp * 1000);
                // Hours part from the timestamp
                var hours = date.getHours();
                // Minutes part from the timestamp
                var minutes = "0" + date.getMinutes();
                // Seconds part from the timestamp
                var seconds = "0" + date.getSeconds();

                // Will display time in 10:30:23 format
                return hours + ':' + minutes.substr(-2) + ':' + seconds.substr(-2);

             },
             "draw_message": function(msg, username, msg_time){
                               let formated_msg_time = Main.format_time(msg_time)
                               let chat_tmpl = "<div class=\"d-flex flex-row comment-row mt-0\">"
                                    + "<div class=\"p-2\"><img src=\"/static/oper/assets/images/users/1.jpg\" alt=\"user\" class=\"rounded-circle\" width=\"50\"></div>"
                                    + "<div class=\"comment-text w-100\">"
                                    + `<h6 class=\"font-medium\">${username}</h6>`
                                    + `<span class=\"mb-3 d-block\">${msg}</span>`
                                    + "</div>"
                                    + "<div class=\"comment-footer\">"
                                    + `<span class=\"text-muted float-end\">${formated_msg_time}</span>`
                                    + "</div></div>";
                                $(Main.id_messages_container).prepend(chat_tmpl);

             },
             "post_message": function(){
                      let msg_txt = $(Main.id_message).val();

                       var request = $.ajax({
                           url: "/oper/api/post/" + Main.chat_id+"/",
                           method: "POST",
                           data:{"txt": msg_txt},
                        });
                        request.done(function( msg ) {
                           $(Main.id_message).val("");
                          // Main.last_chat_time = msg["time"];
                          // Main.draw_message(msg_txt, Main.username, msg["time"]);

                        });

                        request.fail(function( jqXHR, textStatus ) {
                            Main.alert("не могу  отправить " );
                        });

            },

            "address_list": function(chanel){

                 Main.current_wallet = chanel.toLowerCase();
                 $("#wallets").DataTable().ajax.url('/oper/api/wallets/'+chanel+"/").load();
                 var val = document.getElementById("autosweep_" + Main.current_wallet);
                 if(val && val.value == "yes"){
                    $("#sweep_activated").prop("checked", true);
                 }else{
                    $("#sweep_activated").prop("checked", false);
                 }


            },
            "subscribe_oper": function(){

                  var post_action = function(resp){
                        var li = resp["link"];
                        Main.alert(`<a target=\"_blank\" href=\"${li}\">${li}</a>`, "Ссылка для подписки на уведомления");
                  };
                  var url = $(event.target).data("url");
                  Main.one_line_api(url, post_action)
            },
            "alert": function(msg, title){
                $("#common_modal_dlg_title").html(title);
                $("#common_modal_dlg_text").html(msg);
                $("#common_modal").modal("show");
            },
            "make_process4order": function(i){
                var request = $.ajax({
                   url: "/oper/api/order/status/processed/" + i,
                   method: "GET",
                   dataType: "json"
                });

                request.done(function( msg ) {
                   Main.alert("Done");
                });

                request.fail(function( jqXHR, textStatus ) {
                  Main.alert("не могу изменить статус " );
                });


            },
            "make_cancel4order": function(i){
                var request = $.ajax({
                   url: "/oper/api/order/status/canceled/" + i,
                   method: "GET",
                   dataType: "json"
                });
                request.done(function( msg ) {
                   Main.alert("Done");
                });
                request.fail(function( jqXHR, textStatus ) {
                  Main.alert("не могу изменить статус " );
                });
            },
            update_wallets_list : function(msg){
                $("#wallets").DataTable().ajax.reload()

            },
            show_key_description: function(msg){
                 Main.alert(msg["description"]);
            },
            gather_now : function(){
                let url = "/oper/api/create_task4sweep/"

                let currency_to_gather = Main.current_wallet;
                let amnt = prompt("Укажите минимальную сумму(если 0, то собирается все), которую вы хотели бы собирать для " + currency_to_gather , 1);
                var request = $.ajax({
                   url: url+"?_="+new Date(),
                   method: "POST",
                   data:{"min_amnt": amnt,
                         "currency": currency_to_gather},
                   dataType: "json"
                });
                request.done(Main.show_key_description);
                request.fail(function( jqXHR, textStatus ) {
                   try {
                            var a = JSON.parse(jqXHR.responseText);
                            Main.alert(a["description"]);
                        } catch(e) {
                              Main.alert("не могу завершить действие " + url );
                        }

                });


            },
            confirm_params4task_spread: function(url, postaction ){
                let amnt = prompt("Укажите сумму, которую вы хотели бы распределить", "1");
                var request = $.ajax({
                   url: url+"?_="+new Date(),
                   method: "POST",
                   data:{"amnt": amnt},
                   dataType: "json"
                });
                request.done(function( msg ) {
                  if(postaction){
                        return postaction(msg)

                  }
                });
                request.fail(function( jqXHR, textStatus ) {
                   try {
                            var a = JSON.parse(jqXHR.responseText);
                            Main.alert(a["description"]);
                        } catch(e) {
                              Main.alert("не могу завершить действие " + url );
                        }

                });

            },
            one_line_api: function(url, postaction){
              if(!url){
                    url = $(event.target).data("url")
              }
              if(!url){
                    Main.alert("Техническая ошибка, напишите разрабам")
                    return;
              }
              if(postaction){
                      postaction = $(event.target).data("postaction")
                      if(postaction)
                         postaction = eval(postaction)
              }
              var request = $.ajax({
                   url: url+"?_="+new Date(),
                   method: "GET",
                   dataType: "json"
                });
                request.done(function( msg ) {
                  if(postaction){
                        postaction(msg)

                  }else{
                    Main.alert("Ok!");
                  }
                  return  true;
                });
                request.fail(function( jqXHR, textStatus ) {
                   try {
                            var a = JSON.parse(jqXHR.responseText);
                            Main.alert(a["description"]);
                        } catch(e) {
                              Main.alert("не могу завершить действие " + url );
                        }

                });
            },
            whole_order_info: function(order_id, view_id){
                   var url = "/oper/api/orders/" + order_id;
                   var request = $.ajax({
                                    url: url,
                                    method: "GET",
                                    dataType: "json"
                                });
                    request.done(function( msg ) {
                        $(view_id).html(Main.simple_form(msg["order"], ["pk"]));
                    });
                    request.fail(function( jqXHR, textStatus ) {
                        Main.alert("не могу получить данные для ордеру");
                    });

            },
            simple_form: function(fields, except){
                    var res = [];
                    var terms = {
                        "account": "Адрес/Cчет",
                        "payment_id": "Доп.данные",
                        "status": "Cтатус",
                        "currency":	"Валюта",
                        "pub_date":	"Дата",
                        "processed_date": "Дата проведения",
                        "amnt":	"Сумма",
                         "buy": "Продажа",
                        "sell": "Покупка",
                        "operator": "оператор",
                        "client_info": "информация о клиенте",
                        "client_payed": "Статус оплаты",
                        "invoice_address": "Платежные данные оплаты",
                        "trans_info": "платежные данные выплаты",
                         "client_get": "статус выплаты",
                        "client_telegram_connected": "подключился к боту",
                        "rate": "курс",
                    }
                    for(var key in fields){
                        var name = key;
                        if(name in except){
                            continue;
                        }
                        if(key in terms){
                            name = terms[key]
                        }
                        var s = `<div class="form-group row">
                <label class="col-4 col-form-label" for=""><strong>${name}</strong></label>
                <div class="col-8">
                    ${fields[key]}
                </div>
              </div>`
                        res.push(s)
                    }
                    return res.join("")
            },
            autosweep_managing: function(ev){


                var url = "/oper/api/manage/autosweep/" + Main.current_wallet;
                var request = $.ajax({
                   url: url,
                   method: "GET",
                   dataType: "json"
                });
                request.done(function(msg){
                    $("#"+msg["name"]).val(msg["value"]);
                    Main.show_key_description(msg);

                });
                request.fail(function( jqXHR, textStatus ) {
                    Main.alert("не могу завершить действие");
                });


            },
            data_online_api: function(obj, post_action){
                var url = $(obj).data("api-url");
                Main.one_line_api(url, post_action)
            },
            show_trans_info: function(i){
                var url = "/oper/api/order/show_payment/"+i;
                var request = $.ajax({
                   url: url,
                   method: "GET",
                   dataType: "json"
                });
                 request.done(function( msg ) {
                        $("#info_modal").modal("show");
                        $("#info_modal_title").html("#" + msg["trans"][0]["pk"]);
                        $("#info_modal_dlg").html(Main.simple_form(msg["trans"][0]["fields"]));
                        $("#info_modal_dlg_save").data({"api-url": "/oper/api/trans/processed/" + msg["trans"][0]["pk"]});
                });
                request.fail(function( jqXHR, textStatus ) {
                  Main.alert("не могу получить данные для транзакции");
                });


            },
            find_max: function(list, key_func){
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
            },
            prepare_data4plot:function(data){
                    // Since the axes don't change, we don't need to call plot.setupGrid()


                     //[{data: data["buy"], label: "покупка", }, {data: data["sell"], label: "продажа" }]

                    // Since the axes don't change, we don't need to call plot.setupGrid()
                        var sin = []
                            , cos = [],
                            offset=1;
                        for (var i = 0; i < 12; i += 0.2) {
                            sin.push([i, Math.sin(i + offset)]);
                            cos.push([i, Math.cos(i + offset)]);
                        }
                    let buy_sum=[];
                    let buy_rate=[];
                    let sell_sum=[];
                    let sell_rate=[];

                    for(var i in data["buy"]){
                        var item = data["buy"][i];
                        var j=item["dt"];
                 //       var j = i;
                        buy_sum.push([j, item["sm"]]);
                        buy_rate.push([j, item["rate"]]);

                    }
                    for(var i in data["sell"]){
                        var item = data["sell"][i];
                        var j=item["dt"];
               //         var j = i;
                        sell_sum.push([j , item["sm"]]);
                        sell_rate.push([j, item["rate"]]);
                    }

                    return [
                             {"data": buy_sum, "label":"сумма покупки"},
                             {"label":"средние курс" , "data":buy_rate},
                              {"label":"продажа сумма",data:sell_sum},
                              {"label":"продажа курс", data:sell_rate},

                             ]

            },
            draw_plot: function(data){
                           var options = {legend: true,
                                       xaxis: {
                                            mode: "categories",
                                            showTicks: false,
                                            gridLines: false
                                       },
                                       series: {
                                            bars: {
                                                show: true,
                                                barWidth: 0.6,
                                                align: "center"
                                            }
                                       },
                                       legend:{show:true},
                                       color: "#2b2b2b"};

                            let prepared_data = Main.prepare_data4plot(data);

                            Main.plotObj = $.plot($("#flot-line-chart"), prepared_data,  options);



            },
            plot_deals: function(ev, currency1, currency2){

                var url = "/oper/api/get_deals_data/" + currency1 + "/" + currency2 + "/"
                var request = $.ajax({
                   url: url+"?_="+new Date(),
                   method: "GET",
                   dataType: "json"
                });

                request.done(function( msg ) {
                    Main.draw_plot(msg["data"])
                });

                request.fail(function( jqXHR, textStatus ) {
                        try {
                            var a = JSON.parse(jqXHR.responseText);
                            Main.alert(a["description"]);
                        } catch(e) {
                              Main.alert("не могу завершить действие " + url );
                        }

                });



            }

        }
        $('.zero_tables').each(function(){
                var api_url = $(this).data("api-url");
                var columns = []
                 $(this).find('thead tr th ').each(function(){
                    columns.push({"data":$(this).data("col")});
                });

                 var table = $(this).DataTable({ajax:api_url,
                                                columns: columns,
                                                order: [[0, 'desc']],
                                                });
                 $(this).find("tbody").on('mouseenter', 'td', function () {
                    var colIdx = table.cell(this).index().column;
                    $(table.cells().nodes()).removeClass('odd');
                    $(table.column(colIdx).nodes()).addClass('odd');
                });

        });
        $(".edit_vals").each(function(){
               var api_url = $(this).data("url");
                var postaction = $(this).data("post_action");
                $(this).on("keyup", function(){
                   var val = $(this).val();
                   var name = $(this).attr("name");

                   var request = $.ajax({
                                        url: api_url+"?_="+new Date(),
                                        method: "POST",
                                        dataType: "json",
                                        data:{"val":val, "name":name}
                                    });
                   request.done(function( msg ) {
                      if(postaction){
                            let functionObj = window[postaction];
                            functionObj(msg)
                      }else{
                        Main.alert("Ok!");
                      }
                      return  true;
                    });
                    request.fail(function( jqXHR, textStatus ) {
                       try {
                                var a = JSON.parse(jqXHR.responseText);
                                Main.alert(a["description"]);
                            } catch(e) {
                                  Main.alert("не могу завершить действие " + url );
                            }

                    });
                   });
                });


        }
        );
