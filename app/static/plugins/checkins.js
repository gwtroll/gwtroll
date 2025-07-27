(async function () {
  fetch("/api/checkins")
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      new Chart(document.getElementById("checkins"), {
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
              text: "Checkins",
            },
          },
        },
      });
    })
    .catch((error) => console.error("Error fetching chart data:", error));
})();
