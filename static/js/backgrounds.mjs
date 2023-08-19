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
    const message = document.getElementById("input").value
    const gmMessage = document.getElementById("gm-input").value
    chatbotResponse(message, gmMessage);
  });

const mutateMainFlavor = (flavor) => {
  const flavorElement = document.getElementById("main-flavor");
  flavorElement.textContent = flavor;
};

const mutateGMFlavor = (flavor) => {
  const flavorElement = document.getElementById("gm-flavor");
  flavorElement.textContent = flavor;
};

const mutateUserFlavor = (flavor) => {
  const flavorElement = document.getElementById("user-flavor");
  flavorElement.textContent = flavor;
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

const fetchBackgrounds = async (message, gmMessage) => {
  try {
    loading = true;
    const response = await fetch("/chat/backgrounds", {
      method: "POST",
      body: JSON.stringify({
        message: message,
        "gm_message": gmMessage,
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

    mutateMainFlavor("Let me tell you about this person...")

    loading = false;
  } catch (error) {
    loading = false;
  }
};

const chatbotResponse = (message, gmMessage) => {
  if (message === "" || gmMessage === "") {
    // flavor update
    mutateMainFlavor("I need both pieces to generate your background.")
  } else {
    if (loading) {
      // loading flavor
      mutateMainFlavor("Slow down... I can only answer you one question at a time.")
    } else {
      // complete message
      clearRuleResponse();
      mutateMainFlavor("Let me think about that...");
      fetchBackgrounds(message, gmMessage)
    }
  }
};
