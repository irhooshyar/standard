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
        intro: "در این پنل می‌توانید به انطباق موضوعی یک پیش‌نویس  و اسناد موجود در مخزن اطلاعاتی بپردازید."
    }, {
        element: document.querySelector('#country'),
        intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید."
    }, {
        element: document.querySelector('#KeywordsBox'),
        intro: "کلیدواژگان متناظر با پیش‌نویس مدنظر را در این قسمت  وارد نمایید. از «/» به عنوان جداکننده کلیدواژگان بهره بجویید. به عنوان نمونه: «دولت الکترونیک/اقدام» "
    }, {
        element: document.querySelector('#advanced_search'),
        intro: "با کلیک روی این گزینه، تنظیمات پیشرفته را برای انطباق موضوعی تعیین نمایید."
    }, {
        element: document.querySelector('#document_search'),
        intro: "با کلیک روی این گزینه اسناد متناظر با کلیدواژگان و پیش‌نویس ارائه خواهند شد."
    }, {
        element: document.querySelector('#file_input_btn'),
        intro: "با کلیک روی این گزینه فایل پیش‌نویس  مدنظر را آپلود نمایید. درحال حاضر تنها از فایل‌های word پشتیبانی می‌شود."
    },{
        element: document.querySelector('#LevelSelect'),
        intro: "در این قسمت سطح اسنادی که مایل به جستجوی کلیدواژگان در آن‌ها هستید، تعیین می‌شود."
    },{
        element: document.querySelector('#SubjectSelect'),
        intro: "در این قسمت موضوع اسنادی که مایل به جستجوی کلیدواژگان در آن‌ها هستید، تعیین می‌شود."
    },{
        element: document.querySelector('#TypeSelect'),
        intro: "در این قسمت نوع اسنادی که مایل به جستجوی کلیدواژگان در آن‌ها هستید، تعیین می‌شود."
    }, {
        element: document.querySelector('#ApprovalReferences'),
        intro: "در این قسمت مرجع تصویب اسنادی که مایل به جستجوی کلیدواژگان در آن‌ها هستید، تعیین می‌شود."
    }, {
        element: document.querySelector('#YearFrom'),
        intro: "در این قسمت محدوده سال تصویب اسنادی که مایل به جستجوی کلیدواژگان در آن‌ها هستید، تعیین می‌شود."
    }, {
        element: document.querySelector('#YearTo'),
        intro: "در این قسمت محدوده سال تصویب اسنادی که مایل به جستجوی کلیدواژگان در آن‌ها هستید، تعیین می‌شود."
    }
    , {
        element: document.querySelector('#WhereSelect'),
        intro: "در این قسمت محل جستجوی کلیدواژگان تعیین می‌شود."
    }, {
        element: document.querySelector('#search_result_tab'),
        intro: "با توجه به موارد تعیین شده در گزینه های جستجو (نوع کشور، کلیدواژگان و موارد دیگر)، در این تب اسناد مرتبط با گزینه‌ها لیست میشوند. کاربر امکان مرتب سازی نتایج بر اساس یک ستون خاص را دارا می‌باشد."
    },{
        element: document.querySelector('#actors_graph_tab'),
        intro: "در این تب، اطلاعات مربوط به کنش‌گران سند (متولیان اجرا، همکاران و دارای صلاحیت اختیاری) نمایش داده شده‌است. با کلیک روی نمودارها می‌توانید اطلاعات بیش‌تری را مشاهده نمایید."
    },{
        element: document.querySelector('#reference_graph_tab'),
        intro: "در این تب اطلاعات مربوط به گراف ارجاعات با محوریت سند پیش‌نویس، نمایش داده می‌شود."
    },{
        element: document.querySelector('#confilict_analysis_tab'),
        intro: "در این تب تناقضات و تشابهات میان پیش‌نویس و اسناد پیدا شده، نمایش داده می‌شود."
    },{
        element: document.querySelector('#ExportExcel'),
        intro: "با کلیک روی این گزینه امکان دانلود اسامی و اطلاعات جانبی مربوط به اسناد حاصل از جستجو را خواهید داشت."
    },{
        element: document.querySelector('#DownloadBtn'),
        intro: "با کلیک روی این گزینه امکان دانلود اسناد حاصل از جستجو را خواهید داشت."
    }]
}).start();


}
