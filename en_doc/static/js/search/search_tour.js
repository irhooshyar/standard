function showTour(){
    document.getElementById("advanced_fields").classList.add("show");
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "در این پنل می‌توانید با وارد کردن یک یا چند کلیدواژه، اسناد متناظر با کلیدواژگان را جستجو نمایید. امکان پساپردازش نتایج نیز در این پنل وجود دارد."
    },
        {
        element: document.querySelector('#country'),
        intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید."
    },
        {
        element: document.querySelector('#SearchBox'),
        intro: "کلیدواژه‌های مورد نظر خود را در اینجا وارد نمایید."
    }, {
        element: document.querySelector('#advanced_search'),
        intro: "برای استفاده از جستجوی پیشرفته بر روی این دکمه کلیک نمایید."
    },{
        element: document.querySelector('#document_search'),
        intro: "برای مشاهده نتیجه جستجو روی این دکمه کلیک نمایید."
    }, {
        element: document.querySelector('#LevelSelect'),
        intro: "برای تعیین سطح سند روی این گزینه کلیک نمایید."
    }, {
        element: document.querySelector('#SubjectSelect'),
        intro: "برای تعیین موضوع سند روی این گزینه کلیک نمایید."
    }, {
        element: document.querySelector('#TypeSelect'),
        intro: "برای تعیین نوع سند روی این گزینه کلیک نمایید."
    }
    , {
        element: document.querySelector('#ApprovalReferences'),
        intro: "برای تعیین مرجع تصویب سند روی این گزینه کلیک نمایید."

    }, {
        element: document.querySelector('#YearFrom'),
        intro: "برای تعیین محدوده سال تصویب سند بر روی این گزینه کلیک نمایید."

        }, {
        element: document.querySelector('#YearTo'),
        intro: "برای تعیین محدوده سال تصویب سند بر روی این گزینه کلیک نمایید."

    },  {
        element: document.querySelector('#WhereSelect'),
        intro: "برای تعیین محل جستجوی سند گزینه‌ای را انتخاب نمایید."

    },  {
        element: document.querySelector('#SearchTypeSelect'),
        intro: "برای تعیین نوع جستجو در اسناد گزینه‌ای را انتخاب نمایید. اگر عبارت مورد نظر شما «قانون و مقررات» می‌باشد، با انتخاب نوع جستجوی «Exact» دقیقا اسنادی نمایش داده خواهند شد که شامل این کلمات، به همین صورت نوشته شده باشند. با انتخاب «OR» اسنادی نمایش داده می‌شوند که یا کلمه قانون، یا کلمه مقررات و یا هردو را داشته باشند. و اگر نوع جستجو «And» باشد اسنادی نمایش داده می‌شوند که شامل هم قانون و هم مقررات باشند."
    },  {
        element: document.querySelector('#search_result_tab'),
        intro: "نتایج جستجو با توجه به المان‌های جستجویی  تعیین شده توسط کاربر، در این تب ارائه میشوند. کاربر امکان مرتب‌سازی نتایج بر اساس ستون‌های مختلف را نیز داراست."

    },{
        element: document.querySelector('#bar_chart_info_tab'),
        intro: "تحلیل‌های نموداری مستندات ظاهر شده در نتیجه جستجو، در این تب ارائه می‌شوند."

    },{
        element: document.querySelector('#document_graph_tab'),
        intro: "گراف ارجاعات میان اسناد ظاهر شده در نتیجه جستجو، در این تب ارائه می‌شوند."

    },{
        element: document.querySelector('#ExportExcel'),
        intro: "برای دانلود اسامی اسناد و اطلاعات جانبی آن‌ها در قالب اکسل، روی این گزینه کلیک نمایید."

    },{
        element: document.querySelector('#DownloadBtn'),
        intro: "برای دانلود متن اسناد ظاهر شده در نتیجه جستجو، روی این گزینه کلیک نمایید."

    }, ]
}).start();


}
