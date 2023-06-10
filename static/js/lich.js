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
      lichResponse(inputMessage);
    }
  });

document
  .querySelector(".chatbot-submit-btn")
  .addEventListener("click", (event) => {
    event.preventDefault();
    const input = document.querySelector(".chatbot-input").value.trim();
    lichResponse(input);
  });

const mutateFlavor = (flavor) => {
  const flavorElement = document.querySelector(".chatbot-flavor");
  flavorElement.textContent = flavor;
};

const mutateLastMessage = (message) => {
  const lastMessageElement = document.querySelector(".chatbot-last-message");
  lastMessageElement.style.visibility = "visible";
  lastMessageElement.textContent = message;
};

const concatLichResponse = (lichText) => {
  const lichElement = document.querySelector(".chatbot-response");
  lichElement.style.visibility = "visible";
  lichElement.textContent = lichElement.textContent + lichText;
};

const clearLichResponse = () => {
  const lichElement = document.querySelector(".chatbot-response");
  lichElement.style.visibility = "hidden";
  lichElement.textContent = "";
};

const fetchLich = async (message) => {
  try {
    loading = true;
    const response = await fetch("/lich", {
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
      concatLichResponse(value);
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

const lichResponse = (message) => {
  if (message === "") {
    mutateFlavor("I can't say anything if you don't.");
  } else {
    if (loading) {
      mutateFlavor("Slow down... I can only answer one question at a time.");
    } else {
      clearLichResponse();
      mutateFlavor("Let me think about that...");
      mutateLastMessage(message);
      fetchLich(message);
    }
  }
};
