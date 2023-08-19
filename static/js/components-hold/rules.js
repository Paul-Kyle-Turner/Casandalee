

export default function ChatbotRulesContainerComponent() {
    const chatbotContainerElement = document.createElement('div')
    chatbotContainerElement.className = "chatbot-container"

    const chatbotMessagesContainerElement = document.createElement('div')
    chatbotMessagesContainerElement.className = "chatbot-messages-container"
    chatbotContainerElement.appendChild(chatbotMessagesContainerElement)

    const chatbotFlavorElement = document.createElement('div')
    chatbotFlavorElement.className = "chatbot-flavor"
    chatbotFlavorElement.textContent = "I am Casandalee. What ruling shall I offer you?"
    chatbotMessagesContainerElement.appendChild(chatbotFlavorElement)

    const chatbotLastMessageElement = document.createElement('div')
    chatbotLastMessageElement.className = "chatbot-last-message"
    chatbotMessagesContainerElement.appendChild(chatbotLastMessageElement)

    const chatbotResponseElement = document.createElement('div')
    chatbotResponseElement.className = "chatbot-response"
    chatbotMessagesContainerElement.appendChild(chatbotResponseElement)

    const chatbotContentResponseElement = document.createElement('div')
    chatbotContentResponseElement.className = "chatbot-content-response"
    chatbotMessagesContainerElement.appendChild(chatbotContentResponseElement)

    return chatbotContainerElement
}

export default function ChatbotRulesFormComponent() {
    const chatbotForm = document.createElement('form')
    chatbotForm.className = "chatbot-form"

    const chatbotInput = document.createElement('input')
    chatbotInput.className = "chatbot-input"
    chatbotInput.placeholder = "Type your message..."
    chatbotForm.appendChild(chatbotInput)

    const chatbotButtonSubmit = document.createElement('button')
    chatbotButtonSubmit.className = "chatbot-submit-btn"
    chatbotButtonSubmit.type = "submit"
    chatbotButtonSubmit.textContent = "Send"
    chatbotForm.appendChild(chatbotButtonSubmit)

    return chatbotForm
}