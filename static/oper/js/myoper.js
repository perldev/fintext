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



        let Main = {
            "chat_interval": 3000,
            "start_chat": function(chat_id, messages_container,  message){
                Main.id_message = "#" + message;
                Main.id_messages_container = "#" + messages_container;
                Main.chat_id= chat_id;
                Main.last_chat_time = null;
                $(id_message).keyup(function(event) {
                      if(!event.which= 13 ){
                            return true;
                      }
                      Main.post_message();
                });
                Main.update_chat();
                //start poling chat
                Main.chat_polling_timer = setInterval(Main.update_chat, Main.chat_interval)

            },
            "update_chat": function(){
                        let msg_txt = $(Main.message).val();
                       var request = $.ajax({
                           url: "/oper/api/get_history/" + Main.chat_id,
                           method: "GET",
                           params: {"last": Main.last_chat_time}
                        });
                        request.done(function( msg ) {
                            var new_messages = msg["result"];
                            new_messages = new_messages.sort(function(a,b){ return a["time"]<b["time"] });
                            for(var i in new_messages){
                                    Main.draw_message(i["text"], i["username"], i["time"]);
                                    Main.last_chat_time = i["time"];
                            }


                        });

                        request.fail(function( jqXHR, textStatus ) {
                            Main.alert("не могу  получить историю " );
                        });
             },
             "draw_message": function(msg, username, msg_time){
                               let = formated_msg_time = Main.format_time(msg_time)
                               let chat_tmpl = "<div class=\"d-flex flex-row comment-row mt-0\">
                                    + "<div class=\"p-2\"><img src=\"/static/oper/assets/images/users/1.jpg\" alt=\"user\" class=\"rounded-circle\" width=\"50\"></div>"
                                    + "<div class=\"comment-text w-100\">"
                                    + "<h6 class=\"font-medium\">${username}</h6>"
                                    + "<span class=\"mb-3 d-block\">${msg}</span>"
                                    + "</div>"
                                    + "<div class=\"comment-footer\">"
                                    + "<span class=\"text-muted float-end\">${formated_msg_time}</span>"
                                    + "</div></div>";
                                $(Main.id_messages_container).prepand(chat_tmpl);

             },
             "post_message": function(){
                      let msg_txt = $(Main.message).val();
                       var request = $.ajax({
                           url: "/oper/api/post/" + Main.chat_id,
                           method: "POST",
                           params:{"txt": msg_txt},
                           dataType: "json"
                        });
                        request.done(function( msg ) {
                           $(message).val("");
                           Main.last_chat_time = msg["time"];
                           Main.draw_message(msg_txt, Main.username, msg["time"]);

                        });

                        request.fail(function( jqXHR, textStatus ) {
                            Main.alert("не могу  отправить " );
                        });


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
            }
        }

        $('#zero_config').DataTable({
                               ajax: '/oper/api/orders',
                               columns: [
                                { data: 'buy' },
                                { data: 'sell' },
                                { data: 'rate' },
                                { data: 'pub_date' },
                                { data: 'operator' },
                                { data: 'client_info' },
                                { data: 'client_payed' },
                                { data: 'client_get' },
                                { data: 'status' },
                                { data: 'actions' },
                            ]
        });
         $('#zero_config tbody').on('mouseenter', 'td', function () {
            var colIdx = table.cell(this).index().column;

            $(table.cells().nodes()).removeClass('odd');
            $(table.column(colIdx).nodes()).addClass('odd');
        });

});