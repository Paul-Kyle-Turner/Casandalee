// chatbot-flavor
// chatbot-last-message
// chatbot-response
// chatbot-content-response

import buildHeader from "./components/root.mjs";

let loading = false;
let contentLoading = false;
let judgeMessageSent = false;

window.onload = function () {
  buildHeader("/");
};

document
  .querySelector(".chatbot-input")
  .addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      const inputMessage = document
        .querySelector(".chatbot-input")
        .value.trim();
      chatbotResponse(inputMessage);
    }
  });

document
  .querySelector(".chatbot-submit-btn")
  .addEventListener("click", (event) => {
    event.preventDefault();
    const input = document.querySelector(".chatbot-input").value.trim();
    chatbotResponse(input);
  });

const mutateFlavor = (flavor) => {
  const flavorElement = document.querySelector(".chatbot-flavor");
  flavorElement.textContent = flavor;
};

const mutateLastMessage = (message) => {
  const lastMessageElement = document.querySelector(".chatbot-last-message");
  lastMessageElement.style.visibility = "visible";
  lastMessageElement.textContent = message;
  document.querySelector(".chatbot-input").value = message;
};

const concatChatbotResponse = (lichText) => {
  const chatbotElement = document.querySelector(".chatbot-response");
  chatbotElement.style.visibility = "visible";
  chatbotElement.textContent = chatbotElement.textContent + lichText;
};

const clearRuleResponse = () => {
  const chatbotElement = document.querySelector(".chatbot-response");
  chatbotElement.style.visibility = "hidden";
  chatbotElement.textContent = "";
};

const showChatbotContent = (content) => {
  const chatbotElement = document.querySelector(".chatbot-content-response");
  chatbotElement.style.visibility = "visible";
  chatbotElement.textContent =
    "Casandalee used this information to determine the answer : ";
  for (const key in content) {
    const contentElement = document.createElement("a");
    contentElement.textContent = key;
    contentElement.href = content[key];
    contentElement.className = "content-link";
    chatbotElement.appendChild(contentElement);
  }
};

const clearChatbotContent = () => {
  const chatbotElement = document.querySelector(".chatbot-content-response");
  chatbotElement.style.visibility = "hidden";
  chatbotElement.textContent = "";
};

const fetchContent = async (message) => {
  try {
    contentLoading = true;
    const response = await fetch("/content/content", {
      method: "POST",
      body: JSON.stringify({
        message: message,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const data = await response.json();
    console.log(data)
    showChatbotContent(data);
    contentLoading = false;
  } catch (error) {
    contentLoading = false;
  }
};

const fetchRules = async (message) => {
  try {
    loading = true;
    const response = await fetch("/chat/rules", {
      method: "POST",
      body: JSON.stringify({
        message: message,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const reader = response.body
      .pipeThrough(new TextDecoderStream())
      .getReader();
    mutateFlavor("I think I found something...");
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      concatChatbotResponse(value);
    }
    mutateFlavor(
      "This is my best answer right now.  Don't worry I am learning..."
    );
    chatbotJudgeInit();
    fetchContent(message);
    loading = false;
    judgeMessageSent = false;
  } catch (error) {
    loading = false;
    mutateFlavor("There has been an error in my process.");
  }
};

const fetchJudge = async (message, response_message, response_judge) => {
  try {
    loading = true;
    if (judgeMessageSent) {
      mutateFlavor("Try another message before you judge me too harshly.");
    } else {
      const response = await fetch("/report/chat", {
        method: "POST",
        body: JSON.stringify({
          message: message,
          response_message: response_message,
          response_judge: response_judge,
        }),
        headers: {
          "Content-Type": "application/json",
        },
      });
      const data = await response.json();
      mutateFlavor(data["server-message"]);
      judgeMessageSent = true;
      loading = false;
    }
  } catch (error) {
    loading = false;
  }
};

const chatbotJudgeInit = () => {
  const chatbotElement = document.querySelector(".chatbot-response");

  const thumbsUp = document.createElement("button");
  thumbsUp.className = "thumbs-up";
  const faThumbsUp = document.createElement("i");
  faThumbsUp.className = "fa fa-thumbs-up";
  thumbsUp.appendChild(faThumbsUp);
  chatbotElement.appendChild(thumbsUp);

  const thumbsDown = document.createElement("button");
  thumbsDown.className = "thumbs-down";
  const faThumbsDown = document.createElement("i");
  faThumbsDown.className = "fa fa-thumbs-down";
  thumbsDown.appendChild(faThumbsDown);
  chatbotElement.appendChild(thumbsDown);

  thumbsUp.addEventListener("click", (event) => {
    event.preventDefault();
    const lastMessage = document
      .querySelector(".chatbot-last-message")
      .textContent.trim();
    const lastResponse = document
      .querySelector(".chatbot-response")
      .textContent.trim();
    const judge = "Good";
    fetchJudge(lastMessage, lastResponse, judge);
  });

  thumbsDown.addEventListener("click", (event) => {
    event.preventDefault();
    const lastMessage = document
      .querySelector(".chatbot-last-message")
      .textContent.trim();
    const lastResponse = document
      .querySelector(".chatbot-response")
      .textContent.trim();
    const judge = "Bad";
    fetchJudge(lastMessage, lastResponse, judge);
  });
};

const chatbotResponse = (message) => {
  if (message === "") {
    mutateFlavor("I can't say anything if you don't.");
  } else {
    if (loading || contentLoading) {
      mutateFlavor("Slow down... I can only answer one question at a time.");
    } else {
      clearRuleResponse();
      clearChatbotContent();
      mutateFlavor("Let me think about that...");
      mutateLastMessage(message);
      fetchRules(message);
    }
  }
};
