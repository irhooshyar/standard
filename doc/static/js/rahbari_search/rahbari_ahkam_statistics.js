async function getFullProfileInfo(country_id, type_id, label_name, from_year, to_year, place, text, search_type, curr_page) {
    const rahbari_type = 0
    const request_link = 'http://' + location.host + "/rahbari_get_full_profile_analysis/" + country_id + "/" + type_id + "/" +
        label_name + "/" + from_year + "/" + to_year + "/" + rahbari_type + "/" + place + "/" + text + "/" + search_type + "/"
        + curr_page + "/";

    startBlockUI('paragraph_info_pane');
    let response = await fetch(request_link).then(response => response.json());

    console.log("__", response)

    /*  Show Table Result */
    total_hits = response["total_hits"]
    // ES_SearchResult = response["result"]
    ES_Aggregations = response["aggregations"]

    const paragraph_tab = document.getElementById("paragraph_info_tab")
    if (paragraph_tab.classList.contains("active")) {
        document.getElementById("SearchResultLable").innerText = "تعداد کل نتایج: " + total_hits + " حکم"
    }
    paragraph_tab.addEventListener("click", () => {
        document.getElementById("SearchResultLable").innerText = "تعداد کل نتایج: " + total_hits + " حکم"
    })

    let sentiment_chart = ES_Aggregations['rahbari-sentiment-agg']['buckets']
    let classification_chart = ES_Aggregations['rahbari-classification-subject-agg']['buckets']
    let persons_chart = ES_Aggregations['rahbari-person-agg']['buckets']
    let locations_chart = ES_Aggregations['rahbari-location-agg']['buckets']
    let organizations_chart = ES_Aggregations['rahbari-organization-agg']['buckets']

    sentiment_chart.sort((a, b) => {
        return getCharAtCode(a['key']) - getCharAtCode(b['key'])
    })
    classification_chart.sort((a, b) => {
        return getCharAtCode(a['key'][0]) - getCharAtCode(b['key'][0])
    })


    showChartData(sentiment_chart, "sentiment_container", "paragraph_charts", [], undefined, "احساس", "توزیع احکام براساس احساسات", "تعداد احکام")
    stackBasedChartData(classification_chart, "subject_container", "موضوع", "توزیع بیانات براساس موضوع", false, false)
    stackBasedChartData(persons_chart, "person_container", "شخص حقیقی", "توزیع بیانات براساس اشخاص حقیقی", true, true)
    stackBasedChartData(locations_chart, "location_container", "موقعیت مکانی", "توزیع بیانات براساس موقعیت مکانی", true, false)
    stackBasedChartData(organizations_chart, "organization_container", "سازمان", "توزیع بیانات  براساس سازمان‌ها", true, false)

    stopBlockUI('paragraph_info_pane', 'داشبورد آماری احکام');
}

function stackBasedChartData(data, container, xAxisTitle,title, chooseFirst30 = false, showItemsTable = false) {
    const dataArray = []

    const sentiment_words = ["احساس بسیار منفی", "بدون ابراز احساسات", "احساس منفی", "احساس خنثی یا ترکیبی از مثبت و منفی", "احساس مثبت", "احساس بسیار مثبت"]
    const differentValues = []
    for (let info of data) {
        const key = info.key[0]

        if (key === "بدون شخص حقیقی" || key === "بدون موقعیت مکانی" || key === "بدون ذکر سازمان") {
            continue
        }

        if (differentValues.includes(key)) {
            continue
        }
        differentValues.push(key)
    }

    const items = []
    for (const value of differentValues) {
        const item = {}
        item['key'] = value
        item['value'] = {}

        for (const info of data) {
            const key = info.key

            if (key[0] === value && !item['value'][key[1]]) {
                item['value'][key[1]] = info

                if (Object.keys(item['value']).length === 6) {
                    break
                }
            }
        }
        items.push(item)
    }

    if (showItemsTable) {
        get_real_persons(items)
    }
    console.log(items)

    for (const item of items) {
        const dataRow = []
        dataRow.push(item['key'])
        dataRow.push(item['value']['احساس بسیار مثبت'] ? item['value']['احساس بسیار مثبت']['doc_count'] : 0)
        dataRow.push(item['value']['احساس مثبت'] ? item['value']['احساس مثبت']['doc_count'] : 0)
        dataRow.push(item['value']['احساس خنثی یا ترکیبی از مثبت و منفی'] ? item['value']['احساس خنثی یا ترکیبی از مثبت و منفی']['doc_count'] : 0)
        dataRow.push(item['value']['احساس منفی'] ? item['value']['احساس منفی']['doc_count'] : 0)
        dataRow.push(item['value']['احساس بسیار منفی'] ? item['value']['احساس بسیار منفی']['doc_count'] : 0)
        dataRow.push(item['value']['بدون ابراز احساسات'] ? item['value']['بدون ابراز احساسات']['doc_count'] : 0)

        dataArray.push(dataRow)

        if (chooseFirst30 && dataArray.length === 30) {
            break
        }
    }


    showStackBasedChart(dataArray, container, xAxisTitle,title)
}


function showStackBasedChart(data, container, xAxisTitle, title) {
    const onClick = async function (event) {
    
        const click_tag = event.domTarget.tag;
        const index = click_tag["index"]
        const text = data[index][0];
        const sentiment = click_tag["X"]["iV"]["seriesName"]
    
        let filtered_result = []
        let header = ""
        let save_file_name = document.getElementById("SearchBox").value;
    
        let field_value = text.replaceAll("#", "*")
        let field_name = CHART_FIELD_DICT[container] + ".keyword"
        let chart_name = CHART_NAME_DICT[container]
    
        await GetClickedColumnParagraphs(chart_name, field_name, field_value, false, false, "", sentiment)
        $("#ChartModalBtn_2").click();
    
    }
    const options = {
        data,
        xAxisTitle,
        yAxisTitle: 'تعداد احکام',
        title,
        bars: [
            {
                name: "احساس بسیار مثبت",
                onClick
            },
            {
                name: "احساس مثبت",
                onClick
            },
            {
                name: "احساس خنثی یا ترکیبی از مثبت و منفی",
                onClick
            },
            {
                name: "احساس منفی",
                onClick
            },
            {
                name: "احساس بسیار منفی",
                onClick
            },
            {
                name: "بدون ابراز احساسات",
                onClick
            }
        ]
    };

    newBarsChart(container, options)

}

function getCharAtCode(str) {
    let sum = 0
    for (let i = 0; i < str.length; i++) {
        sum += str.charCodeAt(i);
    }

    return sum
}