// Change script for markets box
$(document).ready(function () {
    $('.bloomberg').hide();
    $('#bloomberg1').show();
    $('#selectField-bloomberg').change(function () {
        $('.bloomberg').hide();
        $('#'+$(this).val()).show();
    });
});

$(document).ready(function () {
    $('.stocks').hide();
    $('#stocks1').show();
    $('#selectField-stocks').change(function () {
        $('.stocks').hide();
        $('#'+$(this).val()).show();
    });
});

