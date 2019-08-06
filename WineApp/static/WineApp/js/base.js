try {
    window.data_py = JSON.parse(document.getElementById('data_js').textContent);
} catch (e) {
    window.data_py = {}
}

$('document').ready(function () {
    const scrollbars = [];
    $('.scroll-y').each(function () {
        scrollbars.push(new PerfectScrollbar($(this)[0], {
            minScrollbarLength: 20,
            suppressScrollX: true
        }));
    });
    $(window).resize(() => {
        scrollbars.forEach((scroll) => scroll.update());
    });


    $('.chart, .no-scroll-propagation').on('DOMMouseScroll mousewheel', function (ev) {
        ev.stopPropagation();
        ev.preventDefault();
        ev.returnValue = false;
        return false;
    });


});