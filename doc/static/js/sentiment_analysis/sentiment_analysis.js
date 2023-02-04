function startTimer() {
  startTime = new Date();
}

function endTimer() {
  endTime = new Date();
  var timeDiff = endTime - startTime; //in ms
  // strip the ms
  timeDiff /= 1000;

  // get seconds
  var seconds = Math.round(timeDiff);
  console.log(seconds + " seconds");
  return seconds;
}



async function GetTextSummary(text) {
  let form_data = new FormData();
  form_data.append("text", text);

  let link_request = "http://" + location.host + "/GetTextSummary/";

  $.ajax({
    url: link_request,
    data: form_data,
    type: "POST",
    contentType: false,
    processData: false,
    async: true,
  })
    .done(
      await function (res) {
        document.getElementById("summary_text").innerHTML = res["text_summary"];
      }
    )
    .fail(
      await function (res) {
        console.log("fail");
      }
    );


}

COUNTRY_NAME = "EMPTY";
async function init() {
  const url = new URL(window.location.href);
  var paragraph_id = url.searchParams.get("id");

  if (paragraph_id) {
    let request_link =
      "http://" + location.host + "/GetParagraphBy_ID/" + paragraph_id + "/";
    let response = await fetch(request_link).then((response) =>
      response.json()
    );
    paragraph_text = response["paragraph_text"];
    COUNTRY_NAME = response["country_name"];
    document.getElementById("InputText").value = paragraph_text;
    document.getElementById("InputText").disabled = true;


    if (COUNTRY_NAME == "اسناد رهبری") $("#sentiment_result_tab").hide();

    await showKeywordSubjectTab(paragraph_id);

    await showResult();

    
    await getSimilarParagraphs(paragraph_id);

    startBlockUI('summary_text');
    await GetTextSummary(paragraph_text);
    stopBlockUI('summary_text', 'نتایج جست‌وجو');


    document.getElementById("btn").disabled = true;
  } else {
    $("#subject_keyword_tab").hide();
    $("#similarity_tab").hide();
    $("#subject_keyword_tab").removeClass("active");
    $("#subject_keyword_pane").removeClass("active");

    $("#classification_result_tab").addClass("active");
    $("#classification").addClass("active");

    document.getElementById("class_error_text_wrapper").style.display = "none";
  }
}

async function getSimilarParagraphs(paragraph_id) {
  request_link =
    "http://" +
    location.host +
    "/GetSimilarParagraphs_ByParagraphID/" +
    paragraph_id +
    "/";
  response = await fetch(request_link).then((response) => response.json());
  similar_paragraphs = response["similar_paragraphs"];

  let body_content = "";

  if (similar_paragraphs.length == 0) {
    body_content = "پاراگرافی یافت نشد.";
  }

  for (let para of similar_paragraphs) {
    const document_id = para["_source"]["document_id"];
    let document_name = "";

    if ("document_name" in para["_source"]) {
      document_name = para["_source"]["document_name"];
    } else {
      document_name = para["_source"]["name"];
    }

    let text = "";
    try {
      text = para["highlight"]["attachment.content"][0];
    } catch (error) {
      text = para["_source"]["attachment"]["content"];
    }

    const doc_link =
      "http://" + location.host + "/information/?id=" + document_id;
    const doc_tag =
      "<a title='پروفایل سند' class='bold text-primary' target='blank' href='" +
      doc_link +
      "'>" +
      document_name +
      "</a>";

    const paragraph_link =
      "http://" + location.host + "/sentiment_analysis/?id=" + paragraph_id;

    const paragraph_tag =
      "<a class='' title = 'پروفایل حکم' target='blank' href='" +
      paragraph_link +
      "'>" +
      text +
      "</a>";

    const tag =
      "<li class='mb-3 lh-lg shadow border rounded px-4'>" +
      doc_tag +
      paragraph_tag +
      "</li>";
    body_content += tag;
  }

  result_content = "<ol start='" + "1" + "'>" + body_content + "</ol>";
  document.getElementById("SimilarParagraphsContainer").innerHTML =
    result_content;
}

async function showKeywordSubjectTab(paragraph_id) {
  const request_link =
    "http://" +
    location.host +
    "/GetParagraphSubjectContent/" +
    paragraph_id +
    "/" +
    12 +
    "/";
  let response = await fetch(request_link).then((response) => response.json());
  paragraph_text = response["paragraph_text"];
  document_name = response["document_name"];
  document_id = response["document_id"];
  subject_name = response["subject_name"];

  let subject_tag = "";
  if (subject_name !== "") subject_tag = subject_name;

  const paragraph_tag =
    '<div class="subject-content-container"><p>' +
    paragraph_text +
    "</p>" +
    subject_tag +
    "</div>";

  const doc_link =
    "http://" + location.host + "/information/?id=" + document_id;
  let doc_tag =
    "<a style = 'text-decoration:none;' title = 'پروفایل سند' class='bold text-right text-secondary' target='blank' href='" +
    doc_link +
    "'>" +
    document_name +
    "</a>";

  document.getElementById("subjectContentHeader").innerHTML = doc_tag;
  document.getElementById("subjectContentBody").innerHTML += paragraph_tag;

  $("#subject_keyword_tab").show();
}

async function showResult() {
  document.getElementById("class_error_text_wrapper").style.display = "none";
  // document.getElementById('subject_chart_container').style.display = "block";
  document.getElementById("classification_box_title").style.display = "block";

  document.getElementById("no_info").style.display = "none";
  const text = document.getElementById("InputText").value;
  const showResultButton = document.getElementById("btn");

  const cleanText = text.replaceAll("/", ".");

  const sentimentAnalyserLink =
    "http://" + location.host + "/sentimentAnalyser/" + cleanText + "/";
  const taggingSentenceLink =
    "http://" + location.host + "/tagAnalyser/" + cleanText + "/";
  const classificationSentenceLink =
    "http://" + location.host + "/classificationAnalyser/" + cleanText + "/";

  if (cleanText.trim().length === 0) {
    showEmptyInputError();
    return;
  }

  startFullPageBlockUI();
  showResultButton.innerText = "لطفا منتظر باشید";
  showResultButton.disabled = true;


  const taggingRequest = fetch(taggingSentenceLink);
  const classificationRequest = fetch(classificationSentenceLink);

  await taggingRequestProcess(taggingRequest, cleanText);
  await classificationRequestProcess(classificationRequest);
//   console.log(COUNTRY_NAME)
  if (COUNTRY_NAME != "اسناد رهبری") {
    const sentimentRequest = fetch(sentimentAnalyserLink);
    await sentimentRequestProcess(sentimentRequest);

  }

  showResultButton.innerText = "مشاهده نتیجه";
  showResultButton.disabled = false;
  stopFullPageBlockUI('مقداردهی اولیه')
}

function showEmptyInputError() {
  const input = document.getElementById("InputText");
  const inputBorderColor = input.style.borderColor;

  input.style.borderColor = "red";

  setTimeout(() => {
    input.style.borderColor = inputBorderColor;
  }, 500);
}

// sentiment functions
async function sentimentRequestProcess(sentimentRequest) {
  const sentimentResponse = await sentimentRequest;

  const sentimentResponseJson = await sentimentResponse.json();
  const sentimentResult = sentimentResponseJson["result"][0];
  const score = resultToScore(sentimentResult);
  showScoreChart(score);
  showLabelResult(score, sentimentResult);
}

function showScoreChart(score) {
  // const emojiTarget = document.getElementById('score_emoji');
  //
  // if (score === -100) {
  //     emojiTarget.innerHTML = '&#128545;'
  // } else if (score === -50) {
  //     emojiTarget.innerHTML = '&#128577;'
  // } else if (score === 0) {
  //     emojiTarget.innerHTML = '&#128528;'
  // } else if (score === 50) {
  //     emojiTarget.innerHTML = '&#128522;'
  // } else {
  //     emojiTarget.innerHTML = '&#128515;'
  // }

  const opts = {
    angle: 0, // The span of the gauge arc
    lineWidth: 0.3, // The line thickness
    radiusScale: 0.9, // Relative radius
    pointer: {
      length: 0.42, // // Relative to gauge radius
      strokeWidth: 0.029, // The thickness
      color: "#000000", // Fill color
    },
    limitMax: true, // If false, max value increases automatically if value > maxValue
    limitMin: true, // If true, the min value of the gauge will be fixed
    colorStart: "#6F6EA0", // Colors
    colorStop: "#C0C0DB",
    strokeColor: "#EEEEEE", // to see which ones work best for you
    generateGradient: true,
    highDpiSupport: true, // High resolution support
    staticZones: [
      { strokeStyle: "#81323D", min: -100, max: -75 },
      { strokeStyle: "#BF5A68", min: -75, max: -25 },
      { strokeStyle: "#C9C9C9", min: -25, max: 25 },
      { strokeStyle: "#9ABF5A", min: 25, max: 75 },
      { strokeStyle: "#648132", min: 75, max: 100 },
    ],
    staticLabels: {
      font: "10px IRANSans", // Specifies font
      labels: [-100, -50, 0, 50, 100], // Print labels at these values
      fontSize: 160,
      color: "#000000", // Optional: Label text color
      fractionDigits: 0, // Optional: Numerical precision. 0=round off.
    },
  };
  const sentiment_wrraper = document.getElementById("sentiment_analyser");
  sentiment_wrraper.classList.remove("tab-pane");

  const target = document.getElementById("score_emoji"); // your canvas element
  const gauge = new Gauge(target).setOptions(opts);
  gauge.maxValue = 100; // set max gauge value
  gauge.setMinValue(-100); // Prefer setter over gauge.minValue = 0
  gauge.animationSpeed = 10; // set animation speed (32 is default value)
  gauge.set(score); // set actual value

  sentiment_wrraper.classList.add("tab-pane");
}

function showLabelResult(score, result) {
  let result_label = "";
  let result_color = "";

  switch (score) {
    case 0:
      if (result === "no sentiment expressed") {
        result_label = "بدون ابراز احساسات";
      } else {
        result_label = "احساس خنثی یا ترکیبی از مثبت و منفی";
      }
      result_color = "#000000";
      break;
    case 100:
      result_label = "احساس بسیار مثبت";
      result_color = "#648132";
      break;
    case 50:
      result_label = "احساس مثبت";
      result_color = "#648132";
      break;
    case -100:
      result_label = "احساس بسیار منفی";
      result_color = "#81323D";
      break;
    case -50:
      result_label = "احساس منفی";
      result_color = "#81323D";
      break;
    default:
      break;
  }

  document.getElementById("result_label").innerText = result_label;
  document.getElementById("result_label").style.color = result_color;
}

function getEntityAndColor(entity) {
  let color = "";
  let entityWord = "";
  switch (entity) {
    case "B-date":
      color = "#D946EF";
      entityWord = "تاریخ";
      break;
    case "B-time":
      color = "#14B8A6";
      entityWord = "زمان";
      break;
    case "B-money":
      color = "#EC4899";
      entityWord = "پول";
      break;
    case "B-location":
      color = "#6366F1";
      entityWord = "مکان";
      break;
    case "B-organization":
      color = "#ff5050";
      entityWord = "سازمان";
      break;
    case "B-percent":
      color = "#9900ff";
      entityWord = "درصد";
      break;
    case "B-person":
      color = "#0099cc";
      entityWord = "فرد حقیقی";
      break;
    case "B-facility":
      color = "#D946EF";
      entityWord = "امکانات";
      break;
    case "B-product":
      color = "#EC4899";
      entityWord = "محصول";
      break;
    case "B-event":
      color = "#14B8A6";
      entityWord = "رویداد";
      break;
    default:
      color = "#EC4899";
      entityWord = entity;
      break;
  }
  return { color: color, word: entityWord };
}

function resultToScore(result) {
  switch (result) {
    case "mixed":
      return 0;
    case "borderline":
      return 0;
    case "very positive":
      return 100;
    case "positive":
      return 50;
    case "very negative":
      return -100;
    case "negative":
      return -50;
    default:
      return 0;
  }
}

// tagging functions
async function taggingRequestProcess(taggingRequest, text) {
  const taggingResponse = await taggingRequest;

  const taggingResponseJson = await taggingResponse.json();

  if (taggingResponseJson["result"] === "ERROR") {
    taggingSetError();
    return;
  }

  const taggingProducedJson = taggingProduceJson(taggingResponseJson);

  taggingChangeDom(taggingProducedJson, text);
}

function taggingChangeDom(taggingJson, text) {
  let resultText = text;
  let difference = 0;

  for (let i = 0; i < taggingJson.length; i++) {
    const object = taggingJson[i];
    const searchText = text.substring(object["start"], object["end"]);

    const replaceHtml = `<span style="background-color: ${object["color"]}30">
                                 ${searchText} <span style="background-color: ${object["color"]}">${object["entity"]}</span>
                                 </span>`;

    resultText =
      resultText.substring(0, object["start"] + difference) +
      replaceHtml +
      resultText.substring(object["end"] + difference, resultText.length);

    difference = resultText.length - text.length;
  }

  document.getElementById("result_text").innerHTML = "" + resultText;
}

function taggingSetError() {
  const errorBox = document.getElementById("result_text");
  errorBox.innerText = "بدلیل طولانی بودن متن، در روند محاسبه مشکل ایجاد شد.";
}

function taggingProduceJson(jsonString) {
  const taggingProducedJson = jsonString["result"].replaceAll("'", '"');
  const taggingParsedJson = JSON.parse(taggingProducedJson);
  console.log(taggingParsedJson);

  taggingParsedJson.sort((object1, object2) => {
    return object1.start - object2.start;
  });
  const taggingJson = taggingParsedJson
    .map((object, index, array) => {
      if (object["entity"].startsWith("I")) {
        return null;
      }

      const result = getEntityAndColor(object["entity"]);
      let startWordIndex = object["start"];
      let endWordIndex = object["end"];
      let entity = result.word;
      let color = result.color;

      for (let i = index + 1; i < array.length; i++) {
        const iObject = array[i];
        if (iObject["entity"].startsWith("B")) break;

        if (
          iObject["entity"].split("-")[1] !== object["entity"].split("-")[1]
        ) {
          taggingParsedJson[i]["entity"] = taggingParsedJson[i][
            "entity"
          ].replace("I", "B");
          break;
        }

        if (endWordIndex + 10 < iObject["start"]) {
          taggingParsedJson[i]["entity"] = taggingParsedJson[i][
            "entity"
          ].replace("I", "B");
          break;
        }

        endWordIndex = iObject["end"];
      }

      return {
        entity: entity,
        start: startWordIndex,
        end: endWordIndex,
        color: color,
      };
    })
    .filter((object) => object !== null);

  return taggingJson;
}

// classification functions
async function classificationRequestProcess(classificationRequest) {
  const classificationResponse = await classificationRequest;

  const classificationResponseJson = await classificationResponse.json();

  if (classificationResponseJson["result"] === "ERROR") {
    classificationSetError();
    return;
  }

  const data = classificationJsonResultProcess(classificationResponseJson);

  showBarChart(data);
}

function classificationJsonResultProcess(jsonString) {
  const classificationProducedJson = jsonString["result"].replaceAll("'", '"');
  const classificationParsedJson = JSON.parse(classificationProducedJson);
  const classificationArray = classificationParsedJson[0];

  const classificationSortResult = classificationArray.sort(
    (object1, object2) => {
      return object2.score - object1.score;
    }
  );

  const data = [];

  classificationSortResult.map((object) => {
    data.push([object.label, object.score * 100]);
    // labels.push(object.label);
    // data.push(object.score * 100)
  });

  return data;
}

function showBarChart(data) {
  data = data.map((d) => {
    const label = d[0];
    const lowerThan50 = d[1] < 50 ? d[1] : 0;
    const higherThan50 = d[1] >= 50 ? d[1] : 0;
    return [label, lowerThan50, higherThan50];
  });
  const options = {
    data,
    xAxisTitle: "موضوع",
    title: "توزیع موضوعی متن داده شده",
    yAxisTitle: "درصد شباهت",
    bars: [
      {
        name: "کمتر از 50 درصد شباهت",
      },
      {
        name: "بیشتر از 50 درصد شباهت",
      },
    ],
  };

  newBarsChart("subject_chart_container", options);
}

function classificationSetError() {
  const errorBox = document.getElementById("class_error_text_wrapper");
  document.getElementById("subject_chart_container").style.display = "none";
  document.getElementById("classification_box_title").style.display = "none";
  errorBox.style.display = "block";
  errorBox.style.fontSize = "18px";
  errorBox.innerText = "بدلیل طولانی بودن متن، در روند محاسبه مشکل ایجاد شد.";
}
