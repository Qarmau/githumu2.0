/*document.addEventListener('DOMContentLoaded', function() {
    // Background image rotation
    const backgroundImages = document.querySelectorAll('.background-image');
    let currentIndex = 0;

    function rotateBackground() {
        backgroundImages[currentIndex].style.opacity = 0;
        currentIndex = (currentIndex + 1) % backgroundImages.length;
        backgroundImages[currentIndex].style.opacity = 1;
    }

    setInterval(rotateBackground, 10000);

    // Add more interactive features here
});*/
document.addEventListener('DOMContentLoaded', function() {
    const backgroundImages = document.querySelectorAll('.background-image');
    let currentIndex = 0;

    function rotateBackground() {
        backgroundImages[currentIndex].style.opacity = '0';
        currentIndex = (currentIndex + 1) % backgroundImages.length;
        backgroundImages[currentIndex].style.opacity = '1';
    }

    // Only start the rotation if there's more than one image
    if (backgroundImages.length > 1) {
        setInterval(rotateBackground, 10000); // Change image every 10 seconds
    }
});




// Calendar functionality
if (document.getElementById('calendar-container')) {
    const calendarEl = document.getElementById('calendar-container');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        events: '/api/calendar-events/',
        height: 'auto'
    });
    calendar.render();
}

// University admission rate graph
if (document.getElementById('admission-rate-graph')) {
    const ctx = document.getElementById('admission-rate-graph').getContext('2d');
    fetch('/api/admission-rates/')
        .then(response => response.json())
        .then(data => {
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.map(item => item.year),
                    datasets: [{
                        label: 'University Admission Rate',
                        data: data.map(item => item.rate),
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        });
}
document.addEventListener('DOMContentLoaded', function() {
    const eagle = document.querySelector('.eagle-icon');
    let isUp = false;

    function soar() {
        if (isUp) {
            eagle.style.transform = 'translateY(0)';
        } else {
            eagle.style.transform = 'translateY(-20px)';
        }
        isUp = !isUp;
        setTimeout(soar, 2000);
    }

    soar();
});
document.addEventListener('DOMContentLoaded', function() {
    // Add any interactive functionality here
    const deleteLinks = document.querySelectorAll('.delete-link');
    deleteLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            if (confirm('Are you sure you want to delete this assignment?')) {
                window.location.href = this.getAttribute('href');
            }
        });

    });
});