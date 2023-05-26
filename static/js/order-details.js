
function getStatus() {
    fetch(`/api/get_order_status/116`)
    .then(response => response.json())
    .then(response => {
        let counter = 1;
        errorStatuses = ['expired', 'canceled', 'aml_failed', 'failed']
        for (const key in response) {
            let step = document.getElementById(`step-${counter}`)
            step.classList.remove("completed")
            step.classList.remove("failed")
            if ((response[key]) === 'processed') {
                step.classList.add("completed")
            };
            let stepIcon = document.getElementById(`icon-step-${counter}`)
            if (counter == 1){
                if ((response[key]) === 'wait') {
                    stepIcon.innerHTML = '<i class="bi bi-clock-history"></i>'
                } else if ((response[key]) === 'processed') {
                    stepIcon.innerHTML = '<i class="bi bi-check-lg"></i>'
                } else if (errorStatuses.includes(response[key])) {
                    step.classList.add("failed")
                    stepIcon.innerHTML = '<i class="bi bi-x-circle"></i>'
                };
            } else if (counter !== 5) {
                if ((response[key]) === 'wait') {
                    stepIcon.innerHTML = '<i class="bi bi-dot"></i>'
                } else if ((response[key]) === 'processing') {
                    stepIcon.innerHTML = '<i class="bi bi-clock-history"></i>'
                } else if ((response[key]) === 'processed') {
                    stepIcon.innerHTML = '<i class="bi bi-check-lg"></i>'
                } else if (errorStatuses.includes(response[key])) {
                    step.classList.add("failed")
                    stepIcon.innerHTML = '<i class="bi bi-x-circle"></i>'
                };
            } else {
                if ((response[key]) === 'processing') {
                    if (response['payment2client'] == 'processed') {
                        stepIcon.innerHTML = '<i class="bi bi-clock-history"></i>'
                    } else {
                        stepIcon.innerHTML = '<i class="bi bi-dot"></i>'
                    }
                } else if (errorStatuses.includes(response[key])) {
                    step.classList.add("failed")
                    stepIcon.innerHTML = '<i class="bi bi-x-circle"></i>'
                } else {
                    stepIcon.innerHTML = '<i class="bi bi-check-lg"></i>'
                };
            }
            counter += 1;
        }
    })
    .catch(() => {
        console.log('error')
    });
};

window.onload = getStatus;