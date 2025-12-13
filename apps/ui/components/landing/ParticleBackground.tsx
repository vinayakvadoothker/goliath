"use client";

import { useEffect, useRef } from "react";

declare global {
    interface Window {
        particlesJS: (id: string, config: any) => void;
        pJSDom: Array<{ pJS: any }>;
    }
}

export default function ParticleBackground() {
    const containerRef = useRef<HTMLDivElement>(null);
    const particlesLoaded = useRef(false);

    useEffect(() => {
        if (particlesLoaded.current || !containerRef.current) return;

        // Load particles.js from CDN
        const script = document.createElement("script");
        script.src = "http://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js";
        script.async = true;

        script.onload = () => {
            if (window.particlesJS && containerRef.current) {
                window.particlesJS("particles-js", {
                    "particles": {
                        "number": {
                            "value": 80,
                            "density": {
                                "enable": true,
                                "value_area": 800
                            }
                        },
                        "color": {
                            "value": "#ffffff"
                        },
                        "shape": {
                            "type": "circle",
                            "stroke": {
                                "width": 0,
                                "color": "#000000"
                            },
                            "polygon": {
                                "nb_sides": 5
                            }
                        },
                        "opacity": {
                            "value": 0.5,
                            "random": false,
                            "anim": {
                                "enable": false,
                                "speed": 1,
                                "opacity_min": 0.1,
                                "sync": false
                            }
                        },
                        "size": {
                            "value": 3,
                            "random": true,
                            "anim": {
                                "enable": false,
                                "speed": 40,
                                "size_min": 0.1,
                                "sync": false
                            }
                        },
                        "line_linked": {
                            "enable": true,
                            "distance": 150,
                            "color": "#ffffff",
                            "opacity": 0.4,
                            "width": 1
                        },
                        "move": {
                            "enable": true,
                            "speed": 6,
                            "direction": "none",
                            "random": false,
                            "straight": false,
                            "out_mode": "out",
                            "bounce": false,
                            "attract": {
                                "enable": false,
                                "rotateX": 600,
                                "rotateY": 1200
                            }
                        }
                    },
                    "interactivity": {
                        "detect_on": "canvas",
                        "events": {
                            "onhover": {
                                "enable": true,
                                "mode": "repulse"
                            },
                            "onclick": {
                                "enable": true,
                                "mode": "push"
                            },
                            "resize": true
                        },
                        "modes": {
                            "grab": {
                                "distance": 400,
                                "line_linked": {
                                    "opacity": 1
                                }
                            },
                            "bubble": {
                                "distance": 400,
                                "size": 40,
                                "duration": 2,
                                "opacity": 8,
                                "speed": 3
                            },
                            "repulse": {
                                "distance": 200,
                                "duration": 0.4
                            },
                            "push": {
                                "particles_nb": 4
                            },
                            "remove": {
                                "particles_nb": 2
                            }
                        }
                    },
                    "retina_detect": true
                });
                particlesLoaded.current = true;
                console.log("Particles.js initialized successfully");
                
                // Ensure the canvas can receive mouse events
                setTimeout(() => {
                    const canvas = containerRef.current?.querySelector('canvas');
                    if (canvas) {
                        canvas.style.pointerEvents = 'auto';
                        console.log("Canvas pointer events enabled");
                    }
                }, 200);
            }
        };

        document.head.appendChild(script);

        return () => {
            // Cleanup: remove script if component unmounts
            if (document.head.contains(script)) {
                document.head.removeChild(script);
            }
        };
    }, []);

    return (
        <div
            id="particles-js"
            ref={containerRef}
            className="absolute inset-0 w-full h-full z-0 pointer-events-auto"
            style={{
                backgroundColor: "#000000",
                backgroundImage: "url('')",
                backgroundRepeat: "no-repeat",
                backgroundSize: "cover",
                backgroundPosition: "50% 50%"
            }}
        />
    );
}
