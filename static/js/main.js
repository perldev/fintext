let avaliable_pairs = [
    'btc_uah',
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
            message_box.innerHTML = `<h5>Ответ от джанго</h5><br>
            <p>Вы отдаете ${json['response']['amount']} ${json['response']['given_cur']}</p><br>
            <p>Вы получаете: ${json['response']['taken_amount']} ${json['response']['taken_cur']}</p>`;
            modal.show();
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


