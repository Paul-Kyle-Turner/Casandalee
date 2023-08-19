
const anchorNames = {
    "/": "Casandalee : Rules",
    "backgrounds": "Backstories",
    "about": "About"
}

function TopNavComponent(activeRef) {
    const topNavElement = document.createElement('div')
    topNavElement.className = "topnav"

    for (let [anchorRef, anchorName] of Object.entries(anchorNames)) {
        const anchor = document.createElement('a')
        anchor.href = anchorRef
        anchor.textContent = anchorName

        if (activeRef === anchorRef) {
            anchor.className = "active"
        }
        topNavElement.appendChild(anchor)
    }
    return topNavElement
}

export default TopNavComponent