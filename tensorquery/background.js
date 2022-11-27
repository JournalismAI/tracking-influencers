let core = null;

async function savePayload(core) {

  function rand(length, current) {
    current = current ? current : '';
    return length ? rand(--length, '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz'.charAt(Math.floor(Math.random() * 60)) + current) : current;
  }

  function stamp(tag, ext = 'json') {
    const today = new Date();
    const month = today.getMonth() + 1;
    const hour = today.getHours();
    const minute = today.getMinutes();
    return `tensorsocial_${tag}_` + today.getFullYear() + (month < 10 ? '0' + month.toString() : month) + today.getDate() + '_' + (hour < 10 ? '0' + hour.toString() : hour) + (minute < 10 ? '0' + minute.toString() : minute) + '_' + rand(5) + `.${ext}`;
  }

  function downloadJSON(id, data) {
    const a = document.createElement('a');
    const blob = new Blob([data], {
      type: 'octet/stream'
    });
    const e = new MouseEvent('click');
    a.href = window.URL.createObjectURL(blob);
    a.download = stamp(`data_${id}`);
    a.dispatchEvent(e);
  }

  if (core) {
    downloadJSON('identification', core);
  }

}

chrome.action.onClicked.addListener((tab) => {
  if (!tab.url.includes("chrome://")) {
    chrome.scripting.executeScript({
      target: {
        tabId: tab.id
      },
      function: savePayload,
      args: [core]
    });
  }
});

chrome.webRequest.onBeforeRequest.addListener(details => {
    if (details.method == 'POST' && details.url.includes('identification')) {
      const postedString = decodeURIComponent(String.fromCharCode.apply(null, new Uint8Array(details.requestBody.raw[0].bytes)));
      core = (postedString) ? postedString : null;
    }
  }, {
    urls: ['https://app.tensorsocial.com/v1/identification'],
    types: ['main_frame', 'sub_frame', 'script', 'xmlhttprequest']
  },
  ['requestBody']);