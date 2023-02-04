function showTour(){
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'next',
    prevLabel: 'previous',
    doneLabel: 'finish',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "In this panel, by selecting an approval, you can view its related information in the form of different tabs."
    }, {
        element: document.querySelector('#country'),
        intro: "Choose your desired document collection from this section."
    },{
        element: document.querySelector('#document_select'),
        intro: "Choose the desired document from this section."
    },{
        element: document.querySelector('#document_search'),
        intro: "By clicking on this option, you can see the text of the selected document."
    }, {
        element: document.querySelector('#document_download'),
        intro: "By clicking on this option, you can download the selected document in PDF or TXT format."
    }, {
        element: document.querySelector('#doc_info_tab'),
        intro: "In this tab, the statistical information of the document is displayed."
    }, {
        element: document.querySelector('#def_keywords_tab'),
        intro: "In this tab, definitions, general definitions, terms and keywords of the document are displayed."
    }, {
        element: document.querySelector('#multiple_terms_tab'),
        intro: "In this tab, the important phrase of 2 or 3 words in the document is displayed. You can also confirm, delete or add your desired phrase."
    }, {
        element: document.querySelector('#reference_tab'),
        intro: "In this tab, references in the document and documents referring to the selected document are displayed."
    }
    , {
        element: document.querySelector('#subject_analysis_tab'),
        intro: "In this tab, the topic distribution chart of the document is displayed. Also, the keywords of the document are displayed separately for each topic."
    }, {
        element: document.querySelector('#actor_analysis_tab'),
        intro: "In this tab, the information related to the actors of the document is displayed. You can see more information by clicking on the charts."
    }]
}).start();


}
