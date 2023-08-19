import HeaderComponent from "./header.js";
import TopNavComponent from "./topnav.js";
import FirebaseComponent from "./firebase.js";

const buildHeader = (activeRef) => {
  try {
    const rootElement = document.querySelector("#root");

    //topnav
    const topnav = TopNavComponent(activeRef);
    rootElement.prepend(topnav);
  
    //header
    const headerElement = HeaderComponent();
    rootElement.prepend(headerElement);
  
    //firebase
    const firebase = FirebaseComponent();
    rootElement.appendChild(firebase);
  } catch (error) {
    const rootElement = document.querySelector("#main-vertical");

    //topnav
    const topnav = TopNavComponent(activeRef);
    rootElement.prepend(topnav);
  
    //header
    const headerElement = HeaderComponent();
    rootElement.prepend(headerElement);
  }

};

export default buildHeader;
