function cardClicked(cardNumber) {
    alert('Card ' + cardNumber + ' clicked!');
  }

function logout() {
  alert('Logout successful!');
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".btn-details").forEach(button => {
      button.addEventListener("click", async (event) => {
          const vmName = event.target.dataset.vm;
          const action = event.target.dataset.action;
          const rgName = event.target.dataset.rg;

          try {
              const response = await fetch(`/api/vm/${rgName}/${vmName}/${action}`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
              });

              if (response.ok) {
                  const data = await response.json();

                  // Update status and button dynamically
                  document.getElementById(`status-${vmName}`).innerText = data.status;
                  event.target.innerText = data.next_action_text;
                  event.target.dataset.action = data.next_action; // Update button action
              } else {
                  const error = await response.json();
                  alert(`Error: ${error.message}`);
              }
          } catch (error) {
              console.error("Error:", error);
              alert("An error occurred. Please try again.");
          }
      });
  });
});