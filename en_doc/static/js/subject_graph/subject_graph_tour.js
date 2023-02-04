function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: " در این پنل با آپلود فایل «گراف موضوعات» می‌توانید گراف مربوطه را مشاهده نمایید."
    }, {
        element: document.querySelector('#file_input_btn'),
        intro: "فایل مورد نظر خود را از این قسمت انتخاب نمایید."

    },{ element: document.querySelector('#load_sample'),
        intro: "فایل نمونه را از این قسمت انتخاب نمایید."
    },
        { element: document.querySelector('#graph_type'),
        intro: "نوع گراف را از این قسمت انتخاب نمایید."
    },
        {
        element: document.querySelector('#graph_show'),
        intro: "با کلیک روی این گزینه گراف موضوعات نمایش داده می‌شود."
    }, {
        element: document.querySelector('#advanced_view_tab'),
        intro: "در این تب می‌توانید گراف حاصل را مشاهده نمایید."
    }]
}).start();


}
