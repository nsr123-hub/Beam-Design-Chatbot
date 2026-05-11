function clearChat() {

    document.getElementById("messages").innerHTML = `
        <div class="message ai">
            Hello! I'm your AI Structural Engineering Assistant. Describe your RCC beam design requirements, and I'll analyze it for you. For example: "Design a 6m span beam with 25 kN/m load, M25 concrete, and Fe415 steel."
        </div>
    `;
    document.getElementById("message").value = "";

    // Reset report tables
    document.getElementById("inputL").textContent = "-";
    document.getElementById("inputW").textContent = "-";
    document.getElementById("inputFck").textContent = "-";
    document.getElementById("inputFy").textContent = "-";
    document.getElementById("inputB").textContent = "-";
    document.getElementById("inputD").textContent = "-";
    document.getElementById("designStatus").textContent = "-";
    document.getElementById("shearStatus").textContent = "-";
    document.getElementById("ultimateMoment").textContent = "-";
    document.getElementById("limitingMoment").textContent = "-";
}

async function sendMessage() {

    const messageInput = document.getElementById("message");
    const message = messageInput.value.trim();

    if(message === "") return;

    // Add user message
    const messages = document.getElementById("messages");
    messages.innerHTML += `<div class="message user">${message}</div>`;
    messageInput.value = "";

    // Scroll to bottom
    messages.scrollTop = messages.scrollHeight;

    try{

        const response = await fetch("/chat",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                message:message
            })
        });

        const data = await response.json();

        let aiMessage = "";

        if(data.success){

            // Update input table
            document.getElementById("inputL").textContent = data.input_data.L + " m";
            document.getElementById("inputW").textContent = data.input_data.w + " kN/m";
            document.getElementById("inputFck").textContent = data.input_data.fck + " MPa";
            document.getElementById("inputFy").textContent = data.input_data.fy + " MPa";
            document.getElementById("inputB").textContent = data.input_data.b + " mm";
            document.getElementById("inputD").textContent = data.input_data.d + " mm";

            // Update verdict table
            document.getElementById("designStatus").textContent = data.technical_result.design_status;
            document.getElementById("shearStatus").textContent = data.technical_result.shear_status;
            document.getElementById("ultimateMoment").textContent = data.technical_result.ultimate_moment_kNm + " kN·m";
            document.getElementById("limitingMoment").textContent = data.technical_result.limiting_moment_kNm + " kN·m";

            // AI message with analysis only
            aiMessage = data.ai_response;

        } else {

            aiMessage = data.response;

        }

        messages.innerHTML += `<div class="message ai">${aiMessage}</div>`;

        // Scroll to bottom
        messages.scrollTop = messages.scrollHeight;

    } catch(error){

        messages.innerHTML += `<div class="message ai">Server Error. Please try again.</div>`;
        messages.scrollTop = messages.scrollHeight;
    }
}

document.getElementById("message").addEventListener("keydown", function(e){

    if(e.key === "Enter" && !e.shiftKey){

        e.preventDefault();
        sendMessage();
    }
});