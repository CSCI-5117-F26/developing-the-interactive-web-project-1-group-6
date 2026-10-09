// Adapted from https://pure-css.github.io/layouts/tucked-menu-vertical/
(function (window, document) {
    var menu = document.getElementById('menu'),
        rollBack;

    function toggleHorizontal() {
        menu.classList.remove('closing');
        [].forEach.call(
            menu.querySelectorAll('.custom-can-transform'),
            function (el) {
                el.classList.toggle('pure-menu-horizontal');
            }
        );
    }

    function toggleMenu() {
        // set timeout so that the panel has a chance to roll up
        // before the menu switches states
        if (menu.classList.contains('open')) {
            menu.classList.add('closing');
            rollBack = setTimeout(toggleHorizontal, 250);
        } else {
            if (menu.classList.contains('closing')) {
                clearTimeout(rollBack);
                menu.classList.remove('closing');
            } else {
                toggleHorizontal();
            }
        }
        menu.classList.toggle('open');
        document.getElementById('toggle').classList.toggle('x');
    }

    function closeMenu() {
        if (menu.classList.contains('open')) {
            toggleMenu();
        }
    }

    document.getElementById('toggle').addEventListener('click', function (e) {
        toggleMenu();
        e.preventDefault();
    });

    window.addEventListener('resize', closeMenu);
    window.addEventListener('orientationchange', closeMenu);
})(window, document);