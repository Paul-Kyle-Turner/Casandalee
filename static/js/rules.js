// chatbot-flavor
// chatbot-last-message
// chatbot-response
// chatbot-content-response

let loading = false;

document
  .querySelector(".chatbot-input")
  .addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      const inputElement = document.querySelector(".chatbot-input");
      const inputMessage = inputElement.value.trim();
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

const fetchRules = async (message) => {
  try {
    loading = true;
    const response = await fetch("/rules", {
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
    loading = false;
  } catch (error) {
    loading = false;
    mutateFlavor("There has been an error in my process.");
  }
};

const chatbotResponse = (message) => {
  if (message === "") {
    mutateFlavor("I can't say anything if you don't.");
  } else {
    if (loading) {
      mutateFlavor("Slow down... I can only answer one question at a time.");
    } else {
      clearRuleResponse();
      mutateFlavor("Let me think about that...");
      mutateLastMessage(message);
      fetchRules(message);
    }
  }
};
