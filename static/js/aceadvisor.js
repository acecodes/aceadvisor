var AceAdvisor = (function() {
    $(document).ready(function() {
        $('.bloomberg').hide();
        $('#bloomberg1').show();
        $('#selectField-bloomberg').change(function() {
            $('.bloomberg').hide();
            $('#' + $(this).val()).show();
        });
    });

    $(document).ready(function() {
        $('.stocks').hide();
        $('#stocks1').show();
        $('#selectField-stocks').change(function() {
            $('.stocks').hide();
            $('#' + $(this).val()).show();
        });
    });

    $('#headlines').click(function() {
        $('#top').toggle('slow', function() {});
    });

    $('#markets').click(function() {
        $('#middle').toggle('slow', function() {});
    });

    $('#screener').click(function() {
        $('#bottom').toggle('slow', function() {});
    });

    // $( '#options' ).click(function() {
    //   $( '#options_area' ).toggle( 'slow', function() {
    //   });
    // });

    $('.alert-box').click(function() {
        $('.alert-box').toggle('slow', function() {});
    });
})();