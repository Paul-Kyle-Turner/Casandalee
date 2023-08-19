
export default function ChatbotBackstoriesContainerComponent() {
    const chatbotContainerElement = document.createElement('div')
    chatbotContainerElement.className = "chatbot-container"

    const chatbotMessagesContainerElement = document.createElement('div')
    chatbotMessagesContainerElement.className = "chatbot-messages-container"
    chatbotContainerElement.appendChild(chatbotMessagesContainerElement)
    
    const chatbotFlavorElement = document.createElement('div')
    chatbotFlavorElement.className = "chatbot-flavor"
    chatbotFlavorElement.textContent = "I am Casandalee. Tell me about the town and your character. I will spin you a tail about their backstory."
    chatbotMessagesContainerElement.appendChild(chatbotFlavorElement)

    const chatbotGMFlavorElement = document.createElement('div')
    chatbotGMFlavorElement.id = "gm-flavor"
    chatbotGMFlavorElement.className = "chatbot-flavor-gm"
    chatbotGMFlavorElement.textContent = "I am Casandalee. Tell me about the town and your character. I will spin you a tail about their backstory."
    chatbotMessagesContainerElement.appendChild(chatbotGMFlavorElement)

    const chatbotGMInputElement = document.createElement('div')
    chatbotGMFlavorElement.id = "import"
    chatbotGMFlavorElement.className = "chatbot-flavor-gm"
    chatbotGMFlavorElement.textContent = "I am Casandalee. Tell me about the town and your character. I will spin you a tail about their backstory."
    chatbotMessagesContainerElement.appendChild(chatbotGMFlavorElement)
}

<div class="chatbot-container">
          <div class="chatbot-messages-container">
            <div id="gm-flavor" class="chatbot-flavor-gm">
              <div id="import"> 
                <button id="import-button">Import GM scene</button>
                <input placeholder="Type your message..." />
              </div>
              <p>Tell me about your scene and setting. (GM should provide this.)</p>
              <div id="export">
                <button id="export-button">Export GM scene</button>
                <p id="export-hash"></p>
              </div>
            </div>
            <textarea id="gm-input" class="chatbot-textarea-input"></textarea>
            <div id="user-flavor" class="chatbot-flavor">
              Tell me about the character that you want to create.
            </div>
            <textarea id="input" class="chatbot-textarea-input"></textarea>
            <button type="submit" class="chatbot-submit-btn">Send</button>
            <div class="chatbot-response"></div>
            <div class="chatbot-content-response"></div>
          </div>
        </div>