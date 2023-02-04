function showTour(){
    document.getElementById("advanced_fields").classList.add("show");
    introJs().setOptions({
    tooltipClass: 'customTooltip',
    nextLabel: 'next',
    prevLabel: 'previous',
    doneLabel: 'finish',
    showProgress: false,
    steps: [{
        element: document.querySelector('#start'),
        intro: "In this panel, you can search for documents corresponding to keywords by entering one or more keywords. It is also possible to post-process the results in this panel."
    },
        {
        element: document.querySelector('#country'),
        intro: "Choose your desired document collection from this section."
    },
        {
        element: document.querySelector('#SearchBox'),
        intro: "Enter your desired keywords here."
    }, {
        element: document.querySelector('#advanced_search'),
        intro: "Click on this button to use advanced search."
    },{
        element: document.querySelector('#document_search'),
        intro: "Click on this button to see the search result."
    }, {
        element: document.querySelector('#LevelSelect'),
        intro: "Click on this option to determine the level of the document."
    }, {
        element: document.querySelector('#SubjectSelect'),
        intro: "Click on this option to determine the topic of the document."
    }, {
        element: document.querySelector('#TypeSelect'),
        intro: "Click on this option to specify the type of document."
    }
    , {
        element: document.querySelector('#ApprovalReferences'),
        intro: "Click on this option to determine the approval authority of the document."

    }, {
        element: document.querySelector('#YearFrom'),
        intro: "Click on this option to determine the range of the year of approval of the document."

        }, {
        element: document.querySelector('#YearTo'),
        intro: "Click on this option to determine the range of the year of approval of the document."

    },  {
        element: document.querySelector('#WhereSelect'),
        intro: "Select an option to determine the document search location."

    },  {
        element: document.querySelector('#SearchTypeSelect'),
        intro: "Select an option to determine the type of search in documents. If the term you are looking for is \"laws and regulations\", by selecting the \"Exact\" search type, documents containing these words will be displayed exactly. By selecting \"OR\", documents that have either the word law, or the word regulation or both will be displayed. And if the search type is \"And\", documents containing both laws and regulations will be displayed."
    },  {
        element: document.querySelector('#search_result_tab'),
        intro: "The search results according to the search elements specified by the user are presented in this tab. The user can also sort the results based on different columns."

    },{
        element: document.querySelector('#bar_chart_info_tab'),
        intro: "Graphical analyzes of the documents appearing as a result of the search are presented in this tab."

    },{
        element: document.querySelector('#document_graph_tab'),
        intro: "The graph of references among the documents appearing in the search result is presented in this tab."

    },{
        element: document.querySelector('#ExportExcel'),
        intro: "Click on this option to download the names of the documents and their additional information in Excel format."

    },{
        element: document.querySelector('#DownloadBtn'),
        intro: "Click on this option to download the text of the documents that appeared in the search result."

    }, ]
}).start();


}
