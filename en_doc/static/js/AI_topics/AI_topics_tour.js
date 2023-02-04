function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'بعدی',
    prevLabel: 'قبلی',
    doneLabel: 'اتمام',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "در این پنل می‌توانید موضوعات اسناد را به روش latent dirichlet allocation بررسی کنید."
    }, {
        element: document.querySelector('#country'),
        intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید."
    }, {
        element: document.querySelector('#document_search'),
        intro: "با کلیک روی این گزینه کلیدواژه های مختلف به صورت گروه های 10 تایی ارائه خواهند شد."
    },{
        element: document.querySelector('#search_result_tab'),
        intro: "در این تب دسته های 10 تایی کلید واژه ها آورده شده است. با کلیک روی گزینه مشاهده اسناد هر دسته از کلمات، میتوانید اسناد متناظر را ببینید."
    },]
}).start();


}
