function generate() {
    const names = document.getElementById("names").value.split("\n").filter(n => n.trim() !== "");
    const startDate = document.getElementById("start-date").value;
    const endDate = document.getElementById("end-date").value;

    fetch("http://127.0.0.1:5000/generate", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            names: names,
            start_date: startDate,
            end_date: endDate
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("output").innerText = JSON.stringify(data, null, 2);
    });
}
