
let avaliable_pairs = [
    'btc_uah',
    'uah_btc',
    'eth_uah',
    'usdt_uah'
]

let main_rate = 0;
let rate_message = document.getElementById("rate-message");
rate_message.innerHTML = `Загрузка курса...`;
let given_cur_input = document.getElementById("given-cur-input");
let taken_cur_input = document.getElementById("taken-cur-input");
let given_cur_select = document.getElementById("given-cur-select");
let taken_cur_select = document.getElementById("taken-cur-select");


const NUMBER_ALLOWED_CHARS_REGEXP = /[0-9\.]+/;
given_cur_input.addEventListener("keypress", event => {
  if (!NUMBER_ALLOWED_CHARS_REGEXP.test(event.key)) {
    event.preventDefault();
  }
});
taken_cur_input.addEventListener("keypress", event => {
    if (!NUMBER_ALLOWED_CHARS_REGEXP.test(event.key)) {
      event.preventDefault();
    }
  });


fetch(`/api/get_currency_list`)
.then(response => response.json())
.then(json => {
    Object.entries(json['currencies']).forEach(([key, value]) => {
        const opt_given = document.createElement('option');
        const opt_taken = document.createElement('option');
        opt_given.value = key;
        opt_given.innerHTML = value;
        given_cur_select.appendChild(opt_given);
        opt_taken.value = key;
        opt_taken.innerHTML = value;
        if (key === 'uah') {
            opt_taken.selected = "selected"
        }
        taken_cur_select.appendChild(opt_taken);
      });

    fetch(`/api/get_rate/btc/uah`)
    .then(response => response.json())
    .then(json => {
        main_rate = json['result']['rate'];
        rate_message.innerHTML = `Курс ${main_rate}`;
        given_cur_input.value = 1;
        taken_cur_input.value = given_cur_input.value * main_rate;
    })
    .catch(() => {
        rate_message.innerHTML = `Не могу подгрузить курсы...`;
    });
})
.catch(() => {
    rate_message.innerHTML = `Не могу подгрузить валюты...`;
});


function ckeckCurrencyPair() {
    let given_cur = document.getElementById("given-cur-select").value; 
    let taken_cur = document.getElementById("taken-cur-select").value; 
    let cur_pair = given_cur + '_' + taken_cur;
    if (avaliable_pairs.includes(cur_pair)) {
        given_cur_input.disabled = false;
        taken_cur_input.disabled = false;  
        rate_message.innerHTML = `Загрузка курса...`;
        fetch(`/api/get_rate/${given_cur}/${taken_cur}`)
            .then(response => response.json())
            .then(json => {
                main_rate = json['result']['rate'];
                rate_message.innerHTML = `Курс ${main_rate}`;
                taken_cur_input.value = given_cur_input.value * main_rate;
            })
            .catch(() => {
                rate_message.innerHTML = `Что-то пошло не так...`;
              });
    } else {
        given_cur_input.disabled = true;
        taken_cur_input.disabled = true;
        rate_message.innerHTML = `Данная валютная пара не доступна`;
    }
}

function setTakenCurQnty() {
    taken_cur_value = given_cur_input.value * main_rate;
    taken_cur_input.value = taken_cur_value;
}
function setGivenCurQnty() {
    given_cur_value = taken_cur_input.value / main_rate;
    given_cur_input.value = given_cur_value;
}
let Main = {
    "draw_form_crypto": function(resp_obj){
           return  `<div class="form-group row">
                <label class="col-4 col-form-label" for="">Вы отдаете:</label>
                <div class="col-8">
                    ${resp_obj['amount']}&nbsp;${resp_obj['given_cur']}
                </div>
              </div>
              <div class="form-group row">
                <label for="text1" class="col-4 col-form-label">Вы получаете:</label>
                <div class="col-8">
                    ${resp_obj['taken_amount']}&nbsp;${resp_obj['taken_cur']}
                </div>
              </div>
              <div class="form-group row">
                <label for="text" class="col-4 col-form-label">Укажите адрес кошелька ${resp_obj['taken_cur']}</label>
                <div class="col-8">
                  <div class="input-group">
                    <input id="payment-details" name="text" placeholder="адрес валюты" type="text" class="form-control">
                  </div>
                </div>
              </div>
                <div class="form-group row">
                <div class="col-2">
                      <button  class="btn btn-info">Отменить</button>
                    </div>
                    <div class="offset-8 col-2">
                      <button onclick="sendPaymentDetails(event)" class="btn btn-success">Отправить</button>
                    </div>
                </div>
              `


    },
    "draw_form": function(resp_obj){

        return  `<div class="form-group row">
                <label class="col-4 col-form-label" for="">Вы отдаете:</label>
                <div class="col-8">
                    ${resp_obj['amount']}&nbsp;${resp_obj['given_cur']}
                </div>
              </div>
              <div class="form-group row">
                <label for="text1" class="col-4 col-form-label">Вы получаете:</label>
                <div class="col-8">
                    ${resp_obj['taken_amount']}&nbsp;${resp_obj['taken_cur']}
                </div>
              </div>
              <div class="form-group row">
                <label for="text" class="col-4 col-form-label">Укажите номер карты</label>
                <div class="col-8">
                  <div class="input-group">
                    <input id="payment-details" name="text" placeholder="номер карты получения средства" type="text" class="form-control">
                  </div>
                </div>
              </div>
                <div class="form-group row">
                <div class="col-2">
                      <button  class="btn btn-info">Отменить</button>
                    </div>
                    <div class="offset-6 col-2">
                      <button onclick="sendPaymentDetails(event)" class="btn btn-success">Отправить</button>
                    </div>
                </div>
              `

    }



}



document.getElementById("btn-exchange").addEventListener("click", function(event){
    event.preventDefault()
    let given_cur = document.getElementById("given-cur-select").value; 
    let taken_cur = document.getElementById("taken-cur-select").value; 
    let cur_pair = given_cur + '_' + taken_cur;
    let modal = new bootstrap.Modal(document.getElementById('exchange-modal'));

    if (avaliable_pairs.includes(cur_pair) && given_cur_input.value > 0) {
        let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        let given_amount = given_cur_input.value;
        fetch('/api/create_exchange_request/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ 
                'given_cur': given_cur,
                'amount': given_amount,
                'rate': main_rate,
                'taken_cur': taken_cur
             })
        })
        .then(response => response.json())
        .then(json => {

            let message_box = document.getElementById("exchange-modal-body");
            let message_box_title = document.getElementById("exchange-modal-title");
            if(json['response']['is_expired'] == 'true') {
                message_box.innerHTML = `<p>${json['response']['message_to_user']}</p>`;
                ckeckCurrencyPair();
                modal.show();
            } else {
                ///!!!!! TODO remove this from here
                // TODO also
                message_box_title.innerHTML = json['response']['message_to_user'];
                if (json['response']['taken_cur'] == 'uah') {
                    message_box.innerHTML = Main.draw_form(json["response"]);
                } else {
                    message_box.innerHTML = Main.draw_form_crypto(json["response"]);
                }
                ckeckCurrencyPair();
                modal.show();
            }
        })
        .catch(() => {
            let message_box = document.getElementById("exchange-modal-body");
            message_box.innerHTML = `Что-то пошло не так...`;
            modal.show();
        });
    } else {
        let message_box = document.getElementById("exchange-modal-body");
        message_box.innerHTML = '<h5 class="text-center">Вы указали неверные данные!</h5>';
        modal.show();
    }
  });

function sendPaymentDetails(e) {
    e.preventDefault();
    let payment_details = document.getElementById("payment-details").value;
    let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch('/api/create_invoice/', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 
            'payment_details': payment_details,
         })
    })
    .then(response => response.json())
    .then(json => {
        let message_box = document.getElementById("exchange-modal-body");
        message_box.innerHTML = `
        <h5>${json['response']['message']}</h5><br>
        <p>Вам необходимо перечислить <strong>${json['response']['amount']} ${json['response']['given_cur']}</strong> по следующим реквизитам <strong>${json['response']['payment_details_give']}</strong></p><br/>
        <a href="/invoices/${json['response']['invoice_id']}">Страница для отслеживания деталей сделки</a><br/>
        `;
    })
    .catch(() => {
        console.log('some error')
    });
}
