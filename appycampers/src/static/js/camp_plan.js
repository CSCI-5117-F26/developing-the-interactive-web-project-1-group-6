(function () {
    document.querySelectorAll('.site-camp_plan form').forEach((form) => {
        form.addEventListener('submit', (event) => {
            event.preventDefault();
        });
    });
})();
