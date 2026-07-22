const ctx = document.getElementById('salesChart');

new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
            label: 'Monthly Sales',
            data: [12, 19, 10, 25, 18, 30],
            borderWidth: 2
        }]
    },
    options: {
        responsive: true
    }
});