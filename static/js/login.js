"use strict";

function getCookie(cookieName) {
  var name = cookieName + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var cookieArray = decodedCookie.split(";");
  var cookie = cookieArray.find(function (cookie) {
    return cookie.trim().indexOf(name) === 0;
  });
  if (cookie) {
    return cookie.substring(name.length, cookie.length);
  }
  return "";
}

const firebaseConfig = {
  apiKey: "AIzaSyBl9URYKZ6_ZLHcgJdoeVPn9SNG_MBRHQ4",
  authDomain: "dnd-lawyer.firebaseapp.com",
  projectId: "dnd-lawyer",
  storageBucket: "dnd-lawyer.appspot.com",
  messagingSenderId: "964197045808",
  appId: "1:964197045808:web:8ab46a733b0f562d6abff5",
  measurementId: "G-7YGVT0YNBD",
};
firebase.initializeApp(firebaseConfig);

window.addEventListener("load", function () {
  document.getElementById("sign-out").onclick = function () {
    firebase.auth().signOut();
    document
      .querySelector("#firebaseui-auth-container")
      .removeAttribute("hidden");
  };

  var uiConfig = {
    signInSuccessUrl: "/",
    signInOptions: [
      firebase.auth.GoogleAuthProvider.PROVIDER_ID,
      firebase.auth.EmailAuthProvider.PROVIDER_ID,
    ],
    tosUrl: "<your-tos-url>",
  };

  firebase.auth().onAuthStateChanged(
    function (user) {
      if (user) {
        document.getElementById("sign-out").hidden = false;
        console.log(`Signed in as ${user.displayName} (${user.email})`);
        user.getIdToken().then(function (token) {
          document.cookie = "token=" + token;
          document.getElementById("firebaseui-auth-container").hidden = true;
        });
      } else {
        var ui = new firebaseui.auth.AuthUI(firebase.auth());
        ui.start("#firebaseui-auth-container", uiConfig);
        document.getElementById("sign-out").hidden = true;
        document.cookie = "token=";
      }
    },
    function (error) {
      console.log(error);
      alert("Unable to log in: " + error);
    }
  );
});
