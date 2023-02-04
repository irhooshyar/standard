function showTour() {
  introJs()
    .setOptions({
      tooltipClass: "customTooltip",
      nextLabel: "بعدی",
      prevLabel: "قبلی",
      doneLabel: "اتمام",
      showProgress: false,
      steps: [
        {
          element: document.querySelector("#start"),
          intro:
            "در این پنل می‌توانید با انتخاب کشور و تایپ دو کلیدواژه مختلف، اطلاعات آماری مربوط به اسناد حاوی دقیقا این دو کلیدواژه را بررسی نمایید.",
        },
        {
          element: document.querySelector("#country"),
          intro: "مجموعه سند مورد نظر خود را از این قسمت انتخاب نمایید.",
        },
        {
          element: document.querySelector('#SearchBox1'),
          intro: "کلیدواژه‌های اول مورد نظر خود را در اینجا وارد نمایید."
        },
        {
          element: document.querySelector('#SearchBox2'),
          intro: "کلیدواژه‌های دوم مورد نظر خود را در اینجا وارد نمایید."
        },
        {
          element: document.querySelector('#document_search'),
          intro: "با کلیک روی این گزینه اسناد متناظر با هر کدام از کلیدواژه های وارد شده، در کشور انتخاب شده ارائه خواهند شد."
        },
          {
            element: document.querySelector('#multiple_terms_tab'),
            intro:"در این تب،اسناد حاوی کلیدواژه‌های انتخاب شده نمایش داده می‌شود و همچنین می‌توانید کلیدواژه های موردنظر را در متن اسناد مشاهده نمایید."
          },
        {
          element: document.querySelector("#bar_chart_info_tab"),
          intro:
            "در این تب، اطلاعاتی در مورد اسناد حاوی لغات موردنظر در قالب نمودارها ارائه می شود.",
        },
          {
        element: document.querySelector('#ExportExcel'),
        intro: "با کلیک روی این گزینه امکان دانلود اسامی و اطلاعات جانبی مربوط به اسناد حاصل از جستجو را خواهید داشت."

        },
          {
        element: document.querySelector('#DownloadBtn'),
        intro: "با کلیک روی این گزینه امکان دانلود اسناد حاصل از جستجو را خواهید داشت."

    }
      ],
    })
    .start();
}
