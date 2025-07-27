(async function () {
  fetch("/api/preregistrations")
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      new Chart(document.getElementById("preregistrations"), {
        type: "line",
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
              text: "PreReg by Date",
            },
          },
        },
      });
    })
    .catch((error) => console.error("Error fetching chart data:", error));
})();
