(async function () {
  fetch("/api/invoice/status_amount")
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      new Chart(document.getElementById("invoice_status_amount"), {
        type: "bar",
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
              text: "Invoice Status by Amount",
            },
          },
        },
      });
    })
    .catch((error) => console.error("Error fetching chart data:", error));
})();
