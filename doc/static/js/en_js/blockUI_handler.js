const notyf = new Notyf({
  duration: 5000,
  position: {
    x: "left",
    y: "bottom",
  },
  dismissible: true,
});

/* Timer functions  */
var startTime, endTime;

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

// override these in your code to change the default behavior and style
$.blockUI.defaults = {
  // message displayed when blocking (use null for no message)
  message: "<h1>Please wait...</h1>",

  title: null, // title string; only used when theme == true
  draggable: true, // only used when theme == true (requires jquery-ui.js to be loaded)

  theme: false, // set to true to use with jQuery UI themes

  // styles for the message when blocking; if you wish to disable
  // these and use an external stylesheet then do this in your code:
  // $.blockUI.defaults.css = {};
  css: {
    padding: 0,
    margin: 0,
    width: "30%",
    top: "40%",
    left: "35%",
    textAlign: "center",
    color: "#000",
    border: "3px solid #aaa",
    backgroundColor: "#fff",
    cursor: "wait",
  },

  // minimal style set used when themes are used
  themedCSS: {
    width: "30%",
    top: "40%",
    left: "35%",
  },

  // styles for the overlay
  overlayCSS: {
    backgroundColor: "#000",
    opacity: 0.6,
    cursor: "wait",
  },

  // style to replace wait cursor before unblocking to correct issue
  // of lingering wait cursor
  cursorReset: "default",

  // styles applied when using $.growlUI
  growlCSS: {
    width: "350px",
    top: "10px",
    right: "",
    left: "10px",
    border: "none",
    padding: "5px",
    opacity: 0.6,
    cursor: null,
    color: "#fff",
    backgroundColor: "#000",
    "-webkit-border-radius": "10px",
    "-moz-border-radius": "10px",
  },

  // IE issues: 'about:blank' fails on HTTPS and javascript:false is s-l-o-w
  // (hat tip to Jorge H. N. de Vasconcelos)
  iframeSrc: /^https/i.test(window.location.href || "")
    ? "javascript:false"
    : "about:blank",

  // force usage of iframe in non-IE browsers (handy for blocking applets)
  forceIframe: false,

  // z-index for the blocking overlay
  baseZ: 2000,

  // set these to true to have the message automatically centered
  centerX: true, // <-- only effects element blocking (page block controlled via css above)
  centerY: true,

  // allow body element to be stetched in ie6; this makes blocking look better
  // on "short" pages.  disable if you wish to prevent changes to the body height
  allowBodyStretch: true,

  // enable if you want key and mouse events to be disabled for content that is blocked
  bindEvents: true,

  // be default blockUI will supress tab navigation from leaving blocking content
  // (if bindEvents is true)
  constrainTabKey: true,

  // fadeIn time in millis; set to 0 to disable fadeIn on block
  fadeIn: 200,

  // fadeOut time in millis; set to 0 to disable fadeOut on unblock
  fadeOut: 400,

  // time in millis to wait before auto-unblocking; set to 0 to disable auto-unblock
  timeout: 0,

  // disable if you don't want to show the overlay
  showOverlay: false,

  // if true, focus will be placed in the first available input field when
  // page blocking
  focusInput: true,

  // suppresses the use of overlay styles on FF/Linux (due to performance issues with opacity)
  // no longer needed in 2012
  // applyPlatformOpacityRules: true,

  // callback method invoked when fadeIn has completed and blocking message is visible
  onBlock: null,

  // callback method invoked when unblocking has completed; the callback is
  // passed the element that has been unblocked (which is the window object for page
  // blocks) and the options that were passed to the unblock call:
  //   onUnblock(element, options)
  onUnblock: null,

  // don't ask; if you really must know: http://groups.google.com/group/jquery-en/browse_thread/thread/36640a8730503595/2f6a79a77a78e493#2f6a79a77a78e493
  quirksmodeOffsetHack: 4,

  // class name of the message block
  blockMsgClass: "blockMsg",

  // if it is already blocked, then ignore it (don't unblock and reblock)
  ignoreIfBlocked: false,
};

function startBlockUI(container_id) {

  container_selector = "#" + container_id;

  $(container_selector).block({
    // BlockUI code for element blocking
    message:
      "<div class='lds-ellipsis'><div></div><div></div><div></div><div></div></div><h6 dir='ltr' style = 'font-family:Helvetica, sans-serif;'>loading information...<h6>",
    css: {
      color: "var(--menu_color)",
      border: "none",
      borderRadius: "5px",
      borderColor: "var(--menu_color)",
      paddingTop: "5px",
    },
  });
  startTimer();
}

function stopBlockUI(container_id, tab_name) {
  console.log(tab_name);
  container_selector = "#" + container_id;
  $(container_selector).unblock();

  elapsed_time = endTimer();

  if (elapsed_time > 0) {
    notyf_message = tab_name + ": " + elapsed_time + " seconds";

    notyf.success(notyf_message);
  }
}

function startFullPageBlockUI() {
  notyf.dismissAll();

  // change message border

  $.blockUI({
    // BlockUI code for element blocking
    message:
      "<div class='lds-ellipsis'><div></div><div></div><div></div><div></div></div><h6 style = 'font-family:Helvetica, sans-serif;'>loading information...<h6>",

    css: {
      color: "var(--menu_color)",
      border: "none",
      borderRadius: "5px",
      borderColor: "var(--menu_color)",
      paddingTop: "5px",
    },
    showOverlay:true
  });

  startTimer();
}

function stopFullPageBlockUI(tab_name) {
  $.unblockUI();
  elapsed_time = endTimer();

  if (elapsed_time > 0) {
    notyf_message = tab_name + ": " + elapsed_time + " seconds";

    notyf.success(notyf_message);
  }
}

// ****************************************************

function showToastMessage(message_text) {
  document.getElementById("toast_message").innerHTML = message_text;
  var toastElList = [].slice.call(document.querySelectorAll(".toast"));
  var toastList = toastElList.map(function (toastEl) {
    return new bootstrap.Toast(toastEl);
  });
  toastList.forEach((toast) => toast.show());
}
