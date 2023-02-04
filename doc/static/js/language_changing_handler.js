$(document).ready(function () {
    $('select#language').on('change', function (e) {

        selected_language = this.value;
        current_url = window.location.href;
        if (selected_language == 'Iran') {
            window.location = "{% url 'index' %}";
        }else if (selected_language == 'Russia'){
            window.location = "{% url 'ru_index' %}";
        }

    })
});

