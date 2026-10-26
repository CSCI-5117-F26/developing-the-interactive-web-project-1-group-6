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
})();