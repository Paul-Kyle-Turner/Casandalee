
export default function HeaderComponent() {
    const headerElement = document.createElement('div')
    headerElement.id = "header"

    // Giggle
    const giggleElement = document.createElement('img')
    giggleElement.className = "giggle"
    giggleElement.src = "/static/img/logoo.png"
    headerElement.appendChild(giggleElement)

    //sign out
    const signOutElement = document.createElement('button')
    signOutElement.hidden = "true"
    signOutElement.id = "sign-out"
    signOutElement.textContent = "Sign Out"
    headerElement.appendChild(signOutElement)

    //login title
    const loginTitleElement = document.createElement('h1')
    loginTitleElement.id = "login-title"
    loginTitleElement.textContent = "Casandalee : Ai for PF2E"
    headerElement.appendChild(loginTitleElement)

    return headerElement
}
