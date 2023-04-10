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

fetch(`/api/get_rate/btc/uah`)
.then(response => response.json())
.then(json => {
    main_rate = json['result']['rate'];
    rate_message.innerHTML = `Курс ${main_rate}`;
    given_cur_input.value = 1;
    taken_cur_input.value = given_cur_input.value * main_rate;
})
.catch(() => {
    rate_message.innerHTML = `Что-то пошло не так...`;
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

function onlyNumberKey(evt) {
    var ASCIICode = (evt.which) ? evt.which : evt.keyCode
    if (ASCIICode > 31 && (ASCIICode < 48 || ASCIICode > 57))
        return false;
    return true;
}
