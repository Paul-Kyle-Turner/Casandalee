/**
 * Copyright 2018, Google LLC
 * Licensed under the Apache License, Version 2.0 (the `License`);
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an `AS IS` BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

"use strict";

window.addEventListener("load", function () {
  // [START gae_python38_auth_signout]
  // [START gae_python3_auth_signout]
  document.getElementById("sign-out").onclick = function () {
    firebase.auth().signOut();
  };
  // [END gae_python3_auth_signout]
  // [END gae_python38_auth_signout]

  // [START gae_python38_auth_UIconfig_variable]
  // [START gae_python3_auth_UIconfig_variable]
  // FirebaseUI config.
  var uiConfig = {
    signInSuccessUrl: "/",
    signInOptions: [
      // Remove any lines corresponding to providers you did not check in
      // the Firebase console.
      firebase.auth.GoogleAuthProvider.PROVIDER_ID,
      firebase.auth.EmailAuthProvider.PROVIDER_ID,
    ],
    // Terms of service url.
    tosUrl: "<your-tos-url>",
  };
  // [END gae_python3_auth_UIconfig_variable]
  // [END gae_python38_auth_UIconfig_variable]

  // [START gae_python38_auth_request]
  // [START gae_python3_auth_request]
  firebase.auth().onAuthStateChanged(
    function (user) {
      if (user) {
        // User is signed in, so display the "sign out" button and login info.
        document.getElementById("sign-out").hidden = false;
        console.log(`Signed in as ${user.displayName} (${user.email})`);
        user.getIdToken().then(function (token) {
          // Add the token to the browser's cookies. The server will then be
          // able to verify the token against the API.
          // SECURITY NOTE: As cookies can easily be modified, only put the
          // token (which is verified server-side) in a cookie; do not add other
          // user information.
          document.cookie = "token=" + token;
        });
      } else {
        // User is signed out.
        // Initialize the FirebaseUI Widget using Firebase.
        var ui = new firebaseui.auth.AuthUI(firebase.auth());
        // Show the Firebase login button.
        ui.start("#firebaseui-auth-container", uiConfig);
        // Update the login state indicators.
        document.getElementById("sign-out").hidden = true;
        // Clear the token cookie.
        document.cookie = "token=";
      }
    },
    function (error) {
      console.log(error);
      alert("Unable to log in: " + error);
    }
  );
  // [END gae_python3_auth_request]
  // [END gae_python38_auth_request]
});

const form = document.querySelector(".chatbot-form");
const input = document.querySelector(".chatbot-input");
let index = 0;
let messages = [];

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    // Check if the Enter key was pressed
    event.preventDefault(); // Prevent the default Enter key behavior (i.e. adding a newline)
    const message = input.value.trim(); // Get the user's input and trim whitespace
    if (message !== "") {
      // Check if the message is not empty
      addMessage(message, "user"); // Add the user's message to the chat
      input.value = ""; // Clear the input field
      postMessageToLLM(message); // Send the user's message to the chatbot API
    }
  }
});

form.addEventListener("submit", (event) => {
  event.preventDefault(); // Prevent the default form submission
  const message = input.value.trim(); // Get the user's input and trim whitespace
  if (message !== "") {
    // Check if the message is not empty
    addMessage(message, "user"); // Add the user's message to the chat
    input.value = ""; // Clear the input field
    postMessageToLLM(message); // Send the user's message to the chatbot API
  }
});

// Create a message and send it back to the server
// Create a message and send it back to the server
async function postMessageToLLM(message) {
  try {
    const response = await fetch("/lich", {
      method: "POST",
      body: JSON.stringify({
        message: message,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const isJson = response.headers.get('content-type')?.includes('application/json');
      const reader = response.body
      .pipeThrough(new TextDecoderStream())
      .getReader();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        addMessage(value, "lich");
        console.log("Received", value);
      }

      console.log("Response fully received");
  } catch (error) {
    addMessage(
      "Something went wrong handeling the request on the front-end.  Try again.",
      "lich"
    );
    console.error("Error:", error);
  }
  index = index + 1;
}

function addMessage(message, sender) {
  const messagesContainer = document.querySelector(
    ".chatbot-messages-container"
  );
  const messageBox = document.querySelector(
    ".chatbot-message.lich.id" + String(index)
  );

  if (messageBox === null || sender === "user") {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("chatbot-message", sender, "id" + String(index));
    messageDiv.innerText =
      String(sender.charAt(0).toUpperCase()) +
      String(sender.substring(1)) +
      " : " +
      message;
    messagesContainer.appendChild(messageDiv);
  } else {
    messageBox.innerText += message;
  }
}