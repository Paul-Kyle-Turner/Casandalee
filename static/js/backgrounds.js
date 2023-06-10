// chatbot-flavor
// chatbot-last-message
// chatbot-response
// chatbot-content-response

let loading = false;

document
  .querySelector(".chatbot-submit-btn")
  .addEventListener("click", (event) => {
    event.preventDefault();
    chatbotResponse(input);
  });

const fetchRules = async (message) => {
  try {
    loading = true;
    const response = await fetch("/backgrounds", {
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
      fetchBackground(message);
    }
  }
};
