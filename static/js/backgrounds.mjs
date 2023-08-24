// chatbot-flavor
// chatbot-last-message
// chatbot-response
// chatbot-content-response

import buildHeader from "./components/root.mjs";

let loading = false;

window.onload = function () {
  buildHeader("backgrounds");
};

document
  .querySelector(".chatbot-submit-btn")
  .addEventListener("click", (event) => {
    event.preventDefault();
    // get both of the messages
    const message = document.getElementById("input").value;
    const gmMessage = document.getElementById("gm-input").value;
    chatbotResponse(message, gmMessage);
  });

document.querySelector("#export-button").addEventListener("click", (event) => {
  event.preventDefault();
  // EXPORT GM MESSAGE TO BUCKET
  const gmMessage = document.getElementById("gm-input").value;
  fetchExport(gmMessage);
});

document.querySelector("#import-button").addEventListener("click", (event) => {
  event.preventDefault();
  // IMPORT GM MESSAGE TO DOCUMENT
  // get otc
  const otcCode = getOTCCode();
  // use otc to fetch gm message from server
  fetchImport(otcCode);
});

document.querySelector(".copy-button").addEventListener("click", (event) => {
  event.preventDefault();
  // COPY TO CLIPBOARD THE NUMBERS IN OTC
  const otcCode = getOTCCode();
  const copyContent = async () => {
    try {
      await navigator.clipboard.writeText(otcCode);
    } catch (err) {
      console.error("Failed to copy: ", err);
    }
  };
  copyContent();
});

const getOTCCode = () => {
  const otcArray = new Array(6);
  for (let i = 0; i < 6; i++) {
    const otcID = "otc-" + (i + 1).toString();
    const otcNumber = document.getElementById(otcID).value;
    otcArray[i] = otcNumber;
  }
  return otcArray.join("");
};

const setOTCCode = (otcCode) => {
  for (let i = 0; i < 6; i++) {
    const otcID = "#otc-" + (i + 1).toString();
    const otcElement = document.querySelector(otcID);
    otcElement.value = otcCode[i];
  }
};

const mutateMainFlavor = (flavor) => {
  const flavorElement = document.getElementById("main-flavor");
  flavorElement.textContent = flavor;
};

const mutateGMFlavor = (flavor) => {
  const flavorElement = document.getElementById("gm-flavor-text");
  flavorElement.textContent = flavor;
};

const mutateUserFlavor = (flavor) => {
  const flavorElement = document.getElementById("user-flavor");
  flavorElement.textContent = flavor;
};

const mutateGMInput = (text) => {
  const chatbotElement = document.getElementById("gm-input");
  chatbotElement.textContent = text;
};

const concatChatbotResponse = (text) => {
  const chatbotElement = document.querySelector(".chatbot-response");
  chatbotElement.style.visibility = "visible";
  chatbotElement.textContent = chatbotElement.textContent + text;
};

const clearRuleResponse = () => {
  const chatbotElement = document.querySelector(".chatbot-response");
  chatbotElement.style.visibility = "hidden";
  chatbotElement.textContent = "";
};

const fetchImport = async (otc) => {
  try {
    loading = true;

    if (otc === "" || otc.length !== 6){
      loading = false;
      mutateGMInput("Please use a valid code.")
      return
    }

    const response = await fetch("/import/scene", {
      method: "POST",
      body: JSON.stringify({
        otc: otc,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const data = await response.json();
    mutateGMInput(data["gm-scene"]);
    loading = false;
    return data;
  } catch (error) {
    loading = false;
  }
};

const fetchExport = async (gmMessage) => {
  try {
    loading = true;

    if (gmMessage.trim() === "") {
      loading = false
      mutateGMInput("Please add a scene or setting before exporting.")
      return
    }

    const response = await fetch("/export/scene", {
      method: "POST",
      body: JSON.stringify({
        gm_message: gmMessage,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const data = await response.json();
    setOTCCode(data.otc);
    loading = false;
    return data;
  } catch (error) {
    loading = false;
  }
};

const fetchBackgrounds = async (message, gmMessage) => {
  try {
    loading = true;
    mutateMainFlavor("Let me spin a tale for you.");
    mutateUserFlavor("I like your ideas, let's see what we create together.");

    const response = await fetch("/chat/backgrounds", {
      method: "POST",
      body: JSON.stringify({
        message: message,
        gm_message: gmMessage,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    const reader = response.body
      .pipeThrough(new TextDecoderStream())
      .getReader();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      concatChatbotResponse(value);
    }

    mutateMainFlavor(
      "I am Casandalee. Tell me about the town and your character. I will spin you a tail about their backstory."
    );
    mutateUserFlavor("Do you like my ideas?");

    loading = false;
  } catch (error) {
    loading = false;
  }
};

const chatbotResponse = (message, gmMessage) => {
  if (message === "" || gmMessage === "") {
    // flavor update
    mutateMainFlavor("I need both pieces to generate your background.");
  } else {
    if (loading) {
      // loading flavor
      mutateMainFlavor(
        "Slow down... I can only answer you one question at a time."
      );
    } else {
      // complete message
      clearRuleResponse();
      mutateMainFlavor("Let me think about that...");
      fetchBackgrounds(message, gmMessage);
    }
  }
};
