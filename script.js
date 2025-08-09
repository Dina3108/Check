function fetchLeetCodeData() {
  const username = document.getElementById("username").value.trim();
  if (!username) {
    alert("Please enter a username");
    return;
  }

  document.getElementById("loading").style.display = "flex";
  document.getElementById("stats").style.display = "none";
  document.getElementById("problems-container").style.display = "none";

  fetch(`http://leetcode-backend.onrender.com/leetcode?username=${username}`)
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("loading").style.display = "none";

      if (data.error) {
        document.getElementById("stats").innerHTML = `<p>${data.error}</p>`;
        document.getElementById("stats").style.display = "block";
        return;
      }

      // Display stats
      document.getElementById("stats").innerHTML = `
        <strong>Username:</strong> ${data.username}<br>
        <strong>Total Unique Solved:</strong> ${data.total_unique_solved}<br>
        <strong>Easy:</strong> ${data.easy} | 
        <strong>Medium:</strong> ${data.medium} | 
        <strong>Hard:</strong> ${data.hard}<br>
        <strong>Total Score:</strong> ${data.total_score}
      `;
      document.getElementById("stats").style.display = "block";

      // Populate table
      const tableBody = document.getElementById("problems-table");
      tableBody.innerHTML = "";
      data.problems.forEach((p) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${p.title}</td>
          <td>${p.difficulty}</td>
          <td>${p.language}</td>
          <td>${p.time}</td>
          <td>${p.points}</td>
        `;
        tableBody.appendChild(row);
      });
      document.getElementById("problems-container").style.display = "block";
    })
    .catch(() => {
      document.getElementById("loading").style.display = "none";
      document.getElementById("stats").innerHTML =
        "<p>Failed to connect to backend. Is it running?</p>";
      document.getElementById("stats").style.display = "block";
    });
}
