function setLang() {
  let selected_lang = document.getElementById("lang-select").value;
  let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  fetch('/api/set-lang/', {
      method: 'POST',
      headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
      },
      body: JSON.stringify({ 
          'lang': selected_lang,
       })
  })
  .catch(() => {});
  location.reload();
}

let langJsDict = JSON.parse(document.getElementById('langJsDict').textContent)
const langData = document.currentScript.dataset;

let avaliable_pairs = [];

let fiat_currency = {"uah":1, "eur":1, "usd":1, "uah безнал":1}
let main_rate = 0;
let rate_message = document.getElementById("rate-message");
rate_message.innerHTML = `${langJsDict['load_rate'][langData.lang]}`;
let given_cur_input = document.getElementById("given-cur-input");
let taken_cur_input = document.getElementById("taken-cur-input");
let given_cur_select = document.getElementById("given-cur-select");
let taken_cur_select = document.getElementById("taken-cur-select");
let spinner = document.getElementById("loading");

let ifFiat = null;
let cardInput = null;
let errorDiv = null;
let isPaymentDetailsValid = false;

let cashPoints = null;
let cashPointsDiv = null;
let cashPointsSelect = null;


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
const CARD_NUMBER_ALLOWED_CHARS_REGEXP = /[0-9]+/;



function ckeckCurrencyPair() {
    let given_cur = document.getElementById("given-cur-select").value; 
    let taken_cur = document.getElementById("taken-cur-select").value; 
    let cur_pair = given_cur + '_' + taken_cur;
    if (avaliable_pairs.includes(cur_pair)) {
        given_cur_input.disabled = false;
        taken_cur_input.disabled = false;  
        rate_message.innerHTML = `${langJsDict['load_rate'][langData.lang]}`;
        fetch(`/api/get_rate/${given_cur}/${taken_cur}`)
            .then(response => response.json())
            .then(json => {
                main_rate = json['result']['rate'];
                rate_message.innerHTML = `Курс ${main_rate}`;
                taken_cur_input.value = given_cur_input.value * main_rate;
            })
            .catch(() => {
                rate_message.innerHTML = `${langJsDict['smth_wrong'][langData.lang]}`;
              });
    } else {
        given_cur_input.disabled = true;
        taken_cur_input.disabled = true;
        rate_message.innerHTML = `${langJsDict['no_pair'][langData.lang]}`;
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
    "on_load": function(e, cur1, cur2){
        fetch(`/api/get_currency_list`)
        .then(response => response.json())
        .then(json => {
            Object.entries(json['currencies']).forEach(([key, value]) => {
                const opt_given = document.createElement('option');
                const opt_taken = document.createElement('option');
                opt_given.value = key;
                if(opt_given.value == cur1){
                    opt_given.selected = "selected"
                }

                opt_given.innerHTML = value;
                given_cur_select.appendChild(opt_given);
                opt_taken.value = key;
                opt_taken.innerHTML = value;
                if (key === cur2) {
                    opt_taken.selected = "selected"
                }
                taken_cur_select.appendChild(opt_taken);
              });

            fetch(`/api/get_rate/${cur1}/${cur2}`)
            .then(response => response.json())
            .then(json => {
                main_rate = json['result']['rate'];
                rate_message.innerHTML = `Курс ${main_rate}`;
                given_cur_input.value = 1;
                taken_cur_input.value = given_cur_input.value * main_rate;
            })
            .catch(() => {
                rate_message.innerHTML = `${langJsDict['no_rates'][langData.lang]}`;
            });
        })
        .catch(() => {
            rate_message.innerHTML = `${langJsDict['no_currencies'][langData.lang]}`;
        });

    },
    "draw_form_crypto": function(resp_obj){

            let provider_select = '';
            if (resp_obj['taken_cur'] == "usdt") {
              provider_select = `
                <br>
                <div class="form-group row">
                  <label class="col-4 col-form-label">${langJsDict['usdt_net'][langData.lang]}</label>
                  <div class="col-8">
                    <div class="form-check">
                      <input class="form-check-input" type="radio" onclick="selectErc()" name="ercNet" id="ercNet1" checked value="option1" >
                      <label class="form-check-label" for="ercNet1">
                        ERC-20
                      </label>
                    </div>
                    <div class="form-check" >
                      <input class="form-check-input" type="radio" onclick="selectTron()" name="tronNet" id="tronNet1" value="option2">
                      <label class="form-check-label" for="tronNet1">
                        TRON
                      </label>
                    </div>
                  </div>
                </div>
                <br>
              `
            }

            let fiat_payment_select = `
              <br>
              <div class="form-group row">
                <label class="col-4 col-form-label">${langJsDict['payment_way'][langData.lang]}</label>
                <div class="col-8">
                  <div class="form-check" >
                    <input class="form-check-input" type="radio" onclick="selectCard()" name="cardPayment" id="cardPayment" checked value="cardPayment">
                    <label class="form-check-label" for="cardPayment">
                      ${langJsDict['card_pay'][langData.lang]}
                    </label>
                  </div>
                  <div class="form-check">
                    <input class="form-check-input" type="radio" onclick="selectCash()" name="cashPayment" id="cashPayment" value="cashPayment" >
                    <label class="form-check-label" for="cashPayment">
                    ${langJsDict['cash_pay'][langData.lang]}
                    </label>
                  </div>
                </div>
              </div>
              <br>
            `;



           return  `<div class="form-group row">
                <label class="col-4 col-form-label" for="">${langJsDict['you_give'][langData.lang]}</label>
                <div class="col-8">
                    ${resp_obj['amount']}&nbsp;${resp_obj['given_cur']}
                </div>
              </div>
              <div class="form-group row">
                <label for="text1" class="col-4 col-form-label">${langJsDict['you_take'][langData.lang]}</label>
                <div class="col-8">
                    ${resp_obj['taken_amount']}&nbsp;${resp_obj['taken_cur']}
                </div>
              </div>

              ${provider_select}

              <div class="form-group row">
                <label for="text" class="col-4 col-form-label">${langJsDict['wal_adr'][langData.lang]} ${resp_obj['taken_cur']}</label>
                <div class="col-8">
                  <div class="input-group">
                    <input id="payment-details" name="text" placeholder="${langJsDict['cur_adr'][langData.lang]}" type="text" class="form-control">
                  </div>
                  <div id="payment-details-error" class="form-text"></div>
                </div>
              </div>

              ${fiat_payment_select}

              <div class="form-group row" id='cash-points-select-wrapper' style="display:none" >
                <div class="offset-lg-4 col-lg-8 col-12">
                  <select class="form-select" id="cash-points-select" aria-label="${langJsDict['choose_loc'][langData.lang]}">
                  </select>
                </div>
              </div>

              <div class="form-group row">
                  <div class="col-6 text-start">
                    <button  class="btn btn-info">${langJsDict['cancel'][langData.lang]}</button>
                  </div>
                  <div class="col-6 text-end">
                    <button onclick="sendPaymentDetails(event)" class="btn btn-success">${langJsDict['send'][langData.lang]}</button>
                  </div>
              </div>
              `


    },
    "draw_form_cash": function(resp_obj){

        let provider_select = '';
        if (resp_obj['given_cur'] == "usdt") {
          provider_select = `
            <br>
            <div class="form-group row">
              <label class="col-4 col-form-label">${langJsDict['usdt_net'][langData.lang]}</label>
              <div class="col-8">
                <div class="form-check">
                  <input class="form-check-input" type="radio" onclick="selectErc()" name="ercNet" id="ercNet1" checked value="option1" >
                  <label class="form-check-label" for="ercNet1">
                    ERC-20
                  </label>
                </div>
                <div class="form-check" >
                  <input class="form-check-input" type="radio" onclick="selectTron()" name="tronNet" id="tronNet1" value="option2">
                  <label class="form-check-label" for="tronNet1">
                    TRON
                  </label>
                </div>
              </div>
            </div>
            <br>
          `
        }


        return  `<div class="form-group row">
                <label class="col-4 col-form-label" for="">${langJsDict['you_give'][langData.lang]}</label>
                <div class="col-8">
                    ${resp_obj['amount']}&nbsp;${resp_obj['given_cur']}
                </div>
              </div>
              <div class="form-group row">
                <label for="text1" class="col-4 col-form-label">${langJsDict['you_take'][langData.lang]}</label>
                <div class="col-8">
                    ${resp_obj['taken_amount']}&nbsp;${resp_obj['taken_cur']}
                </div>
              </div>

              ${provider_select}


              <br>
              <div id="cashPointsForm" >
                <div class="form-group row">
                  <div class="col-4">${langJsDict['cash_points'][langData.lang]}</div>
                  <div class="col-8" id="cash-points-wrapper">

                  </div>
                </div>
                <div class="form-group row">
                  <div class="col-6 text-start">
                    <button  class="btn btn-info">${langJsDict['cancel'][langData.lang]}</button>
                  </div>
                  <div class="col-6 text-end">
                    <button onclick="sendPaymentDetails(event)" id="btn-send-cash-point" disabled class="btn btn-success">${langJsDict['send'][langData.lang]}</button>
                  </div>
                </div>
              </div>
              `

    },
    "draw_form_card": function(resp_obj){


        let provider_select = '';
        if (resp_obj['given_cur'] == "usdt") {
          provider_select = `
            <br>
            <div class="form-group row">
              <label class="col-4 col-form-label">${langJsDict['usdt_net'][langData.lang]}</label>
              <div class="col-8">
                <div class="form-check">
                  <input class="form-check-input" type="radio" onclick="selectErc()" name="ercNet" id="ercNet1" checked value="option1" >
                  <label class="form-check-label" for="ercNet1">
                    ERC-20
                  </label>
                </div>
                <div class="form-check" >
                  <input class="form-check-input" type="radio" onclick="selectTron()" name="tronNet" id="tronNet1" value="option2">
                  <label class="form-check-label" for="tronNet1">
                    TRON
                  </label>
                </div>
              </div>
            </div>
            <br>
          `
        }
  /*<div class="form-group row">
                  <label for="text1" class="col-4 col-form-label">${langJsDict['get_money_way'][langData.lang]}</label>
                  <div class="col-8">
                    <div class="form-check" id="card-form-check" >
                      <input class="form-check-input" type="radio" onclick="selectCreditCard()" name="creditCard" id="creditCard1" checked value="option1" >
                      <label class="form-check-label" for="creditCard1">
                      ${langJsDict['get_money_card'][langData.lang]}
                      </label>
                    </div>
                    <div class="form-check" >
                      <input class="form-check-input" type="radio" onclick="selectCashPoint()" name="cashPoint" id="cashPoint1" value="option2">
                      <label class="form-check-label" for="cashPoint1">
                      ${langJsDict['get_money_cash'][langData.lang]}
                      </label>
                    </div>
                  </div>
              </div>
              */

        return  `<div class="form-group row">
                <label class="col-4 col-form-label" for="">${langJsDict['you_give'][langData.lang]}</label>
                <div class="col-8">
                    ${resp_obj['amount']}&nbsp;${resp_obj['given_cur']}
                </div>
              </div>
              <div class="form-group row">
                <label for="text1" class="col-4 col-form-label">${langJsDict['you_take'][langData.lang]}</label>
                <div class="col-8">
                    ${resp_obj['taken_amount']}&nbsp;${resp_obj['taken_cur']}
                </div>
              </div>

              ${provider_select}
              <br>
                <div id="creditCardForm" style="display:block">
                <div class="form-group row">
                  <label for="text" class="col-4 col-form-label">${langJsDict['card_num'][langData.lang]}</label>
                  <div class="col-8">
                    <div id="payment-details-error" class="form-text"></div>
                    <div class="input-group">
                      <input id="payment-details" name="text" maxlength="19" oninput="validateCardNumber(value)" onpaste="cardValidationOnPaste()" placeholder="${langJsDict['card_num_plc'][langData.lang]}" type="text" class="form-control">
                    </div>

                  </div>
                </div>
                <br/>
                <div class="form-group row">
                    <div class="col-6 text-start">
                      <button  class="btn btn-info">${langJsDict['cancel'][langData.lang]}</button>
                    </div>
                    <div class="col-6 text-end">
                      <button onclick="sendPaymentDetails(event)" id="btn-send-payment" disabled class="btn btn-success">${langJsDict['send'][langData.lang]}</button>
                    </div>
                </div>
              </div>
              `



    }




}



document.getElementById("btn-exchange").addEventListener("click", function(event){
    event.preventDefault()
    spinner.style.display = 'block';
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
                if (json['response']['taken_cur'] in  fiat_currency ) {
                    if(json['response']['taken_cur'] == "uah безнал"){

                        message_box.innerHTML = Main.draw_form_card(json["response"]);
                        selectCreditCard();
                    }else{
                        message_box.innerHTML = Main.draw_form_cash(json["response"]);
                        selectCashPoint();
                    }



                    cashPoints = JSON.parse(json["response"]["cash_points"]);

                    ifFiat = true;
                    cardInput = document.getElementById("payment-details");
                    cardInput.addEventListener("keypress", event => {
                      if (!CARD_NUMBER_ALLOWED_CHARS_REGEXP.test(event.key)) {
                        event.preventDefault();
                      }
                    });
                    cardInput.addEventListener("input", () => cardInput.value = formatNumber(cardInput.value.replaceAll(" ", "")));
                } else {
                    isPaymentDetailsValid = true;

                    message_box.innerHTML = Main.draw_form_crypto(json["response"]);

                    cashPointsSelect = document.getElementById("cash-points-select");
                    Object.entries(JSON.parse(json["response"]['cash_points'])).forEach(([key, value]) => {
                      const some_option = document.createElement('option');
                      some_option.value = key;
                      some_option.innerHTML = value;
                      cashPointsSelect.appendChild(some_option);
                    });
                }

                errorDiv = document.getElementById("payment-details-error"); 

                ckeckCurrencyPair();
                spinner.style.display = 'none';
                modal.show();
            }
        })
        .catch(() => {
            let message_box = document.getElementById("exchange-modal-body");
            message_box.innerHTML = `${langJsDict['smth_wrong'][langData.lang]}`;
            spinner.style.display = 'none';
            modal.show();
        });
    } else {
        let message_box = document.getElementById("exchange-modal-body");
        message_box.innerHTML = `<h5 class="text-center">${langJsDict['wrong_data'][langData.lang]}</h5>`;
        spinner.style.display = 'none';
        modal.show();
    }
  });

function sendPaymentDetails(e) {
    e.preventDefault();
    spinner.style.display = 'block';
    let pay_details = document.getElementById("payment-details") ? document.getElementById("payment-details").value : null;
    let pay_details_for_cash = document.querySelector('input[name="cashPointInput"]:checked') ? document.querySelector('input[name="cashPointInput"]:checked').value : null;
    let payment_details = null;
    let isCash = false;
    if (pay_details) {
      payment_details = pay_details;
    } else if (pay_details_for_cash) {
      payment_details = pay_details_for_cash;
      isCash = true;
    }

    let usdt_net = null;
    if (document.getElementById("ercNet1")) {
      if (document.querySelector('input[name="ercNet"]:checked')) {
        usdt_net = "erc20"
      } else {
        usdt_net = "tron"
      }
    }

    let fiat_pay_method = null;
    if (document.getElementById("cardPayment")) {
      if (document.querySelector('input[name="cardPayment"]:checked')) {
        fiat_pay_method = "card"
      } else {
        fiat_pay_method = "cash"
      }
    }

    let cash_point = 1;
    if (document.getElementById("cardPayment")) {
      cash_point = document.getElementById("cash-points-select").value; 
    }

    let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch('/api/create_invoice/', {
      method: 'POST',
      headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
      },
      body: JSON.stringify({ 
          'payment_details': payment_details,
          'is_cash': isCash ? '1' : '0',
          'usdt_net': usdt_net,
          'fiat_pay_method': fiat_pay_method,
          'cash_point': cash_point
        })
    })
    .then(response => response.json())
    .then(json => {
        let message_box = document.getElementById("exchange-modal-body");
        if (json['response']['error']) {
          message_box.innerHTML = `
          <h5>${json['response']['error']}</h5><br>
          `;
        } else {
          if (!isCash) {
            let payment_message = null;
            if (json['response']['is_fiat_card'] == 1) {
              payment_message = `
              <p>${langJsDict['mes_part_1'][langData.lang]} <strong>${json['response']['amount']} ${json['response']['given_cur']}</strong> ${langJsDict['mes_part_2'][langData.lang]} <strong>${json['response']['payment_details_give']}</strong></p><br/>
              `
            } else {
              payment_message = `
              <p>${langJsDict['mes2_part_1'][langData.lang]} <strong>${json['response']['amount']} ${json['response']['given_cur']}</strong> ${langJsDict['mes2_part_2'][langData.lang]}<br><strong>${json['response']['payment_details_give']}</strong></p><br/>
              `
            }
            message_box.innerHTML = `
            <h5>${json['response']['message']}</h5><br>
            ${payment_message}
            <a href="/orders/${json['response']['order_id']}">${langJsDict['order_page'][langData.lang]}</a><br/>
            <br/>
            <a href="${json['response']['t_link']}">${langJsDict['t_chat'][langData.lang]}</a>
            `;
          } else {
            message_box.innerHTML = `
            <h5>${json['response']['message']}</h5><br>
            <p>${langJsDict['mes_part_1'][langData.lang]} <strong>${json['response']['amount']} ${json['response']['given_cur']}</strong> ${langJsDict['mes_part_2'][langData.lang]} <strong>${json['response']['payment_details_give']}</strong></p><br/>
            <p>${langJsDict['secret_key'][langData.lang]} <strong>${json['response']['secret_key']}</strong></p>
            <br/>
            <a href="/orders/${json['response']['order_id']}">${langJsDict['order_page'][langData.lang]}</a><br/>
            <br/>
            <a href="${json['response']['t_link']}">${langJsDict['t_chat'][langData.lang]}</a>
            `;
          }

        };
        spinner.style.display = 'none';
    })
    .catch(() => {
        console.log('some error');
        spinner.style.display = 'none';
    });

}

const formatNumber = (number) => number.split("").reduce((seed, next, index) => {
  if (index !== 0 && !(index % 4)) seed += " ";
  return seed + next;
}, "");


// visa 4149499385009483
// master 5168755512651007

// TODO make validation on paste with promise
function cardValidationOnPaste(){
  function someF() {
    var cardNum = document.getElementById('payment-details').value;
    validateCardNumber(cardNum)
  }
  setTimeout(someF, 300)
}

function validateCardNumber(value){
  if(ifFiat) {
    
    if(value.length === 19) {
      var num = value.split(' ').join('');

      const cardArray = num.toString().split("").map((e) => parseInt(e) )
      validlen(cardArray);
      const splitArr =  arrSplit(cardArray)
      const checksum = sumArrDigits(splitArr.arr1).reduce((a, c) => a + c) + splitArr.arr2.reduce((a, c) => a + c);
    
      if(checksum % 10 == 0) {
        const typeValidatorArr = cardArray.slice(0,2)
        const typeValidatorInt = parseInt(typeValidatorArr.join(""))
        
        if (typeValidatorArr[0] == 4){
          var btnSendPayment = document.getElementById('btn-send-payment');
          btnSendPayment.disabled = false;
          return "VISA"
        }else if(typeValidatorInt == 22 || typeValidatorInt == 51 || typeValidatorInt == 52 || typeValidatorInt == 53 || typeValidatorInt == 54){
          var btnSendPayment = document.getElementById('btn-send-payment');
          btnSendPayment.disabled = false;
          return "MASTERCARD";
        }
      } else {
        var btnSendPayment = document.getElementById('btn-send-payment');

        btnSendPayment.disabled = true;
        errorDiv.innerHTML = `Ошибка в номере карты`;
        return null;
      }

    } else {
      errorDiv.innerHTML = ``;
      var btnSendPayment = document.getElementById('btn-send-payment');
      btnSendPayment.disabled = true;
      return null;
    }

  }
}
  
function sumArrDigits(array){
  return array.join("").split("").map(e => parseInt(e))
}

function validlen(arr){
  return  arr.length == 13  || arr.length == 15 || arr.length == 16
}

function arrSplit(cardArray){
  const selectOddValues = cardArray.filter((a,i)=>i%2 === 1);
  const selectEvenValues = cardArray.filter((a,i)=>i%2 === 0);
  let arr1;
  let arr2;
  if (cardArray.length % 2 == 1){
    arr1 = selectOddValues.map(e => e * 2);
    arr2 = selectEvenValues;
  }else {
    arr1 = selectEvenValues.map(e => e * 2);
    arr2 = selectOddValues;
  }
  return {arr1, arr2}
}


// logic of tron/erc select fields
function selectErc() {
  document.getElementById("ercNet1").checked = true;
  document.getElementById("tronNet1").checked = false;
}
function selectTron() {
  document.getElementById("ercNet1").checked = false;
  document.getElementById("tronNet1").checked = true;
}

// logic of cash card select
function selectCard() {
  document.getElementById("cashPayment").checked = false;
  document.getElementById("cardPayment").checked = true;
  document.getElementById("cash-points-select-wrapper").style.display = "none";
}
function selectCash() {
  document.getElementById("cashPayment").checked = true;
  document.getElementById("cardPayment").checked = false;
  document.getElementById("cash-points-select-wrapper").style.display = "block";
}



// logic of payment details select fields.

function selectCreditCard() {
  //document.getElementById("creditCard1").checked = true;
  //document.getElementById("cashPoint1").checked = false;
 // document.getElementById("creditCardForm").style.display = "block";
 // document.getElementById("cashPointsForm").style.display = "none";

  document.getElementById("cash-points-wrapper").innerHTML = ``;
  var btnSendPayment = document.getElementById('btn-send-cash-point');
  btnSendPayment.disabled = true;
}

function selectCashPoint() {
  document.getElementById("cash-points-wrapper").innerHTML = ``
  for (const [key, value] of Object.entries(cashPoints)) {
    document.getElementById("cash-points-wrapper").innerHTML += `
      <div class="form-check">
        <input class="form-check-input" type="radio" name="cashPointInput" onclick="setCashPoint()" id="cashPointInput${key}" value="${key}">
        <label class="form-check-label" for="cashPointInput${key}">
          ${value}
        </label>
      </div>
    `
  }

  //document.getElementById("creditCard1").checked = false;
  //document.getElementById("cashPoint1").checked = true;

  //document.getElementById("creditCardForm").style.display = "none";
  //document.getElementById("cashPointsForm").style.display = "block";
  
}

function setCashPoint() {
  var btnSendPayment = document.getElementById('btn-send-cash-point');
  btnSendPayment.disabled = false;
}




