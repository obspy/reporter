$(function(){
    var shiftWindow = function() { scrollBy(0, -90) };
    if (location.hash) shiftWindow();
    window.addEventListener("hashchange", shiftWindow);
    $(".twentytwenty-container").twentytwenty();
});
