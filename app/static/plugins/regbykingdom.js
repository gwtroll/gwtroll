(async function () {
  fetch("/api/registrations/bykingdom")
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      new Chart(document.getElementById("registrations_bykingdom"), {
        type: "pie",
        data: data,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "top",
            },
            title: {
              display: true,
              text: "Reg by Kingdom",
            },
          },
        },
      });
    })
    .catch((error) => console.error("Error fetching chart data:", error));
})();
