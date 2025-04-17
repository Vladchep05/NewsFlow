const randomParticleCount = Math.floor(Math.random() * (200 - 80 + 1)) + 80; // Случайное число от 80 до 200

particlesJS("particles-js", {
            "particles": {
                "number": {
                    "value": randomParticleCount,
                    "density": {
                        "enable": true,
                        "value_area": 800
                    }
                },
                "color": {
                    "value": "#00ffe0"
                },
                "shape": {
                    "type": "circle"
                },
                "opacity": {
                    "value": 0.4,
                    "random": true
                },
                "size": {
                    "value": 3,
                    "random": true
                },
                "line_linked": {
                    "enable": true,
                    "distance": 150,
                    "color": "#00ffe0",
                    "opacity": 0.3,
                    "width": 1
                },
                "move": {
                    "enable": true,
                    "speed": 1,
                    "random": true,
                    "out_mode": "out"
                }
            },
            "interactivity": {
                "events": {
                    "onhover": {
                        "enable": true,
                        "mode": "grab"
                    },
                    "onclick": {
                        "enable": true,
                        "mode": "repulse"
                    }
                }
            },
            "retina_detect": true
        });