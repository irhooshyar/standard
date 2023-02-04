$('.color_picker').on('change', function() {
    $(this).next('span').css('color', $(this).val());
});