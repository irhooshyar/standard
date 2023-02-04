function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "در این پنل می‌توانید با انتخاب یک مصوبه، اطلاعات مربوط به آن را در قالب تب‌های مختلف مشاهده نمایید."
    }, {
        element: document.querySelector('#country'),
        intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید."
    },{
        element: document.querySelector('#document_select'),
        intro: "سند مورد نظر خود را از این قسمت انتخاب نمایید."
    },{
        element: document.querySelector('#document_search'),
        intro: "با کلیک کردن بر روی این گزینه، می‌توانید متن سند انتخابی را مشاهده نمایید."
    }, {
        element: document.querySelector('#document_download'),
        intro: "با کلیک کردن بر روی این گزینه، می‌توانید  سند انتخابی را دانلود نمایید."
    }, {
        element: document.querySelector('#doc_info_tab'),
        intro: "در این تب اطلاعات آماری سند نمایش داده می‌شود."
    }, {
        element: document.querySelector('#def_keywords_tab'),
        intro: "در این تب تعاریف، تعاریف کلی، اصطلاحات و کلیدواژه‌های  سند نمایش داده می‌شود."
    }, {
        element: document.querySelector('#multiple_terms_tab'),
        intro: "در این تب، عبارت مهم 2 یا 3 کلمه‌ای موجود در سند نمایش داده می‌شود. همچنین می‌توانید عبارت موردنظر خود را تائید، حذف  و یا اضافه نمایید."
    }, {
        element: document.querySelector('#reference_tab'),
        intro: "در این تب ارجاعات موجود در سند و اسناد ارجاع‌ داده به سند انتخابی، نمایش داده می‌شود."
    }
    , {
        element: document.querySelector('#subject_analysis_tab'),
        intro: "در این تب نمودار توزیع موضوعی سند نمایش داده می‌شود. همچنین کلیدواژه‌های سند به تفکیک هر موضوع نمایش داده شده‌است."
    }, {
        element: document.querySelector('#actor_analysis_tab'),
        intro: "در این تب اطلاعات مربوط به کنش‌گران سند (متولیان اجرا، همکاران و دارای صلاحیت اختیاری) نمایش داده شده‌است. با کلیک روی نمودارها می‌توانید اطلاعات بیش‌تری را مشاهده نمایید."
    }, {
        element: document.querySelector('#user_comments'),
        intro: "در این تب می‌توانید، نظرات خود را در مورد سند انتخابی ثبت کنید. همچنین می‌توانید نظرات قبلی خود، در مورد اسناد مختلف را مشاهده نمایید."
    }, {
        element: document.querySelector('#user_notes'),
        intro: "در این تب می‌توانید، یادداشت‌های شخصی خود را در مورد سند انتخابی ثبت کنید."
    }]
}).start();


}
