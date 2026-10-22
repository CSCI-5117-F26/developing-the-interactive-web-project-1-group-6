(function () {
    const page = document.querySelector('.site-camp_plan');
    if (!page) return;

    page.querySelectorAll('form[data-confirm]').forEach((form) => {
        form.addEventListener('submit', (event) => {
            if (!window.confirm(form.dataset.confirm)) event.preventDefault();
        });
    });

    function toggle(button, panel, open) {
        const show = open === undefined ? panel.hidden : open;
        panel.hidden = !show;
        button.setAttribute('aria-expanded', String(show));
        return show;
    }

    // Claim form
    const claimButton = document.getElementById('claim-button');
    const claimForm = document.getElementById('claim-form');
    if (claimButton && claimForm) {
        const select = document.getElementById('claim-item');
        const quantity = document.getElementById('claim-quantity');
        claimButton.addEventListener('click', () => {
            if (toggle(claimButton, claimForm)) select.focus();
        });
        document.getElementById('cancel-claim-button').addEventListener('click', () => {
            claimForm.reset();
            toggle(claimButton, claimForm, false);
            claimButton.focus();
        });
        select.addEventListener('change', () => {
            const option = select.selectedOptions[0];
            if (!option || !option.value) {
                quantity.removeAttribute('max');
                return;
            }
            quantity.max = option.dataset.max;
            quantity.value = Number(option.dataset.mine) || 1;
        });
    }

    // Expense breakdown
    const breakdownButton = document.getElementById('expense-breakdown-button');
    const breakdown = document.getElementById('expense-breakdown');
    if (breakdownButton && breakdown) {
        breakdownButton.addEventListener('click', () => {
            const open = toggle(breakdownButton, breakdown);
            breakdownButton.textContent = open ? 'Hide full breakdown' : 'View full breakdown';
        });
    }

    //  edit for your own extra items
    page.querySelectorAll('.edit-item-button').forEach((button) => {
        const row = button.closest('tr');
        const form = row.querySelector('.edit-item-form');
        const name = row.querySelector('.item-name');
        button.addEventListener('click', () => {
            form.hidden = false;
            name.hidden = true;
            button.hidden = true;
            form.querySelector('input[name="item_name"]').focus();
        });
        form.querySelector('.edit-item-cancel').addEventListener('click', () => {
            form.reset();
            form.hidden = true;
            name.hidden = false;
            button.hidden = false;
            button.focus();
        });
    });

    // Split of expenses
    const expenseForm = document.getElementById('expense-form');
    if (expenseForm) {
        expenseForm.addEventListener('submit', (event) => {
            const boxes = expenseForm.querySelectorAll('input[name="participants"]');
            if (boxes.length && ![...boxes].some((b) => b.checked)) {
                event.preventDefault();
                boxes[0].setCustomValidity('Choose at least one camper to split with.');
                boxes[0].reportValidity();
            }
        });
        expenseForm.querySelectorAll('input[name="participants"]').forEach((box) => {
            box.addEventListener('change', () => box.form.querySelector('input[name="participants"]').setCustomValidity(''));
        });
    }

    // format timestamps
    page.querySelectorAll('.camp-messages time[datetime]').forEach((el) => {
        const when = new Date(el.getAttribute('datetime'));
        if (!isNaN(when)) {
            el.textContent = when.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
        }
    });

    // the messages
    const messages = document.getElementById('camp-messages');
    if (messages && location.hash === '#discussion') messages.lastElementChild?.scrollIntoView({ block: 'nearest' });
})();
